# 旧構成からの移行

以前の `mac/`、`non_mac/`、`mixed/`、`mixed_debian/` は、ルートの
`Dockerfile` と `docker-compose.yml` に統合しました。
`mac_with_livebook/`、`non_mac_with_livebook/`、`mixed_with_livebook/` の代わりに
`--profile livebook` を使います。

旧構成の `version: '3'`、`links:`、複数のビルドターゲットは使いません。
旧構成から PostgreSQL のメジャーバージョンも変更しています。
現在の初期値は [.env.example](../.env.example) と [Compose 構成](../docker-compose.yml)で確認してください。

PostgreSQL 14 のデータディレクトリを PostgreSQL 17 に直接マウントしないでください。
事前にバックアップを取り、ダンプと復元、または適切なメジャーバージョン更新手順で移行します。
新規プロジェクトでは新しい名前付きボリュームを使います。

既存アプリはソースとデータベースのバックアップを保持し、
[既存アプリの利用手順](development.md#既存の-phoenix-アプリを使う)に従って設定を追加します。
動作中のアプリの `config/*.exs` を丸ごと置き換えないでください。

今回の変更は構造の再設計であり、既存アプリやデータの互換性を保証する更新ではありません。
重複した構成の保守を避けるため、旧ディレクトリは削除しています。
