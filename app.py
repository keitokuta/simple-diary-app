from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import logging
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "diary-app-secret-key-2023"

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db_connection():
    """データベース接続を取得"""
    if not os.path.exists("diary.db"):
        raise FileNotFoundError(
            "データベースファイルが見つかりません。ステップ3でデータベースを作成してください。"
        )

    conn = sqlite3.connect("diary.db")
    conn.row_factory = sqlite3.Row
    return conn


def validate_diary_data(date, content):
    """日記データのバリデーション"""
    errors = []

    # 日付の検証
    if not date:
        errors.append("日付は必須項目です。")
    else:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            errors.append("正しい日付形式で入力してください。")

    # 内容の検証
    if not content:
        errors.append("日記の内容は必須項目です。")
    else:
        content = content.strip()
        if len(content) < 5:
            errors.append("日記の内容は5文字以上で入力してください。")
        elif len(content) > 1000:
            errors.append("日記の内容は1000文字以内で入力してください。")

    return errors, content.strip() if content else ""


@app.route("/post", methods=["GET", "POST"])
def post():
    """日記投稿ページ"""
    if request.method == "POST":
        try:
            date = request.form.get("date")
            content = request.form.get("content")

            logger.info(
                f"日記投稿試行: 日付={date}, 内容長={len(content) if content else 0}"
            )

            # バリデーション
            errors, cleaned_content = validate_diary_data(date, content)

            if errors:
                for error in errors:
                    flash(error, "error")
                logger.warning(f"バリデーションエラー: {errors}")
                return render_template("post.html")

            # データベース保存
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO diaries (date, content) VALUES (?, ?)",
                (date, cleaned_content),
            )
            conn.commit()

            diary_id = cursor.lastrowid
            conn.close()

            logger.info(f"日記保存成功: ID={diary_id}")
            flash("日記を保存しました！", "success")
            return redirect(url_for("index"))

        except FileNotFoundError as e:
            logger.error(f"ファイルエラー: {str(e)}")
            flash("データベースファイルが見つかりません。", "error")
            return render_template("post.html")

        except sqlite3.Error as e:
            logger.error(f"データベースエラー: {str(e)}")
            flash("データベースエラーが発生しました。", "error")
            return render_template("post.html")

        except Exception as e:
            logger.error(f"予期しないエラー: {str(e)}")
            flash("予期しないエラーが発生しました。", "error")
            return render_template("post.html")

    return render_template("post.html")


@app.route("/")
def index():
    """日記一覧ページ"""
    try:
        conn = get_db_connection()
        diaries = conn.execute(
            "SELECT * FROM diaries ORDER BY date DESC, id DESC"
        ).fetchall()
        conn.close()
        return render_template("index.html", diaries=diaries)
    except Exception as e:
        logger.error(f"データ取得エラー: {str(e)}")
        flash(f"データの取得中にエラーが発生しました: {str(e)}", "error")
        return render_template("index.html", diaries=[])


if __name__ == "__main__":
    print("日記管理アプリを起動中...")
    print("ブラウザで http://localhost:5000 にアクセスしてください")
    app.run(debug=True, host="0.0.0.0", port=5000)
