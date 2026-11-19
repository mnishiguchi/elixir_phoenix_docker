# Elixir / Phoenix + Docker Compose

Phoenix のローカル開発用スターターです。macOS、Linux、Windows + WSL2 で
共通の Docker Compose 構成を使い、PostgreSQL と任意の Livebook を組み合わせます。
本番環境へのデプロイは対象外です。

## はじめに

Docker Engine と Docker Compose v2 以降、または Docker Desktop を用意してください。
ホストに Elixir、Erlang、PostgreSQL、Node.js をインストールする必要はありません。
Windows では PowerShell ではなく WSL2 の Linux シェルを使います。

リポジトリを取得し、ルートディレクトリで実行します。

```sh
./bin/new hello_phoenix
docker compose up -d web
```

http://localhost:4000/ を開きます。初回はイメージの取得とコンパイルに時間がかかります。
起動状況は `docker compose logs -f web` で確認できます。

`bin/new` はローカル設定と認証情報を `.env` に作成し、`app/` に Phoenix アプリを
生成してデータベースと依存関係を初期化します。既存の `.env` は保持し、
既存の `app/` には上書きしません。生成した `app/` はこのリポジトリの Git 管理対象外です。

停止するときは `docker compose down` を実行します。データベースのボリュームは残ります。

## just を使う場合（任意）

[just](https://just.systems/man/en/installation.html) を導入すると、開発コマンドを短く実行できます。
macOS で Homebrew を使う場合は `brew install just`、Linux・WSL2 で Cargo を使う場合は
`cargo install just --locked` でインストールできます。その他の導入方法は公式資料を参照してください。

```sh
just                       # コマンドと説明の一覧（just --list でも表示）
just new hello_phoenix      # 新規アプリの生成と初期化
just up                    # 起動
just test                  # アプリのテスト
just down                  # Livebook を含めて停止（データ保持）
```

just がなくても、上記のスクリプトと Compose コマンドで操作できます。
コマンドの対応表は[開発手順](docs/development.md#日常のコマンド)を参照してください。

## 詳しい使い方

- [開発手順](docs/development.md)：日常のコマンド、Livebook、既存アプリの利用、OS 別の注意点
- [トラブルシューティング](docs/troubleshooting.md)
- [旧構成からの移行](docs/migration.md)
- [資料一覧](docs/README.md)：設計判断、検証手順、実測記録

Linux x86_64 で動作確認済みです。他の対象環境の検証状況は
[検証記録](docs/worklog/20261119-development-smoke-test.md)を参照してください。

## ライセンス

[MIT License](LICENSE) を適用します。
