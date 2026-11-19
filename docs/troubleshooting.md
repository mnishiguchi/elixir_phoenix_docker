# トラブルシューティング

## 生成ファイルに書き込めない

ホストで `id -u` と `id -g` を実行し、`.env` の `APP_UID`、`APP_GID` と比較します。
修正後はイメージを再ビルドします。

```sh
docker compose build --no-cache web
```

通常は `sudo` を使わず実行してください。Linux の Docker グループへのアクセスは
root 相当の権限を伴うため、ホスト側のアカウント管理にも注意が必要です。

## `app/ already exists` が表示される

`bin/new` は空のディレクトリにも上書きしません。既存アプリを使う場合は
[開発手順](development.md#既存の-phoenix-アプリを使う)を参照してください。
生成物が不要な場合は内容を確認し、別の場所へ移してから再実行します。

## PostgreSQL に接続できない・パスワード認証に失敗する

```sh
docker compose ps
docker compose logs db
docker compose exec db pg_isready -U postgres
```

`POSTGRES_USER` を変更した場合は `-U` も合わせます。
既存ボリュームの認証情報は初回初期化時の値のままです。`.env` の
`POSTGRES_PASSWORD` だけを変更してもデータベース内のパスワードは変わりません。
PostgreSQL のロールのパスワードを更新するか、不要なデータであることを確認して
`docker compose down -v` で初期化し直します。このコマンドはデータを削除します。

## HTTP ポートが使用中

`.env` の `PHX_PORT`、`LIVEBOOK_PORT`、`LIVEBOOK_IFRAME_PORT` を変更し、
サービスを再作成します。Phoenix のコンテナ内ポートは 4000 のままです。

## ファイル変更が反映されない

コンテナには変更監視用の `inotify-tools` が入っています。編集対象がマウントされた
`app/` 内かを確認してください。WSL2 の配置方針は[開発手順](development.md#実行環境)を参照してください。
監視が停止している場合は `docker compose restart web` で再起動します。

## Livebook から Phoenix に接続できない

`docker compose up -d web` で Phoenix を起動し、ログで起動成功を確認します。
`.env` の `ERLANG_COOKIE` をコンテナ起動の間に変更していないか確認してください。
接続先は `phoenix@web.phoenix.test` です。attached runtime には
ノード間通信を有効にした Phoenix と、Livebook に一致する Elixir マイナーバージョンが必要です。
`ELIXIR_IMAGE` を変更した場合は Livebook との互換性も確認します。

## アセット処理で daisyUI・heroicons・Phoenix JavaScript が見つからない

`app/deps -> /cache/deps` と `app/_build -> /cache/_build` のリンクを確認します。
Mix の環境変数とは別に、アセット処理もこの相対パスを使います。
`bin/new` はリンクを作成します。既存アプリの場合は[開発手順](development.md#既存の-phoenix-アプリを使う)に従ってください。
リンク先はコンテナ内にあるため、ホストからは存在しないように見える場合があります。

## 互換性のないビルド成果物が再利用される

キャッシュだけを初期化する場合は、スタックを停止し、`docker volume ls` で
プロジェクトに属する Mix 用ボリュームの名前を確認して対象だけを削除します。
`docker compose down -v` は PostgreSQL を含む全ボリュームを削除するため、用途を区別してください。
