"""Docker デーモンとネットワークを使わないオフラインテスト。"""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]


class ComposeStructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text())

    def test_services_and_livebook_profile(self):
        services = self.compose["services"]
        self.assertEqual(set(services), {"web", "db", "livebook"})
        self.assertEqual(services["livebook"]["profiles"], ["livebook"])
        self.assertNotIn("version", self.compose)
        self.assertNotIn("links", services["web"])

    def test_database_health_and_service_readiness(self):
        services = self.compose["services"]
        self.assertEqual(services["web"]["depends_on"]["db"]["condition"], "service_healthy")
        self.assertIn("pg_isready", " ".join(services["db"]["healthcheck"]["test"]))
        self.assertNotIn("ports", services["db"], "Do not expose Postgres to host by default")

    def test_nonroot_build_and_cached_mix(self):
        dockerfile = (ROOT / "Dockerfile").read_text()
        self.assertIn("USER developer", dockerfile)
        self.assertIn("MIX_DEPS_PATH=/cache/deps", dockerfile)
        self.assertIn("MIX_BUILD_ROOT=/cache/_build", dockerfile)
        web = self.compose["services"]["web"]
        self.assertIn("mix_deps:/cache/deps", web["volumes"])
        self.assertIn("mix_build:/cache/_build", web["volumes"])
        self.assertTrue(any(v == ".:/workspace" for v in web["volumes"]))

    def test_local_bindings_and_livebook_auth_defaults(self):
        services = self.compose["services"]
        for name in ("web", "livebook"):
            for port in services[name]["ports"]:
                self.assertTrue(port.startswith("127.0.0.1:"), (name, port))
        env = services["livebook"]["environment"]
        self.assertNotIn("LIVEBOOK_TOKEN_ENABLED", env)
        self.assertNotIn("LIVEBOOK_PASSWORD", env)
        self.assertIn("attached:phoenix@web.phoenix.test", env["LIVEBOOK_DEFAULT_RUNTIME"])
        self.assertIn("web.phoenix.test", services["web"]["networks"]["default"]["aliases"])


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        self.root.mkdir()
        (self.root / "bin").mkdir()
        for filename in ("bin/new", "bin/setup", ".env.example"):
            dest = self.root / filename
            shutil.copy2(ROOT / filename, dest)
        self.bin = Path(self.temp.name) / "fake_bin"
        self.bin.mkdir()
        self.log = Path(self.temp.name) / "docker.log"
        docker = self.bin / "docker"
        docker.write_text(
            "#!/bin/sh\n"
            "printf '%s\\n' \"$*\" >> \"$DOCKER_LOG\"\n"
            "case \" $* \" in\n"
            "  *' mix phx.new app '*)\n"
            "    mkdir -p app/config\n"
            "    printf '%s\\n' 'import Config' > app/config/dev.exs\n"
            "    printf '%s\\n' 'import Config' > app/config/test.exs\n"
            "    ;;\n"
            "esac\n"
        )
        docker.chmod(0o755)
        identity = self.bin / "id"
        identity.write_text(
            "#!/bin/sh\n"
            "case \"$1\" in -u) echo 1001 ;; -g) echo 1002 ;; *) exit 2 ;; esac\n"
        )
        identity.chmod(0o755)
        self.env = os.environ.copy()
        self.env["PATH"] = f"{self.bin}:{self.env['PATH']}"
        self.env["DOCKER_LOG"] = str(self.log)

    def call(self, script, *args):
        return subprocess.run(
            [str(self.root / "bin" / script), *args],
            cwd=self.root,
            env=self.env,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_setup_creates_local_secrets_with_user_ids_without_overwrite(self):
        first = self.call("setup")
        self.assertEqual(first.returncode, 0, first.stderr)
        contents = (self.root / ".env").read_text()
        self.assertIn("APP_UID=1001", contents)
        self.assertIn("APP_GID=1002", contents)
        self.assertNotIn("replace_with_random_local_password", contents)
        self.assertNotIn("replace_with_random_local_cookie", contents)
        self.assertEqual((self.root / ".env").stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.call("setup").returncode, 0)
        self.assertEqual((self.root / ".env").read_text(), contents)

    def test_generator_creates_app_and_docker_overrides(self):
        result = self.call("new", "hello_phoenix")
        self.assertEqual(result.returncode, 0, result.stderr)
        config = self.root / "app" / "config"
        self.assertIn('import_config "docker.exs"', (config / "dev.exs").read_text())
        self.assertIn('import_config "docker_test.exs"', (config / "test.exs").read_text())
        self.assertIn("config :hello_phoenix, HelloPhoenix.Repo", (config / "docker.exs").read_text())
        self.assertIn("HelloPhoenixWeb.Endpoint", (config / "docker.exs").read_text())
        self.assertEqual(os.readlink(self.root / "app/deps"), "/cache/deps")
        self.assertEqual(os.readlink(self.root / "app/_build"), "/cache/_build")
        calls = self.log.read_text()
        self.assertIn("compose build web", calls)
        self.assertIn("--no-deps --workdir /workspace web mix phx.new app --app hello_phoenix --module HelloPhoenix --no-install", calls)
        self.assertIn("compose run --rm web mix setup", calls)

    def test_generator_rejects_existing_app_before_docker_calls(self):
        (self.root / "app").mkdir()
        result = self.call("new", "hello_phoenix")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.log.exists())

    def test_generator_rejects_unsafe_app_names(self):
        for name in ("BadName", "foo-bar", "../foo", "foo__bar", "9wrong", "a_", "foo;rm"):
            with self.subTest(name=name):
                result = self.call("new", name)
                self.assertEqual(result.returncode, 2, result.stderr)
        self.assertFalse(self.log.exists())


if __name__ == "__main__":
    unittest.main()
