"""起動済みの Livebook と生成した smoke_app の統合テスト。

Python 標準ライブラリのみを使います。オフラインテストには含めず、個別に実行します。
"""

from http.cookiejar import CookieJar
import json
from pathlib import Path
import re
import subprocess
import time
from urllib.parse import urlencode, urlsplit
from urllib.request import build_opener, HTTPCookieProcessor

ROOT = Path(__file__).resolve().parents[1]


def compose(*args, **kwargs):
    return subprocess.run(
        ["docker", "compose", *args], cwd=ROOT, check=True, text=True, **kwargs
    )


def fetch(opener, url):
    with opener.open(url, timeout=5) as response:
        return urlsplit(response.url).path, response.read().decode()


def main():
    # 展開された認証情報を表示せず、設定からホスト側のポートを読み取ります。
    config = json.loads(
        compose("--profile", "livebook", "config", "--format", "json", capture_output=True).stdout
    )
    port = next(
        item["published"]
        for item in config["services"]["livebook"]["ports"]
        if item["target"] == 8080
    )
    base = f"http://127.0.0.1:{port}"
    guest = build_opener(HTTPCookieProcessor(CookieJar()))
    for attempt in range(40):
        try:
            path, _ = fetch(guest, base + "/")
            break
        except OSError:
            if attempt == 39:
                raise
            time.sleep(3)
    assert path == "/authenticate", "Unauthenticated access must require login"
    path, _ = fetch(guest, base + "/?token=invalid-smoke-token")
    assert path == "/authenticate", "An invalid token must not authenticate"

    logs = compose("logs", "--no-color", "livebook", capture_output=True).stdout
    tokens = re.findall(r"[?&]token=([A-Za-z0-9_-]+)", logs)
    assert tokens, "Livebook did not log a login token"
    authenticated = build_opener(HTTPCookieProcessor(CookieJar()))
    path, body = fetch(authenticated, base + "/?" + urlencode({"token": tokens[-1]}))
    assert path == "/" and "Livebook" in body, "Token login failed"
    path, _ = fetch(authenticated, base + "/")
    assert path == "/", "Login session was not retained"
    print("Livebook rejects guests/invalid tokens and accepts its generated token", flush=True)

    compose(
        "exec", "-T", "livebook", "elixir", "-pa", "/app/lib/*/ebin",
        "-e", "Code.eval_string(IO.read(:stdio, :eof))",
        input=(ROOT / "tests/livebook_runtime.exs").read_text(), timeout=90,
    )


if __name__ == "__main__":
    main()
