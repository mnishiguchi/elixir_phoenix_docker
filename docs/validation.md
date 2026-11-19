# 検証手順

実施済みの結果と未検証事項は[検証記録](worklog/20261119-development-smoke-test.md)に保存しています。
ここでは現行の手順を説明します。

## オフラインテスト

Compose の構造と `bin/new`、`bin/setup` の動作を確認します。
スクリプトのテストでは Docker の代替実行ファイルを使うため、Docker デーモンやネットワークは不要です。
PyYAML の初回インストールにはネットワークが必要です。
just を導入済みの場合は、引数の安全な受け渡し、サブディレクトリからの実行、
テスト環境の指定、データを保持する停止、失敗の伝播も確認します。
just がない場合はこの4件のみ省略し、既存のテストは実行します。

```sh
python3 -m pip install PyYAML
python3 -m unittest discover -s tests -v
sh -n bin/setup
sh -n bin/new
```

just を導入済みの場合は、形式とコマンド一覧も確認してください。

```sh
just --fmt --check
just --list
```

## Compose 構成の確認

Docker Compose を使える環境で実行します。

```sh
./bin/setup
docker compose config -q
docker compose --profile livebook config -q
```

## 統合テスト

`app/` がまだないチェックアウトで実行してください。Docker デーモン、インターネット接続、
依存関係の取得とコンパイルのための時間が必要です。

```sh
./bin/new smoke_app
docker compose up -d web
docker compose run --rm -e MIX_ENV=test web mix test
curl -fsS http://127.0.0.1:4000/
docker compose --profile livebook up -d
python3 tests/smoke_livebook.py
```

起動直後に HTTP 接続が失敗した場合は、`docker compose logs web` で起動を確認して再試行します。
ポートを変更した場合は `curl` の接続先も変更してください。

Livebook のチェックはアプリ名 `smoke_app` を前提とします。
未認証アクセスと不正なトークンの拒否、ログのトークンによるセッション確立を確認します。
さらに Livebook の attached runtime で Phoenix ノード上のコードを評価し、
`SmokeApp.Repo` 経由で PostgreSQL に問い合わせます。
Python の標準ライブラリと Livebook イメージ内の Elixir を使います。
ブラウザー画面での操作は別途手動で確認してください。

終了後はサービスを停止します。ボリュームは保持します。

```sh
docker compose --profile livebook down
```

just 経由で統合テストを行う場合は、[開発手順の対応表](development.md#日常のコマンド)に従って
生成・起動・テスト・Livebook 起動・停止をそれぞれ `just new smoke_app`、`just up`、
`just test`、`just livebook`、`just down` に置き換えます。

## CI

[GitHub Actions](../.github/workflows/validate.yml) は push と PR でオフラインテスト、
シェル構文、justfile の形式とコマンド一覧、Compose 構成を確認します。手動の `workflow_dispatch` ではアプリの生成、
コンパイル、起動、Phoenix テスト、Livebook のチェックも実行し、最後にサービスを停止します。
生成・起動・テスト・Livebook 起動・停止は just 経由で実行します。
この検証は開発環境の動作確認であり、セキュリティ監査ではありません。
