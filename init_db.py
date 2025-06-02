import sqlite3
import os


def init_database():
    """データベースとテーブルを初期化する関数"""

    # データベースファイルのパス
    db_path = "diary.db"

    # 既存のデータベースファイルがあれば削除（開発時のみ）
    if os.path.exists(db_path):
        os.remove(db_path)
        print("既存のデータベースファイルを削除しました。")

    # データベースファイルの作成（なければ新規作成される）
    conn = sqlite3.connect(db_path)
    print("データベースファイル 'diary.db' を作成しました。")

    # カーソルオブジェクトの作成
    cursor = conn.cursor()

    # テーブルの作成
    cursor.execute(
        """
        CREATE TABLE diaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    print("テーブル 'diaries' を作成しました。")

    # サンプルデータの挿入（テスト用）
    sample_data = [
        ("2023-10-20", "今日は良い天気でした。散歩をして気分がリフレッシュしました。"),
        ("2023-10-19", "プログラミングの勉強をしました。Flaskについて学んでいます。"),
        ("2023-10-18", "友達と映画を見に行きました。とても面白かったです。"),
    ]

    cursor.executemany("INSERT INTO diaries (date, content) VALUES (?, ?)", sample_data)

    print("サンプルデータを挿入しました。")

    # データベースへコミット（変更を保存）
    conn.commit()

    # 作成されたデータの確認
    cursor.execute("SELECT * FROM diaries")
    rows = cursor.fetchall()

    print("\n作成されたデータ:")
    for row in rows:
        print(f"ID: {row[0]}, 日付: {row[1]}, 内容: {row[2][:20]}...")

    # 接続を閉じる
    conn.close()
    print("\nデータベースの初期化が完了しました。")


if __name__ == "__main__":
    init_database()
