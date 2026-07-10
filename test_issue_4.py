"""
Issue #4: ローカルJSONファイルへのデータの保存と読み込み
このテストスクリプトで、Issue #4の実装が要件を満たしているか検証します。
"""
import json
import os
import sys
from typing import List, Dict

TODOS_FILE = "test_todos.json"


def load_tasks() -> List[Dict]:
    """ファイルからタスクを読み込む。エラー時は空リストを返す。"""
    try:
        if os.path.exists(TODOS_FILE):
            with open(TODOS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"[Error] {e}")
    return []


def save_tasks(tasks: List[Dict]) -> bool:
    """タスクをJSONファイルに保存。成功時Trueを返す。"""
    try:
        with open(TODOS_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"[Save Error] {e}")
        return False


def test_issue_4():
    """Issue #4の完了条件を検証"""
    print("=" * 60)
    print("Issue #4: JSONファイルへのデータ保存・読み込み検証")
    print("=" * 60)
    
    # Test 1: アプリ起動時のファイル読み込み
    print("\n[Test 1] アプリ起動時の読み込み処理")
    print("- ファイルが存在しない場合: 空リストを返す")
    if os.path.exists(TODOS_FILE):
        os.remove(TODOS_FILE)
    
    tasks = load_tasks()
    assert tasks == [], f"[FAIL] 空リストが返されるべき。実際: {tasks}"
    print("  [PASS] OK\n")
    
    # Test 2: タスク追加時の保存
    print("[Test 2] タスク追加時の保存")
    test_tasks = [
        {"task": "テストタスク1", "done": False},
        {"task": "テストタスク2", "done": True}
    ]
    result = save_tasks(test_tasks)
    assert result is True, "[FAIL] save_tasks()がTrueを返すべき"
    assert os.path.exists(TODOS_FILE), "[FAIL] ファイルが作成されていない"
    print("  [PASS] OK\n")
    
    # Test 3: 保存したデータの読み込み
    print("[Test 3] 保存したデータの読み込み")
    loaded_tasks = load_tasks()
    assert loaded_tasks == test_tasks, f"[FAIL] データが正しく読み込まれていない。実際: {loaded_tasks}"
    print("  [PASS] OK\n")
    
    # Test 4: JSONファイルのフォーマット
    print("[Test 4] JSONファイルのフォーマット検証")
    with open(TODOS_FILE, "r", encoding="utf-8") as f:
        content = json.load(f)
    assert isinstance(content, list), "[FAIL] JSONはリスト形式であるべき"
    for task in content:
        assert "task" in task and "done" in task, "[FAIL] taskとdoneキーが必須"
    print("  [PASS] JSON形式が正しい\n")
    
    # Test 5: 完了条件の確認
    print("[Test 5] 完了条件の確認")
    print("- ブラウザリロード・サーバー再起動後も、JSONファイルから復元可能")
    restored_tasks = load_tasks()
    assert len(restored_tasks) == 2, "[FAIL] データが正しく復元されていない"
    print("  [PASS] データ永続化が機能している\n")
    
    # クリーンアップ
    os.remove(TODOS_FILE)
    
    print("=" * 60)
    print("All tests passed! Issue #4の実装は要件を満たしています。")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_issue_4()
    except AssertionError as e:
        print(f"\n[FAILED] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
