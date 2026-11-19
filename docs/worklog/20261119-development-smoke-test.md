# 2026-11-19 開発環境の動作確認

## 環境

Linux x86_64（LMDE 7）、Docker Engine 29.10.0、Docker Compose 5.8.0 で確認しました。
web は Elixir 1.19.5 / OTP 28、Livebook は 0.19.10（Elixir 1.19.3 / OTP 28）、
Phoenix generator は 1.8.16、PostgreSQL は 17 です。

## 結果

| 確認項目 | 結果 |
| --- | --- |
| 既定構成と Livebook プロファイルの Compose 構成 | 成功 |
| Debian 開発イメージのビルド、非 root UID/GID | 成功 |
| Phoenix の新規生成と `mix setup` | 成功 |
| localhost:4000 の HTTP 応答 | 200 |
| バインドマウントした HEEx テンプレートの再読み込み | 成功 |
| PostgreSQL に接続した生成アプリのテスト | 5 件成功 |
| Livebook の未認証・不正トークン拒否と正常なログイン | 成功 |
| attached runtime のコード評価と Phoenix Repo の問い合わせ | 成功（`SELECT 1` が `[[1]]` を返却） |
| オフラインテストとシェル構文 | 8 件成功、構文確認成功 |

初回の実行で、アセット処理がアプリ相対の `deps/`、`_build/` を必要とすることと、
Livebook が接続先に同じ Elixir マイナーバージョンを要求することを確認しました。
キャッシュへのリンクを追加し、web の初期値を Elixir 1.20 / OTP 29 から
1.19 / OTP 28 に合わせた後、新規生成から再確認しました。
継続的な確認手順は[検証手順](../validation.md)を参照してください。

## 未検証事項

macOS Intel、macOS Apple Silicon、Linux ARM64、Windows WSL2 の実機確認は未実施です。
Elixir イメージのマニフェストには amd64 と arm64 が含まれますが、
これは ARM64 での実行成功を確認したものではありません。

Livebook のブラウザー画面での操作は未確認です。今回確認したのは HTTP 認証と
Livebook の実際の attached-runtime プロトコルによる評価です。

## just 導入後の追加確認

同じ Linux x86_64 ホストで just 1.59.0 を使い、以下を確認しました。

- 形式の検証と日本語の説明付きコマンド一覧の表示。
- 既存8件と just 用4件を合わせた12件のオフラインテスト成功。
  just 用テストは特殊文字を含む引数、実行ディレクトリ、テスト環境と停止処理、失敗の伝播を確認。
- `just setup` が既存の `.env` を保持。
- web 停止中の `just test` が PostgreSQL を起動し、生成アプリの5件のテストに成功。
- `just migrate`、`just up`、`just shell`、`just iex`、`just logs` の実行。
  シェルの作業ディレクトリは `/workspace/app`、UID は 1000。IEx で `SELECT 1` が成功。
- `just livebook` 後の Phoenix HTTP 200、Livebook の認証と attached runtime の DB 問い合わせ。
- `just down` で全サービスが停止し、停止前後で名前付きボリュームの一覧が一致。

`just new` の引数受け渡しは代替スクリプトで検証しました。今回の追加確認では、
既存の生成アプリを使用し、新規生成からの統合テストは再実行していません。
新規生成を含む just 経由の確認は手動 CI ワークフローにも追加しましたが、CI はまだ実行していません。
macOS・WSL2 における just の実機確認も未実施です。
