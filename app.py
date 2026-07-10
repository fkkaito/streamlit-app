import streamlit as st
import json
import os
from typing import List, Dict
from datetime import datetime

# ページタイトルとアイコン設定
st.set_page_config(page_title="TODO App", page_icon="📝", layout="wide")

# 保存ファイルのパス
TODOS_FILE = "todos.json"

# セッション状態キー（一元管理）
SESSION_KEY_TASKS = "tasks"
SESSION_KEY_TASK_INPUT = "task_input"
SESSION_KEY_FILTER = "filter"
SESSION_KEY_PRIORITY_FILTER = "priority_filter"
SESSION_KEY_SEARCH = "search"


def load_tasks() -> List[Dict]:
    """ファイルからタスクを読み込む。エラー時は空リストを返す。"""
    try:
        if os.path.exists(TODOS_FILE):
            with open(TODOS_FILE, "r", encoding="utf-8") as f:
                tasks = json.load(f)
                # 後方互換性：優先度と期限フィールドを追加
                for task in tasks:
                    if "priority" not in task:
                        task["priority"] = "中"
                    if "due_date" not in task:
                        task["due_date"] = None
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


# ページレイアウト
st.title("📝 TODO アプリ（拡張版）")
st.markdown("---")

# タスク追加エリア
st.subheader("📌 新しいタスクを追加")
col1, col2, col3, col4 = st.columns([2, 1, 1, 0.8])

with col1:
    new_task = st.text_input(
        "タスク名",
        key=SESSION_KEY_TASK_INPUT,
        placeholder="やることを入力してください..."
    )

with col2:
    priority = st.selectbox(
        "優先度",
        ["高", "中", "低"],
        key="new_priority"
    )

with col3:
    due_date = st.date_input(
        "期限",
        value=None,
        key="new_due_date"
    )

with col4:
    add_button = st.button("追加", use_container_width=True)

# タスク追加処理（ボタンまたはEnter）
if add_button:
    if new_task.strip():
        st.session_state[SESSION_KEY_TASKS].append({
            "task": new_task.strip(),
            "done": False,
            "priority": priority,
            "due_date": due_date.isoformat() if due_date else None,
            "created_at": datetime.now().isoformat()
        })
        if save_tasks(st.session_state[SESSION_KEY_TASKS]):
            st.session_state[SESSION_KEY_TASK_INPUT] = ""
            st.rerun()
    else:
        st.warning("タスクを入力してください")

st.markdown("---")

# フィルター・検索エリア
st.subheader("🔍 フィルター・検索")
filter_col1, filter_col2, filter_col3, filter_col4 = st.columns([1, 1, 1, 1])

with filter_col1:
    filter_option = st.selectbox(
        "ステータス",
        ["すべて", "未完了", "完了"],
        key=SESSION_KEY_FILTER
    )

with filter_col2:
    priority_filter = st.selectbox(
        "優先度",
        ["すべて", "高", "中", "低"],
        key=SESSION_KEY_PRIORITY_FILTER
    )

with filter_col3:
    search_term = st.text_input(
        "キーワード検索",
        key=SESSION_KEY_SEARCH,
        placeholder="タスク名で検索..."
    )

with filter_col4:
    st.write("")  # スペーサー
    if st.button("完了タスク一括削除", help="完了したすべてのタスクを削除します"):
        st.session_state[SESSION_KEY_TASKS] = [
            task for task in st.session_state[SESSION_KEY_TASKS]
            if not task["done"]
        ]
        if save_tasks(st.session_state[SESSION_KEY_TASKS]):
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
            col1, col2, col3, col4, col5 = st.columns([0.5, 1, 2, 1.5, 0.5])
            
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
                    if save_tasks(st.session_state[SESSION_KEY_TASKS]):
                        st.rerun()
            
            with col2:
                # 優先度表示
                priority_icon = get_priority_icon(task.get("priority", "中"))
                st.markdown(priority_icon)
            
            with col3:
                # タスク表示（完了したら打ち消し線）
                if task["done"]:
                    st.markdown(f"~~{task['task']}~~")
                else:
                    st.text(task['task'])
            
            with col4:
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
            
            with col5:
                # 削除ボタン
                if st.button("🗑️", key=f"delete_{i}", help="タスクを削除"):
                    st.session_state[SESSION_KEY_TASKS].pop(i)
                    if save_tasks(st.session_state[SESSION_KEY_TASKS]):
                        st.rerun()
    else:
        st.info("💬 条件に合致するタスクがありません")
else:
    st.info("📭 タスクがまだありません。新しいタスクを追加してください！")

st.markdown("---")

# サイドバー
with st.sidebar:
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
    
    st.markdown("---")
    st.markdown("### 💾 データ操作")
    
    # エクスポート機能
    if st.button("📥 JSONでエクスポート"):
        export_data = export_tasks_json(st.session_state[SESSION_KEY_TASKS])
        st.download_button(
            label="📄 todos.json をダウンロード",
            data=export_data,
            file_name=f"todos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    st.markdown("---")
    st.markdown("### ℹ️ 使用方法")
    st.markdown("""
    - **優先度**: タスクの重要度を設定
    - **期限**: タスクの完了期日を設定
    - **検索**: タスク名でキーワード検索
    - **フィルター**: ステータスと優先度でフィルター
    - **一括削除**: 完了したタスクをまとめて削除
    - **エクスポート**: データをJSON形式で保存
    """)
