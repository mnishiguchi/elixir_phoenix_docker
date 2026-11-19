# 引数をシェルの位置引数として渡し、アプリ名をコマンドとして解釈させません。
set positional-arguments
set shell := ["sh", "-eu", "-c"]

# 利用できるコマンドを一覧表示する
@default:
    just --list

# ローカル設定を作成する（既存の .env は保持）
setup:
    ./bin/setup

# Phoenix アプリを app/ に生成して初期化する
new name:
    ./bin/new "$1"

# Phoenix と PostgreSQL を起動する
up:
    docker compose up -d web

# Phoenix のログを追跡する
logs:
    docker compose logs -f web

# 起動済みの web コンテナでシェルを開く
shell:
    docker compose exec web sh

# 一時コンテナでアプリの IEx を起動する
iex:
    docker compose run --rm web iex -S mix

# テスト用データベースで Phoenix のテストを実行する
test:
    docker compose run --rm -e MIX_ENV=test web mix test

# 開発用データベースのマイグレーションを実行する
migrate:
    docker compose run --rm web mix ecto.migrate

# Phoenix と Livebook を起動する（トークンは Livebook のログで確認）
livebook:
    docker compose --profile livebook up -d

# Livebook を含む開発環境を停止する（ボリュームは保持）
down:
    docker compose --profile livebook down
