# デバッグ方法

## 「PCでは動くが、モバイルや Codespaces ではエラーになる」場合

**PC では正常に動いている**のに、**モバイルのブラウザ**や **GitHub Codespaces** で開くと「GEMINI_API_KEYが設定されていません」と出ることがあります。

### 理由

- **PC（ローカル）**  
  同じフォルダに `.env` があり、その中に `GEMINI_API_KEY` が書いてあるため、アプリが動きます。
- **Codespaces**  
  `.env` は **Git に含まれていません**（`.gitignore` で除外しているため）。  
  Codespaces はリポジトリをクローンした状態なので、**その環境には `.env` が存在しません**。  
  そのため、Codespaces 上で開いたときだけ API キー未設定エラーになります。
- **モバイルで同じ URL（PC で起動した Streamlit）にアクセスしている場合**  
  サーバーは PC 上の同じプロセスなので、API キーは読み込まれています。  
  この場合は「キーが無い」ではなく、**別の要因**（画面のエラー表示や、モバイルでのスクリプト読み込み失敗など）の可能性があります。

### 対処

- **Codespaces でも動かしたい場合**  
  Codespaces の環境にだけ、次のどちらかで API キーを渡してください。
  1. Codespaces 内で、プロジェクト直下に `.env` を新規作成し、`GEMINI_API_KEY=あなたのキー` を書く。
  2. リポジトリの **Settings → Secrets and variables → Codespaces** で `GEMINI_API_KEY` を追加する（推奨。キーをリポジトリに含めずに済みます）。
- **モバイルで「APIキーが設定されていません」と出る場合**  
  アクセスしている URL が **PC の Streamlit** なら、サーバー側にはキーがあるはずです。  
  その場合は、モバイルのブラウザのキャッシュ削除や、別ブラウザでのアクセスを試すと原因の切り分けになります。

---

## Python のトレースバックを確認するには

Streamlit の**画面上には、通常は Python のトレースバックは出ません**。  
エラー時には「エラー: GEMINI_API_KEY環境変数が設定されていません。」のようなメッセージだけが表示されます。

### トレースバックを見る場所

1. **ターミナル（推奨）**  
   `streamlit run app.py` を実行した**同じターミナル**に、Python のトレースバックが表示されます。
   - ローカル: コマンドを実行したターミナル
   - Codespaces: 下部の「ターミナル」パネルで `streamlit run app.py` を実行したタブ

2. **Streamlit の画面**  
   起動中に例外が発生した場合、アプリ側でトレースバックを表示する処理を入れています。  
   その場合は画面上のコードブロックにトレースバックが出ます。

### API キーエラーについて

「GEMINI_API_KEY環境変数が設定されていません」と出ている場合は、**API キーが未設定**です。  
この状態ではアプリは動かず、他の機能も試せません。

- **ローカル / Codespaces**  
  プロジェクト直下に `.env` を作成し、次の1行を追加してください。  
  `GEMINI_API_KEY=あなたのAPIキー`
- **Streamlit Cloud**  
  アプリの Settings → Secrets に  
  `GEMINI_API_KEY = "あなたのAPIキー"`  
  を追加してください。
- **GitHub Codespaces**  
  リポジトリの Settings → Secrets and variables → Codespaces で  
  `GEMINI_API_KEY` を追加すると、環境変数として自動で渡されます。

`.env` は `.gitignore` に入っているため、Git にはコミットされません。
