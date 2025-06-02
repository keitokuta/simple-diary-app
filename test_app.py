import sqlite3
import os
import sys
from datetime import datetime


def test_database():
    """データベースのテスト"""
    print("=== データベーステスト ===")

    if not os.path.exists("diary.db"):
        print("❌ データベースファイルが見つかりません")
        return False

    try:
        conn = sqlite3.connect("diary.db")
        cursor = conn.cursor()

        # テーブルの存在確認
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='diaries'"
        )
        if not cursor.fetchone():
            print("❌ diariesテーブルが見つかりません")
            return False

        # テーブル構造の確認
        cursor.execute("PRAGMA table_info(diaries)")
        columns = cursor.fetchall()
        expected_columns = ["id", "date", "content", "created_at"]
        actual_columns = [col[1] for col in columns]

        for col in expected_columns:
            if col not in actual_columns:
                print(f"❌ カラム '{col}' が見つかりません")
                return False

        # データの件数確認
        cursor.execute("SELECT COUNT(*) FROM diaries")
        count = cursor.fetchone()[0]
        print(f"✅ データベース正常 (日記件数: {count}件)")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ データベースエラー: {str(e)}")
        return False


def test_files():
    """必要ファイルの存在確認"""
    print("\n=== ファイル存在確認 ===")

    required_files = [
        "app.py",
        "templates/index.html",
        "templates/post.html",
        "static/style.css",
    ]

    all_exists = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} が見つかりません")
            all_exists = False

    return all_exists


def test_app_import():
    """アプリケーションのインポートテスト"""
    print("\n=== アプリケーションインポートテスト ===")

    try:
        # app.pyをインポートしてみる
        import app

        print("✅ app.py のインポート成功")

        # Flaskアプリケーションの存在確認
        if hasattr(app, "app"):
            print("✅ Flaskアプリケーション確認")
        else:
            print("❌ Flaskアプリケーションが見つかりません")
            return False

        return True

    except ImportError as e:
        print(f"❌ インポートエラー: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {str(e)}")
        return False


def main():
    """メインテスト関数"""
    print("🧪 日記管理アプリ 統合テスト開始")
    print("=" * 50)

    tests = [test_files, test_database, test_app_import]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 50)
    print("📊 テスト結果")

    passed = sum(results)
    total = len(results)

    if passed == total:
        print(f"✅ 全てのテストが成功しました ({passed}/{total})")
        print("🎉 アプリケーションは正常に動作する準備ができています！")
        return True
    else:
        print(f"❌ {total - passed}個のテストが失敗しました ({passed}/{total})")
        print("🔧 問題を修正してから再度テストしてください。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
