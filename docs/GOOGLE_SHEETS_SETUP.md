# Google Sheets連携の設定ガイド

このドキュメントでは、コンシェルジュアプリでGoogle Sheetsを連携するためのサービスアカウント設定方法を説明します。

## 📋 概要

このアプリは**読み取り専用**でGoogle Sheetsからデータを取得します。そのため、最小権限の原則に従い、必要最小限の設定を行います。

## 🔑 必要な権限とスコープ

アプリで使用しているスコープ：
- `https://www.googleapis.com/auth/spreadsheets` - スプレッドシートの読み取り
- `https://www.googleapis.com/auth/drive` - Google Driveへのアクセス（スプレッドシートを開くため）

## 🛠️ 設定手順

### ステップ1: Google Cloud プロジェクトの作成・選択

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成、または既存のプロジェクトを選択
3. プロジェクト名は任意（例：「familyship-concierge」）

### ステップ2: 必要なAPIの有効化

以下のAPIを有効化します：

1. **Google Sheets API**
   - 「APIとサービス」→「ライブラリ」を開く
   - 「Google Sheets API」を検索して有効化

2. **Google Drive API**（スプレッドシートを開くために必要）
   - 「Google Drive API」を検索して有効化

### ステップ3: サービスアカウントの作成

1. 「APIとサービス」→「認証情報」を開く
2. 「認証情報を作成」→「サービスアカウント」を選択
3. サービスアカウントの詳細を入力：
   - **サービスアカウント名**: 任意（例：「familyship-sheets-reader」）
   - **サービスアカウントID**: 自動生成される
   - **説明**: 「ファミリーシップコンシェルジュ用のスプレッドシート読み取り専用アカウント」
4. 「作成して続行」をクリック

### ステップ4: サービスアカウントのIAMロール設定

**重要**: このアプリは読み取り専用なので、サービスアカウント自体に特別なIAMロールは**不要**です。

ただし、念のため最小限のロールを付与する場合：
- **ロール**: 「閲覧者」（Viewer）のみ
- または、ロールを付与せず、スプレッドシートの共有設定のみで対応（推奨）

**推奨**: IAMロールは付与せず、次のステップ5でスプレッドシートを直接共有する方法が最も安全です。

### ステップ5: サービスアカウントキーの作成

1. 作成したサービスアカウントをクリック
2. 「キー」タブを開く
3. 「キーを追加」→「新しいキーを作成」を選択
4. **キーのタイプ**: 「JSON」を選択
5. 「作成」をクリック
6. JSONファイルが自動的にダウンロードされます（**このファイルは安全に保管してください**）

### ステップ6: スプレッドシートの共有設定（最重要）

**これが最も重要なステップです。**

1. 連携したいGoogleスプレッドシートを開く
2. 右上の「共有」ボタンをクリック
3. サービスアカウントのメールアドレスを追加：
   - JSONファイル内の `"client_email"` の値をコピー
   - 例: `familyship-sheets-reader@your-project.iam.gserviceaccount.com`
4. **権限**: 「閲覧者」を選択（読み取り専用）
5. 「送信」をクリック（通知は不要なのでチェックを外してもOK）

**注意**: 
- サービスアカウントのメールアドレスは、JSONファイルの `client_email` フィールドに記載されています
- 複数のスプレッドシートを使用する場合は、それぞれに共有設定が必要です

### ステップ7: Streamlit Secretsへの設定

ダウンロードしたJSONファイルの内容を、Streamlit Secretsに設定します。

#### Streamlit Cloud の場合

1. Streamlit Cloud のダッシュボードでアプリを開く
2. 「Settings」→「Secrets」を開く
3. 以下の形式で追加：

```toml
GEMINI_API_KEY = "your-gemini-api-key"
GOOGLE_SHEETS_ID = "your-spreadsheet-id"
GOOGLE_SHEETS_CREDENTIALS = '''
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "your-private-key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "your-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
'''
```

**重要ポイント**:
- JSON全体をシングルクォート3つ（`'''`）で囲む
- JSON内の改行は `\n` で表現
- `private_key` の改行も `\n` で表現

#### ローカル開発の場合

`.streamlit/secrets.toml` ファイルを作成し、同じ形式で設定：

```toml
GEMINI_API_KEY = "your-gemini-api-key"
GOOGLE_SHEETS_ID = "your-spreadsheet-id"
GOOGLE_SHEETS_CREDENTIALS = '''
{
  "type": "service_account",
  ...
}
'''
```

### ステップ8: スプレッドシートIDの取得

スプレッドシートのURLからIDを取得：
```
https://docs.google.com/spreadsheets/d/【ここがスプレッドシートID】/edit
```

例: URLが `https://docs.google.com/spreadsheets/d/1a2b3c4d5e6f7g8h9i0j/edit` の場合
→ スプレッドシートIDは `1a2b3c4d5e6f7g8h9i0j`

## ✅ 設定確認

アプリを起動し、サイドバーの「講座データ読み込み状況」を確認：
- ✅ **Google Sheets** に接続中 → 正常に動作しています
- ⚠️ **認証情報が設定されていません** → Secretsの設定を確認
- 📄 **ローカルCSV** → Google Sheets未設定のため、ローカルファイルを使用

## 🔒 セキュリティのベストプラクティス

1. **最小権限の原則**
   - サービスアカウントにはIAMロールを付与しない（推奨）
   - スプレッドシートの共有権限は「閲覧者」のみ

2. **JSONファイルの管理**
   - JSONファイルはGitにコミットしない（`.gitignore`に追加済み）
   - Streamlit Secretsに設定後、ローカルのJSONファイルは削除してもOK

3. **定期的な確認**
   - 不要になったサービスアカウントは削除
   - 使用していないスプレッドシートの共有は解除

## ❓ トラブルシューティング

### エラー: "Access denied" または "Permission denied"

**原因**: スプレッドシートがサービスアカウントと共有されていない

**解決方法**:
1. スプレッドシートの「共有」設定を確認
2. サービスアカウントのメールアドレス（`client_email`）が追加されているか確認
3. 権限が「閲覧者」以上になっているか確認

### エラー: "API not enabled"

**原因**: 必要なAPIが有効化されていない

**解決方法**:
1. Google Cloud Consoleで「Google Sheets API」と「Google Drive API」が有効化されているか確認
2. 有効化されていない場合は有効化

### エラー: "Invalid credentials"

**原因**: JSONファイルの内容が正しくない、またはSecretsの設定が間違っている

**解決方法**:
1. JSONファイルの内容が完全か確認（特に `private_key` が正しく含まれているか）
2. Streamlit Secretsの `GOOGLE_SHEETS_CREDENTIALS` が正しい形式か確認
3. JSON内の改行が `\n` で正しくエスケープされているか確認

## 📚 参考リンク

- [Google Sheets API ドキュメント](https://developers.google.com/sheets/api)
- [サービスアカウントの作成と管理](https://cloud.google.com/iam/docs/service-accounts)
- [Streamlit Secrets の管理](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
