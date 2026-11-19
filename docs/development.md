# 開発手順

## 実行環境

Docker Compose v2 以降と POSIX シェルを使います。`awk`、`grep`、`id`、`od`、`tr` が必要です。
これらは通常、macOS、Linux、WSL2 に含まれます。

| ホスト | 利用方針 |
| --- | --- |
| macOS Intel / Apple Silicon | Docker Desktop を使い、ターミナルから実行します。 |
| Linux x86_64 / ARM64 | Docker Engine と Compose を使います。`bin/setup` がホストの UID/GID（ユーザー・グループ ID）を設定します。通常のユーザーで実行してください。 |
| Windows + WSL2 | WSL2 の Linux シェルで実行します。標準の WSL2 バックエンドでは、ソースを `/mnt/c/...` より `/home/<user>/...` に置くことを推奨します。 |

対象環境と動作確認済みの環境は異なります。[検証記録](worklog/20261119-development-smoke-test.md)を参照してください。
Docker Desktop の設定に応じた要件は [WSL2 の公式資料](https://docs.docker.com/desktop/features/wsl/best-practices/)で確認してください。

## ファイルと設定

| パス | 用途 |
| --- | --- |
| `Dockerfile` | Debian ベース、非 root ユーザーの開発イメージ |
| `docker-compose.yml` | Phoenix、PostgreSQL、任意の Livebook |
| `.env.example` | ローカル設定のひな形 |
| `bin/setup` | `.env` に UID/GID とランダムなローカル認証情報を作成 |
| `bin/new` | `app/` にアプリを生成し、開発・テスト用の設定とキャッシュへのリンクを追加 |
| `app/` | アプリのソース。必要に応じて独立した Git リポジトリで管理 |
| `tests/` | スターター自体のテスト |

設定の初期値は [.env.example](../.env.example) と [Compose 構成](../docker-compose.yml)を参照してください。
ポートや UID/GID、ローカル認証情報は `.env` で変更します。イメージ内の設定を変えた場合は再ビルドが必要です。
Livebook の接続先と Livebook 自体の Elixir マイナーバージョンはそろえてください。

アプリのソースはバインドマウントで共有し、依存関係とビルド成果物は名前付きボリュームに保存します。
`app/deps` と `app/_build` はコンテナ内のキャッシュへのシンボリックリンクです。
リンク先はホストには存在しないため、ホスト上ではリンク切れに見える場合があります。

## 日常のコマンド

すべてリポジトリのルートで実行します。

| 操作 | コマンド |
| --- | --- |
| 起動 | `docker compose up -d web` |
| ログ | `docker compose logs -f web` |
| 停止（データ保持） | `docker compose down` |
| シェル | `docker compose exec web sh` |
| 別コンテナで IEx を起動 | `docker compose run --rm web iex -S mix` |
| マイグレーション | `docker compose run --rm web mix ecto.migrate` |
| アプリのテスト | `docker compose run --rm -e MIX_ENV=test web mix test` |
| PostgreSQL に接続 | `docker compose exec db psql -U postgres` |
| 再ビルドして起動 | `docker compose up -d --build web` |
| 全ボリュームを削除 | `docker compose down -v` |

`down -v` は PostgreSQL のデータも完全に削除します。
`POSTGRES_USER` を変更した場合は `psql` の `-U` も合わせてください。

## Livebook

```sh
docker compose --profile livebook up -d
docker compose logs livebook
```

http://localhost:8080/ を開き、ログに表示されるトークンで認証します。
既定の attached runtime（既存の Erlang ノードに接続する実行環境）は Phoenix ノードを使うため、
ノートブックからアプリのモジュールを呼び出せます。
`Mix.install/2` が必要な場合は Livebook で standalone runtime を選択します。

トークン認証は有効です。Phoenix、Livebook、iframe 用の HTTP ポートはホストの
ループバックアドレスにのみ公開します。この開発環境を外部に公開しないでください。

## 既存の Phoenix アプリを使う

1. `./bin/setup` を実行し、アプリを `app/` に配置します。`app/mix.exs` が必要です。
2. `app/config/dev.exs` の末尾でデータベース接続先と HTTP の待受先を上書きします。
   以下はアプリ名が `hello_phoenix` の例です。

   ```elixir
   config :hello_phoenix, HelloPhoenix.Repo,
     hostname: System.get_env("DB_HOST", "localhost"),
     username: System.get_env("DB_USER", "postgres"),
     password: System.get_env("DB_PASSWORD", "postgres")

   config :hello_phoenix, HelloPhoenixWeb.Endpoint,
     http: [ip: {0, 0, 0, 0}, port: String.to_integer(System.get_env("PORT", "4000"))]
   ```

3. `app/config/test.exs` の末尾にも上の `Repo` の設定を追加します。Endpoint の変更は不要です。
4. 既存の `deps/` と `_build/` があれば別の場所へ移してから、キャッシュへのリンクを作ります。

   ```sh
   ln -s /cache/deps app/deps
   ln -s /cache/_build app/_build
   ```

5. 初期化して起動します。独自の `mix setup` を使うアプリでは、そのアプリの手順に従ってください。

   ```sh
   docker compose run --rm web mix setup
   docker compose up -d web
   ```

このスターターから `Dockerfile`、`docker-compose.yml`、`.env.example`、`bin/` を
アプリの親ディレクトリへコピーして使うこともできます。アプリはその下の `app/` に配置します。

## 参考資料

- [Phoenix のインストール](https://hexdocs.pm/phoenix/installation.html)と [phx.new](https://hexdocs.pm/phx_new/Mix.Tasks.Phx.New.html)
- [Compose の起動順序](https://docs.docker.com/compose/how-tos/startup-order/)と[プロファイル](https://docs.docker.com/compose/how-tos/profiles/)
- [Livebook の Docker 利用](https://github.com/livebook-dev/livebook#docker)
