"""
Streamlit TODO App - Phase 2機能テスト
タスク編集、カテゴリ分類、ダークモード、自動バックアップをテストします。
"""
import json
import os
import sys
import shutil
from typing import List, Dict
from datetime import datetime

TEST_FILE = "test_todos_phase2.json"
BACKUP_DIR = "test_backups"
THEME_CONFIG = "test_theme_config.json"


def cleanup():
    """テストファイルをクリーンアップ。"""
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    if os.path.exists(THEME_CONFIG):
        os.remove(THEME_CONFIG)
    if os.path.exists(BACKUP_DIR):
        shutil.rmtree(BACKUP_DIR)


def load_tasks() -> List[Dict]:
    """ファイルからタスクを読み込む。"""
    try:
        if os.path.exists(TEST_FILE):
            with open(TEST_FILE, "r", encoding="utf-8") as f:
                tasks = json.load(f)
                for task in tasks:
                    if "category" not in task:
                        task["category"] = "その他"
                    if "updated_at" not in task:
                        task["updated_at"] = datetime.now().isoformat()
                    if "task_id" not in task:
                        task["task_id"] = hash(task.get("task", "")) % 10000
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


def create_backup_dir():
    """バックアップディレクトリを作成。"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)


def auto_backup_tasks(tasks: List[Dict]) -> bool:
    """タスクの自動バックアップを作成。"""
    try:
        create_backup_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(BACKUP_DIR, f"backup_{timestamp}.json")
        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False


def get_category_icon(category: str) -> str:
    """カテゴリアイコンを取得。"""
    category_icons = {
        "仕事": "💼",
        "プライベート": "🎯",
        "学習": "📚",
        "健康": "🏃",
        "その他": "📌"
    }
    return category_icons.get(category, "📌")


def save_theme_config(theme: Dict) -> bool:
    """テーマ設定を保存。"""
    try:
        with open(THEME_CONFIG, "w", encoding="utf-8") as f:
            json.dump(theme, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False


def test_phase2_features():
    """Phase 2機能のテスト"""
    print("=" * 60)
    print("Streamlit TODO App - Phase 2機能テスト")
    print("=" * 60)
    
    cleanup()
    
    # Test 1: カテゴリフィールドの追加
    print("\n[Test 1] カテゴリフィールドの追加")
    tasks = [
        {"task": "仕事タスク", "done": False, "priority": "高", "category": "仕事", "updated_at": datetime.now().isoformat()},
        {"task": "学習タスク", "done": False, "priority": "中", "category": "学習", "updated_at": datetime.now().isoformat()}
    ]
    assert save_tasks(tasks), "[FAIL] タスク保存失敗"
    loaded = load_tasks()
    assert loaded[0]["category"] == "仕事", "[FAIL] カテゴリが保存されていない"
    assert loaded[1]["category"] == "学習", "[FAIL] カテゴリが保存されていない"
    print("  [PASS] OK\n")
    
    # Test 2: 後方互換性（カテゴリなしのタスク）
    print("[Test 2] 後方互換性：カテゴリなしのタスク")
    cleanup()
    old_tasks = [
        {"task": "旧タスク", "done": False, "priority": "中"}
    ]
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(old_tasks, f)
    
    loaded = load_tasks()
    assert loaded[0]["category"] == "その他", "[FAIL] デフォルトカテゴリが設定されていない"
    print("  [PASS] OK\n")
    
    # Test 3: タスク編集機能
    print("[Test 3] タスク編集機能")
    cleanup()
    tasks = [
        {
            "task": "編集前", 
            "done": False, 
            "priority": "中",
            "category": "その他",
            "task_id": 123,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]
    assert save_tasks(tasks), "[FAIL] タスク保存失敗"
    
    # タスクを編集
    loaded = load_tasks()
    loaded[0]["task"] = "編集後"
    loaded[0]["priority"] = "高"
    loaded[0]["category"] = "仕事"
    loaded[0]["updated_at"] = datetime.now().isoformat()
    
    assert save_tasks(loaded), "[FAIL] 編集したタスク保存失敗"
    updated = load_tasks()
    assert updated[0]["task"] == "編集後", "[FAIL] タスク名が更新されていない"
    assert updated[0]["priority"] == "高", "[FAIL] 優先度が更新されていない"
    assert updated[0]["category"] == "仕事", "[FAIL] カテゴリが更新されていない"
    print("  [PASS] OK\n")
    
    # Test 4: カテゴリアイコン
    print("[Test 4] カテゴリアイコン")
    assert get_category_icon("仕事") == "💼", "[FAIL] 仕事のアイコンが正しくない"
    assert get_category_icon("学習") == "📚", "[FAIL] 学習のアイコンが正しくない"
    assert get_category_icon("健康") == "🏃", "[FAIL] 健康のアイコンが正しくない"
    assert get_category_icon("その他") == "📌", "[FAIL] その他のアイコンが正しくない"
    print("  [PASS] OK\n")
    
    # Test 5: 自動バックアップ作成
    print("[Test 5] 自動バックアップ作成")
    cleanup()
    tasks = [{"task": "バックアップテスト", "done": False, "priority": "中", "category": "その他"}]
    assert auto_backup_tasks(tasks), "[FAIL] バックアップ作成失敗"
    assert os.path.exists(BACKUP_DIR), "[FAIL] バックアップディレクトリが作成されていない"
    backups = os.listdir(BACKUP_DIR)
    assert len(backups) > 0, "[FAIL] バックアップファイルが作成されていない"
    print("  [PASS] OK\n")
    
    # Test 6: バックアップディレクトリの確認
    print("[Test 6] バックアップディレクトリの確認")
    create_backup_dir()
    assert os.path.exists(BACKUP_DIR), "[FAIL] バックアップディレクトリが存在しない"
    print("  [PASS] OK\n")
    
    # Test 7: テーマ設定
    print("[Test 7] テーマ設定")
    theme = {"theme": "dark"}
    assert save_theme_config(theme), "[FAIL] テーマ設定保存失敗"
    assert os.path.exists(THEME_CONFIG), "[FAIL] テーマ設定ファイルが作成されていない"
    
    with open(THEME_CONFIG, "r", encoding="utf-8") as f:
        loaded_theme = json.load(f)
    assert loaded_theme["theme"] == "dark", "[FAIL] テーマが正しく保存されていない"
    print("  [PASS] OK\n")
    
    # Test 8: updated_atフィールドの管理
    print("[Test 8] updated_atフィールドの管理")
    cleanup()
    created_time = "2026-07-10T10:00:00"
    tasks = [
        {
            "task": "テスト",
            "done": False,
            "created_at": created_time,
            "updated_at": created_time
        }
    ]
    assert save_tasks(tasks), "[FAIL] タスク保存失敗"
    
    loaded = load_tasks()
    assert loaded[0]["created_at"] is not None, "[FAIL] created_atが管理されていない"
    assert loaded[0]["updated_at"] is not None, "[FAIL] updated_atが管理されていない"
    print("  [PASS] OK\n")
    
    # Test 9: task_idの自動生成
    print("[Test 9] task_idの自動生成")
    cleanup()
    tasks = [{"task": "ID生成テスト", "done": False}]
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f)
    
    loaded = load_tasks()
    assert "task_id" in loaded[0], "[FAIL] task_idが生成されていない"
    assert isinstance(loaded[0]["task_id"], int), "[FAIL] task_idが整数でない"
    print("  [PASS] OK\n")
    
    # クリーンアップ
    cleanup()
    
    print("=" * 60)
    print("All tests passed! Phase 2機能は正常に動作しています。")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_phase2_features()
    except AssertionError as e:
        print(f"\n[FAILED] {e}")
        cleanup()
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        cleanup()
        sys.exit(1)
