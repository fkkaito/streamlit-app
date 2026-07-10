import streamlit as st
import json
import os
import shutil
from typing import List, Dict
from datetime import datetime
from pathlib import Path

# ページタイトルとアイコン設定
st.set_page_config(page_title="TODO App", page_icon="📝", layout="wide")

# 保存ファイルのパス
TODOS_FILE = "todos.json"
BACKUP_DIR = "backups"
THEME_CONFIG = "theme_config.json"

# セッション状態キー（一元管理）
SESSION_KEY_TASKS = "tasks"
SESSION_KEY_TASK_INPUT = "task_input"
SESSION_KEY_FILTER = "filter"
SESSION_KEY_PRIORITY_FILTER = "priority_filter"
SESSION_KEY_SEARCH = "search"
SESSION_KEY_CATEGORY_FILTER = "category_filter"
SESSION_KEY_THEME = "theme"
SESSION_KEY_EDIT_MODE = "edit_mode"
SESSION_KEY_EDIT_ID = "edit_id"


def create_backup_dir():
    """バックアップディレクトリを作成。"""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)


def load_tasks() -> List[Dict]:
    """ファイルからタスクを読み込む。エラー時は空リストを返す。"""
    try:
        if os.path.exists(TODOS_FILE):
            with open(TODOS_FILE, "r", encoding="utf-8") as f:
                tasks = json.load(f)
                # 後方互換性：新フィールドを追加
                for task in tasks:
                    if "priority" not in task:
                        task["priority"] = "中"
                    if "due_date" not in task:
                        task["due_date"] = None
                    if "category" not in task:
                        task["category"] = "その他"
                    if "created_at" not in task:
                        task["created_at"] = datetime.now().isoformat()
                    if "updated_at" not in task:
                        task["updated_at"] = datetime.now().isoformat()
                    if "task_id" not in task:
                        task["task_id"] = hash(task.get("task", "")) % 10000
                return tasks
    except (json.JSONDecodeError, IOError) as e:
        st.error(f"⚠️ データ読込エラー: {e}")
    return []


def save_tasks(tasks: List[Dict]) -> bool:
    """タスクをJSONファイルに保存。成功時Trueを返す。"""
    try:
        with open(TODOS_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        st.error(f"⚠️ データ保存エラー: {e}")
        return False


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


def get_priority_icon(priority: str) -> str:
    """優先度アイコンを取得。"""
    priority_icons = {
        "高": "🔴",
        "中": "🟡",
        "低": "🟢"
    }
    return priority_icons.get(priority, "🟡")


def load_theme_config() -> Dict:
    """テーマ設定を読み込む。"""
    if os.path.exists(THEME_CONFIG):
        try:
            with open(THEME_CONFIG, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"theme": "light", "color_primary": "#FF6B6B"}


def save_theme_config(theme: Dict) -> bool:
    """テーマ設定を保存。"""
    try:
        with open(THEME_CONFIG, "w", encoding="utf-8") as f:
            json.dump(theme, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False


# セッション状態の初期化
if SESSION_KEY_TASKS not in st.session_state:
    st.session_state[SESSION_KEY_TASKS] = load_tasks()

if SESSION_KEY_TASK_INPUT not in st.session_state:
    st.session_state[SESSION_KEY_TASK_INPUT] = ""

if SESSION_KEY_FILTER not in st.session_state:
    st.session_state[SESSION_KEY_FILTER] = "すべて"

if SESSION_KEY_PRIORITY_FILTER not in st.session_state:
    st.session_state[SESSION_KEY_PRIORITY_FILTER] = "すべて"

if SESSION_KEY_SEARCH not in st.session_state:
    st.session_state[SESSION_KEY_SEARCH] = ""

if SESSION_KEY_CATEGORY_FILTER not in st.session_state:
    st.session_state[SESSION_KEY_CATEGORY_FILTER] = "すべて"

if SESSION_KEY_THEME not in st.session_state:
    st.session_state[SESSION_KEY_THEME] = load_theme_config()

if SESSION_KEY_EDIT_MODE not in st.session_state:
    st.session_state[SESSION_KEY_EDIT_MODE] = False

if SESSION_KEY_EDIT_ID not in st.session_state:
    st.session_state[SESSION_KEY_EDIT_ID] = None


# ページレイアウト
st.title("📝 TODO アプリ（フル機能版）")
st.markdown("---")

# サイドバー：テーマ設定
with st.sidebar:
    st.markdown("### 🎨 テーマ設定")
    theme_choice = st.selectbox(
        "テーマを選択",
        ["light", "dark"],
        key="theme_selector"
    )
    
    if theme_choice == "dark":
        st.markdown(
            """
            <style>
                .stApp {
                    background-color: #0e1117;
                    color: #c9d1d9;
                }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.session_state[SESSION_KEY_THEME] = {"theme": "dark"}
        save_theme_config({"theme": "dark"})
    else:
        st.session_state[SESSION_KEY_THEME] = {"theme": "light"}
        save_theme_config({"theme": "light"})

# タスク追加・編集エリア
st.subheader("📌 タスク管理")
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    if st.session_state[SESSION_KEY_EDIT_MODE]:
        st.write("🔧 編集モード")
    new_task = st.text_input(
        "タスク名",
        key=SESSION_KEY_TASK_INPUT,
        placeholder="やることを入力してください..."
    )

with col2:
    category = st.selectbox(
        "カテゴリ",
        ["仕事", "プライベート", "学習", "健康", "その他"],
        key="new_category"
    )

with col3:
    priority = st.selectbox(
        "優先度",
        ["高", "中", "低"],
        key="new_priority"
    )

col4, col5, col6 = st.columns([1, 1, 1])

with col4:
    due_date = st.date_input(
        "期限",
        value=None,
        key="new_due_date"
    )

with col5:
    if st.session_state[SESSION_KEY_EDIT_MODE]:
        if st.button("✓ 更新", use_container_width=True):
            if new_task.strip() and st.session_state[SESSION_KEY_EDIT_ID] is not None:
                for i, task in enumerate(st.session_state[SESSION_KEY_TASKS]):
                    if task.get("task_id") == st.session_state[SESSION_KEY_EDIT_ID]:
                        st.session_state[SESSION_KEY_TASKS][i].update({
                            "task": new_task.strip(),
                            "category": category,
                            "priority": priority,
                            "due_date": due_date.isoformat() if due_date else None,
                            "updated_at": datetime.now().isoformat()
                        })
                        if save_tasks(st.session_state[SESSION_KEY_TASKS]):
                            auto_backup_tasks(st.session_state[SESSION_KEY_TASKS])
                            st.session_state[SESSION_KEY_EDIT_MODE] = False
                            st.session_state[SESSION_KEY_EDIT_ID] = None
                            st.session_state[SESSION_KEY_TASK_INPUT] = ""
                            st.success("✅ タスクを更新しました")
                            st.rerun()
    else:
        if st.button("➕ 追加", use_container_width=True):
            if new_task.strip():
                st.session_state[SESSION_KEY_TASKS].append({
                    "task": new_task.strip(),
                    "done": False,
                    "priority": priority,
                    "category": category,
                    "due_date": due_date.isoformat() if due_date else None,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                    "task_id": hash(new_task.strip() + str(datetime.now())) % 100000
                })
                if save_tasks(st.session_state[SESSION_KEY_TASKS]):
                    auto_backup_tasks(st.session_state[SESSION_KEY_TASKS])
                    st.session_state[SESSION_KEY_TASK_INPUT] = ""
                    st.success("✅ タスクを追加しました")
                    st.rerun()
            else:
                st.warning("タスクを入力してください")

with col6:
    if st.session_state[SESSION_KEY_EDIT_MODE]:
        if st.button("✕ キャンセル", use_container_width=True):
            st.session_state[SESSION_KEY_EDIT_MODE] = False
            st.session_state[SESSION_KEY_EDIT_ID] = None
            st.session_state[SESSION_KEY_TASK_INPUT] = ""
            st.rerun()

st.markdown("---")

# フィルター・検索エリア
st.subheader("🔍 フィルター・検索")
filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns(5)

with filter_col1:
    filter_option = st.selectbox(
        "ステータス",
        ["すべて", "未完了", "完了"],
        key=SESSION_KEY_FILTER
    )

with filter_col2:
    category_filter = st.selectbox(
        "カテゴリ",
        ["すべて", "仕事", "プライベート", "学習", "健康", "その他"],
        key=SESSION_KEY_CATEGORY_FILTER
    )

with filter_col3:
    priority_filter = st.selectbox(
        "優先度",
        ["すべて", "高", "中", "低"],
        key=SESSION_KEY_PRIORITY_FILTER
    )

with filter_col4:
    search_term = st.text_input(
        "キーワード検索",
        key=SESSION_KEY_SEARCH,
        placeholder="検索..."
    )

with filter_col5:
    if st.button("🗑️ 完了タスク削除", help="完了したすべてのタスクを削除"):
        st.session_state[SESSION_KEY_TASKS] = [
            task for task in st.session_state[SESSION_KEY_TASKS]
            if not task["done"]
        ]
        if save_tasks(st.session_state[SESSION_KEY_TASKS]):
            auto_backup_tasks(st.session_state[SESSION_KEY_TASKS])
            st.success("✅ 完了したタスクを削除しました")
            st.rerun()

st.markdown("---")

# タスク一覧表示
st.subheader("📋 タスク一覧")

if st.session_state[SESSION_KEY_TASKS]:
    # フィルター適用
    filtered_tasks = []
    for i, task in enumerate(st.session_state[SESSION_KEY_TASKS]):
        # ステータスフィルター
        if filter_option == "完了" and not task["done"]:
            continue
        if filter_option == "未完了" and task["done"]:
            continue
        
        # カテゴリフィルター
        if category_filter != "すべて" and task.get("category", "その他") != category_filter:
            continue
        
        # 優先度フィルター
        if priority_filter != "すべて" and task.get("priority", "中") != priority_filter:
            continue
        
        # キーワード検索
        if search_term and search_term.lower() not in task["task"].lower():
            continue
        
        filtered_tasks.append((i, task))
    
    if filtered_tasks:
        # 優先度でソート（高 > 中 > 低）
        priority_order = {"高": 0, "中": 1, "低": 2}
        filtered_tasks.sort(key=lambda x: priority_order.get(x[1].get("priority", "中"), 1))
        
        for i, task in filtered_tasks:
            col1, col2, col3, col4, col5, col6, col7 = st.columns([0.5, 1, 0.8, 2, 1.2, 0.8, 0.5])
            
            with col1:
                # チェックボックス
                done = st.checkbox(
                    "完了",
                    value=task["done"],
                    key=f"checkbox_{i}",
                    label_visibility="collapsed"
                )
                if done != task["done"]:
                    st.session_state[SESSION_KEY_TASKS][i]["done"] = done
                    st.session_state[SESSION_KEY_TASKS][i]["updated_at"] = datetime.now().isoformat()
                    if save_tasks(st.session_state[SESSION_KEY_TASKS]):
                        auto_backup_tasks(st.session_state[SESSION_KEY_TASKS])
                        st.rerun()
            
            with col2:
                # 優先度表示
                priority_icon = get_priority_icon(task.get("priority", "中"))
                st.markdown(priority_icon)
            
            with col3:
                # カテゴリ表示
                category_icon = get_category_icon(task.get("category", "その他"))
                st.markdown(category_icon)
            
            with col4:
                # タスク表示（完了したら打ち消し線）
                if task["done"]:
                    st.markdown(f"~~{task['task']}~~")
                else:
                    st.text(task['task'])
            
            with col5:
                # 期限表示
                due_date_str = task.get("due_date")
                if due_date_str:
                    due_date_obj = datetime.fromisoformat(due_date_str).date()
                    today = datetime.now().date()
                    if due_date_obj < today and not task["done"]:
                        st.markdown(f"🔴 {due_date_obj}")
                    elif due_date_obj == today:
                        st.markdown(f"🟡 {due_date_obj}")
                    else:
                        st.markdown(f"⏰ {due_date_obj}")
                else:
                    st.write("-")
            
            with col6:
                # 編集ボタン
                if st.button("✏️", key=f"edit_{i}", help="タスクを編集"):
                    st.session_state[SESSION_KEY_EDIT_MODE] = True
                    st.session_state[SESSION_KEY_EDIT_ID] = task.get("task_id")
                    st.session_state[SESSION_KEY_TASK_INPUT] = task["task"]
                    st.rerun()
            
            with col7:
                # 削除ボタン
                if st.button("🗑️", key=f"delete_{i}", help="タスクを削除"):
                    st.session_state[SESSION_KEY_TASKS].pop(i)
                    if save_tasks(st.session_state[SESSION_KEY_TASKS]):
                        auto_backup_tasks(st.session_state[SESSION_KEY_TASKS])
                        st.rerun()
    else:
        st.info("💬 条件に合致するタスクがありません")
else:
    st.info("📭 タスクがまだありません。新しいタスクを追加してください！")

st.markdown("---")

# サイドバー：統計情報
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📊 統計情報")
    total_tasks = len(st.session_state[SESSION_KEY_TASKS])
    completed_tasks = sum(1 for task in st.session_state[SESSION_KEY_TASKS] if task["done"])
    pending_tasks = total_tasks - completed_tasks
    
    st.metric("総タスク数", total_tasks)
    st.metric("完了", completed_tasks)
    st.metric("未完了", pending_tasks)
    
    if total_tasks > 0:
        progress = completed_tasks / total_tasks
        st.progress(progress, text=f"{int(progress*100)}% 完了")
    
    # カテゴリ別統計
    st.markdown("#### カテゴリ別")
    categories = {}
    for task in st.session_state[SESSION_KEY_TASKS]:
        cat = task.get("category", "その他")
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in sorted(categories.items()):
        icon = get_category_icon(cat)
        st.write(f"{icon} {cat}: {count}個")
    
    # バックアップ情報
    st.markdown("---")
    st.markdown("### 💾 バックアップ")
    create_backup_dir()
    backups = sorted(os.listdir(BACKUP_DIR)) if os.path.exists(BACKUP_DIR) else []
    st.write(f"バックアップ数: {len(backups)}")
    
    if backups and len(backups) > 0:
        st.write(f"最新: {backups[-1]}")
    
    if st.button("🔄 手動バックアップ"):
        if auto_backup_tasks(st.session_state[SESSION_KEY_TASKS]):
            st.success("✅ バックアップを作成しました")
        else:
            st.error("❌ バックアップ作成に失敗しました")
    
    # ヘルプ
    st.markdown("---")
    st.markdown("### ℹ️ 使用方法")
    st.markdown("""
    **タスク管理**
    - ✏️: タスクを編集
    - 🗑️: タスクを削除
    - ✓: ステータスを更新
    
    **フィルター**
    - ステータス: すべて/未完了/完了
    - カテゴリ: 仕事/プライベート/学習/健康/その他
    - 優先度: 高/中/低
    - キーワード検索
    
    **バックアップ**
    - 自動: タスク操作時
    - 手動: サイドバーから実行
    """)
