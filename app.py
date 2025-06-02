from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "your-secret-key-here"  # セッション管理用の秘密鍵


def get_db_connection():
    """データベース接続を取得する関数"""
    conn = sqlite3.connect("diary.db")
    conn.row_factory = sqlite3.Row  # 辞書形式でデータを取得
    return conn


@app.route("/")
def index():
    """日記一覧ページ"""
    try:
        conn = get_db_connection()
        diaries = conn.execute("SELECT * FROM diaries ORDER BY date DESC").fetchall()
        conn.close()
        return render_template("index.html", diaries=diaries)
    except Exception as e:
        flash(f"エラーが発生しました: {str(e)}", "error")
        return render_template("index.html", diaries=[])


@app.route("/post", methods=["GET", "POST"])
def post():
    """日記投稿ページ"""
    if request.method == "POST":
        # POSTリクエストの場合：日記を保存
        date = request.form["date"]
        content = request.form["content"]

        # バリデーション
        if not date or not content:
            flash("日付と内容は必須項目です。", "error")
            return render_template("post.html")

        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO diaries (date, content) VALUES (?, ?)", (date, content)
            )
            conn.commit()
            conn.close()
            flash("日記を保存しました！", "success")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"保存中にエラーが発生しました: {str(e)}", "error")
            return render_template("post.html")

    # GETリクエストの場合：投稿フォームを表示
    return render_template("post.html")


@app.route("/health")
def health():
    """アプリケーションの動作確認用エンドポイント"""
    return {
        "status": "OK",
        "message": "日記管理アプリは正常に動作しています",
        "database": "diary.db",
        "routes": ["/", "/post", "/health"],
    }


if __name__ == "__main__":
    # データベースファイルの存在確認
    if not os.path.exists("diary.db"):
        print("警告: diary.db が見つかりません。")
        print("ステップ3でデータベースを作成してください。")

    print("Flask アプリケーションを起動中...")
    print("ブラウザで http://localhost:5000 にアクセスしてください")
    app.run(debug=True, host="0.0.0.0", port=5000)
