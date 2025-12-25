# Python MIDI Editor for GitHub Codespaces

このプロジェクトは、PythonとFlaskを使用し、ブラウザ上で楽譜入力・MIDI出力ができる軽量エディタです。

## 機能
- **楽譜UI入力**: 五線譜をクリックして音符(C4〜B5)を配置。
- **プレビュー再生**: ブラウザのWeb Audio APIを使用して音を確認。
- **MIDIエクスポート**: 作成したメロディを`.mid`ファイルとしてダウンロード。
- **GitHub Codespaces対応**: ポート転送機能で即座にプレビュー可能。

## 使い方 (GitHub Codespaces)

1. **リポジトリを開く**
   - GitHubで新しいリポジトリを作成し、上記ファイルをアップロードします。
   - `Code`ボタンをクリックし、`Codespaces`タブから`Create codespace on main`を選択します。

2. **ライブラリのインストール**
   ターミナル（画面下部）で以下のコマンドを実行します：
   ```bash
   pip install -r requirements.txt
