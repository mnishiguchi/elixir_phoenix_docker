# ドキュメント

初めて使う場合は[ルート README](../README.md)から始めてください。

## 現行の仕様・手順

| 資料 | 内容 |
| --- | --- |
| [開発手順](development.md) | コマンド、設定、Livebook、既存アプリ、OS 別の注意点 |
| [トラブルシューティング](troubleshooting.md) | よくある問題の確認と対処 |
| [移行手順](migration.md) | 旧ディレクトリ構成からの移行とデータの扱い |
| [検証手順](validation.md) | オフラインテスト、Docker 統合テスト、CI |

## 設計判断・過去の記録

- [開発環境の設計判断](design-decisions/0001-unify-development-environment.md)
- [2026-11-19 の動作確認](worklog/20261119-development-smoke-test.md)

## 管理方針

現行の手順はこのディレクトリ直下で管理します。長期的な設計判断は
`design-decisions/`、日付のある調査・実験・検証結果は `worklog/` に保存します。
実測記録は当時の環境と結果を残し、現在の手順とは分けて扱います。

更新時は既存の資料を優先し、同じ説明を複製せず正となる資料へリンクしてください。
構成や手順を変更したときは関連資料とこの目次を更新します。
細かな変更履歴は Git に任せます。ファイル名の題名部分は英語の小文字の kebab-case とし、
設計判断は `NNNN-topic.md`、作業記録は `YYYYMMDD-topic.md` とします。
設計判断の番号は4桁の連番とし、本文は日本語で記述します。
文章の共通方針は [AGENTS.md](../AGENTS.md) を参照してください。
