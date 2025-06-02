from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import logging
from datetime import datetime
import os
import math

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


def format_date(date_string):
    """日付文字列をフォーマット"""
    try:
        from datetime import datetime

        date_obj = datetime.strptime(date_string, "%Y-%m-%d")
        return date_obj.strftime("%Y年%m月%d日")
    except:
        return date_string


def truncate_content(content, max_length=100):
    """内容を指定した長さで切り詰める"""
    if len(content) <= max_length:
        return content
    return content[:max_length] + "..."


# テンプレートフィルターとして登録
app.jinja_env.filters["format_date"] = format_date
app.jinja_env.filters["truncate_content"] = truncate_content


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
    """日記一覧ページ（完全版）"""
    # パラメータの取得
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)
    search_query = request.args.get("search", "").strip()
    sort_by = request.args.get("sort", "date")
    order = request.args.get("order", "desc")

    # パラメータの検証
    if per_page not in [5, 10, 20]:
        per_page = 5
    if page < 1:
        page = 1

    try:
        conn = get_db_connection()

        # 基本クエリとパラメータ
        base_conditions = []
        params = []

        # 検索条件の構築
        if search_query:
            base_conditions.append("(content LIKE ? OR date LIKE ?)")
            search_param = f"%{search_query}%"
            params.extend([search_param, search_param])

        # WHERE句の構築
        where_clause = ""
        if base_conditions:
            where_clause = " WHERE " + " AND ".join(base_conditions)

        # 総件数の取得
        count_query = f"SELECT COUNT(*) as total FROM diaries{where_clause}"
        total = conn.execute(count_query, params).fetchone()["total"]

        # ページネーション計算
        total_pages = math.ceil(total / per_page) if total > 0 else 1
        if page > total_pages:
            page = total_pages

        offset = (page - 1) * per_page

        # 並び替え条件の検証と構築
        valid_sort_columns = ["date", "id", "created_at"]
        valid_orders = ["asc", "desc"]

        if sort_by not in valid_sort_columns:
            sort_by = "date"
        if order not in valid_orders:
            order = "desc"

        order_clause = f" ORDER BY {sort_by} {order.upper()}"
        if sort_by != "id":
            order_clause += ", id DESC"  # 同じ日付の場合はIDで並び替え

        # データ取得クエリ
        data_query = (
            f"SELECT * FROM diaries{where_clause}{order_clause} LIMIT ? OFFSET ?"
        )
        data_params = params + [per_page, offset]

        diaries = conn.execute(data_query, data_params).fetchall()
        conn.close()

        # ページネーション情報
        pagination = {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_prev": page > 1,
            "has_next": page < total_pages,
            "prev_num": page - 1 if page > 1 else None,
            "next_num": page + 1 if page < total_pages else None,
            "start_index": offset + 1 if total > 0 else 0,
            "end_index": min(offset + per_page, total),
        }

        logger.info(
            f'日記一覧表示: ページ={page}, 件数={len(diaries)}, 検索="{search_query}"'
        )

        return render_template(
            "index.html",
            diaries=diaries,
            pagination=pagination,
            search_query=search_query,
            sort_by=sort_by,
            order=order,
        )

    except sqlite3.Error as e:
        logger.error(f"データベースエラー: {str(e)}")
        flash("データベースエラーが発生しました。", "error")
        return render_template("index.html", diaries=[], pagination=None)
    except Exception as e:
        logger.error(f"予期しないエラー: {str(e)}")
        flash("予期しないエラーが発生しました。", "error")
        return render_template("index.html", diaries=[], pagination=None)


if __name__ == "__main__":
    print("日記管理アプリを起動中...")
    print("ブラウザで http://localhost:5000 にアクセスしてください")
    app.run(debug=True, host="0.0.0.0", port=5000)
