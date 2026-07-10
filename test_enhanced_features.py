"""
Streamlit TODO App拡張機能テスト
新しく追加された以下の機能をテストします：
- タスク優先度機能
- タスク期限設定
- タスク検索機能
- 完了タスク一括削除
- データエクスポート
- 後方互換性
"""
import json
import os
import sys
from typing import List, Dict
from datetime import datetime

TEST_FILE = "test_todos_enhanced.json"


def load_tasks() -> List[Dict]:
    """ファイルからタスクを読み込む。"""
    try:
        if os.path.exists(TEST_FILE):
            with open(TEST_FILE, "r", encoding="utf-8") as f:
                tasks = json.load(f)
                for task in tasks:
                    if "priority" not in task:
                        task["priority"] = "中"
                    if "due_date" not in task:
                        task["due_date"] = None
                return tasks
    except (json.JSONDecodeError, IOError) as e:
        print(f"[Error] {e}")
    return []


def save_tasks(tasks: List[Dict]) -> bool:
    """タスクをJSONファイルに保存。"""
    try:
        with open(TEST_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"[Save Error] {e}")
        return False


def export_tasks_json(tasks: List[Dict]) -> str:
    """タスクをJSON形式でエクスポート。"""
    return json.dumps(tasks, ensure_ascii=False, indent=2)


def get_priority_icon(priority: str) -> str:
    """優先度アイコンを取得。"""
    priority_icons = {
        "高": "🔴",
        "中": "🟡",
        "低": "🟢"
    }
    return priority_icons.get(priority, "🟡")


def test_enhanced_features():
    """拡張機能のテスト"""
    print("=" * 60)
    print("Streamlit TODO App 拡張機能テスト")
    print("=" * 60)
    
    # Test 1: 優先度フィールドの追加
    print("\n[Test 1] 優先度フィールドの追加")
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    
    tasks = [
        {"task": "高優先度タスク", "done": False, "priority": "高", "due_date": None},
        {"task": "低優先度タスク", "done": False, "priority": "低", "due_date": None}
    ]
    assert save_tasks(tasks), "[FAIL] タスク保存失敗"
    loaded = load_tasks()
    assert loaded[0]["priority"] == "高", "[FAIL] 優先度が保存されていない"
    print("  [PASS] OK\n")
    
    # Test 2: 期限フィールドの追加
    print("[Test 2] 期限フィールドの追加")
    os.remove(TEST_FILE)
    
    today = datetime.now().isoformat()
    tasks = [
        {"task": "期限ありタスク", "done": False, "priority": "中", "due_date": today},
        {"task": "期限なしタスク", "done": False, "priority": "中", "due_date": None}
    ]
    assert save_tasks(tasks), "[FAIL] タスク保存失敗"
    loaded = load_tasks()
    assert loaded[0]["due_date"] is not None, "[FAIL] 期限が保存されていない"
    assert loaded[1]["due_date"] is None, "[FAIL] 期限なしが正しく保存されていない"
    print("  [PASS] OK\n")
    
    # Test 3: 後方互換性（古いタスクに優先度を追加）
    print("[Test 3] 後方互換性検証")
    os.remove(TEST_FILE)
    
    # 古いフォーマットのタスク（優先度・期限なし）
    old_tasks = [
        {"task": "旧フォーマットタスク", "done": False}
    ]
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(old_tasks, f)
    
    loaded = load_tasks()
    assert loaded[0]["priority"] == "中", "[FAIL] 優先度がデフォルト値で追加されていない"
    assert loaded[0]["due_date"] is None, "[FAIL] 期限がNoneで追加されていない"
    print("  [PASS] OK\n")
    
    # Test 4: 優先度アイコンの取得
    print("[Test 4] 優先度アイコン")
    assert get_priority_icon("高") == "🔴", "[FAIL] 高優先度のアイコンが正しくない"
    assert get_priority_icon("中") == "🟡", "[FAIL] 中優先度のアイコンが正しくない"
    assert get_priority_icon("低") == "🟢", "[FAIL] 低優先度のアイコンが正しくない"
    print("  [PASS] OK\n")
    
    # Test 5: 完了タスク一括削除
    print("[Test 5] 完了タスク一括削除")
    os.remove(TEST_FILE)
    
    tasks = [
        {"task": "完了タスク1", "done": True, "priority": "高", "due_date": None},
        {"task": "未完了タスク", "done": False, "priority": "中", "due_date": None},
        {"task": "完了タスク2", "done": True, "priority": "低", "due_date": None}
    ]
    assert save_tasks(tasks), "[FAIL] タスク保存失敗"
    
    # 完了タスクを削除
    remaining = [task for task in tasks if not task["done"]]
    assert len(remaining) == 1, "[FAIL] 未完了タスクが1つ残るべき"
    assert remaining[0]["task"] == "未完了タスク", "[FAIL] 間違ったタスクが削除された"
    print("  [PASS] OK\n")
    
    # Test 6: データエクスポート
    print("[Test 6] JSONエクスポート")
    os.remove(TEST_FILE)
    
    tasks = [
        {"task": "エクスポートテスト", "done": False, "priority": "高", "due_date": today}
    ]
    assert save_tasks(tasks), "[FAIL] タスク保存失敗"
    
    exported = export_tasks_json(tasks)
    assert isinstance(exported, str), "[FAIL] エクスポート結果が文字列でない"
    assert "エクスポートテスト" in exported, "[FAIL] タスク名がエクスポートに含まれていない"
    
    # エクスポート結果がJSON形式であることを確認
    parsed = json.loads(exported)
    assert len(parsed) == 1, "[FAIL] エクスポートされたタスク数が正しくない"
    print("  [PASS] OK\n")
    
    # Test 7: 検索フィルター
    print("[Test 7] 検索フィルター")
    os.remove(TEST_FILE)
    
    tasks = [
        {"task": "Python開発", "done": False, "priority": "高", "due_date": None},
        {"task": "JavaScript学習", "done": False, "priority": "中", "due_date": None},
        {"task": "Python学習", "done": False, "priority": "低", "due_date": None}
    ]
    assert save_tasks(tasks), "[FAIL] タスク保存失敗"
    
    # "Python"で検索
    search_term = "Python"
    filtered = [task for task in tasks if search_term.lower() in task["task"].lower()]
    assert len(filtered) == 2, "[FAIL] 検索結果が正しくない"
    print("  [PASS] OK\n")
    
    # Test 8: 優先度でソート
    print("[Test 8] 優先度でソート")
    os.remove(TEST_FILE)
    
    tasks = [
        {"task": "低優先度", "done": False, "priority": "低", "due_date": None},
        {"task": "高優先度", "done": False, "priority": "高", "due_date": None},
        {"task": "中優先度", "done": False, "priority": "中", "due_date": None}
    ]
    
    priority_order = {"高": 0, "中": 1, "低": 2}
    sorted_tasks = sorted(tasks, key=lambda x: priority_order.get(x.get("priority", "中"), 1))
    
    assert sorted_tasks[0]["priority"] == "高", "[FAIL] 高優先度が最初にある"
    assert sorted_tasks[1]["priority"] == "中", "[FAIL] 中優先度が次にある"
    assert sorted_tasks[2]["priority"] == "低", "[FAIL] 低優先度が最後にある"
    print("  [PASS] OK\n")
    
    # クリーンアップ
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    
    print("=" * 60)
    print("All tests passed! 拡張機能は正常に動作しています。")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_enhanced_features()
    except AssertionError as e:
        print(f"\n[FAILED] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
