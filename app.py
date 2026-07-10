import streamlit as st
import json
import os
from typing import List, Dict

# ページタイトルとアイコン設定
st.set_page_config(page_title="TODO App", page_icon="📝")

# 保存ファイルのパス
TODOS_FILE = "todos.json"

# セッション状態キー（一元管理）
SESSION_KEY_TASKS = "tasks"
SESSION_KEY_TASK_INPUT = "task_input"
SESSION_KEY_FILTER = "filter"


def load_tasks() -> List[Dict]:
    """ファイルからタスクを読み込む。エラー時は空リストを返す。"""
    try:
        if os.path.exists(TODOS_FILE):
            with open(TODOS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
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


# セッション状態の初期化
if SESSION_KEY_TASKS not in st.session_state:
    st.session_state[SESSION_KEY_TASKS] = load_tasks()

if SESSION_KEY_TASK_INPUT not in st.session_state:
    st.session_state[SESSION_KEY_TASK_INPUT] = ""

if SESSION_KEY_FILTER not in st.session_state:
    st.session_state[SESSION_KEY_FILTER] = "すべて"

# ページレイアウト
st.title("📝 TODO アプリ")
st.markdown("---")

# タスク入力エリア
col1, col2 = st.columns([4, 1])

with col1:
    new_task = st.text_input(
        "新しいタスクを入力",
        key=SESSION_KEY_TASK_INPUT,
        placeholder="やることを入力してください..."
    )

with col2:
    if st.button("追加", key="add_button", use_container_width=True):
        if new_task.strip():
            # セッション状態にタスクを追加
            st.session_state[SESSION_KEY_TASKS].append({
                "task": new_task.strip(),
                "done": False
            })
            # ファイルに保存
            if save_tasks(st.session_state[SESSION_KEY_TASKS]):
                # 入力欄をクリア
                st.session_state[SESSION_KEY_TASK_INPUT] = ""
                # UI を再描画
                st.rerun()
        else:
            st.warning("タスクを入力してください")

st.markdown("---")

# フィルター機能
filter_option = st.selectbox(
    "タスク表示フィルター",
    ["すべて", "未完了", "完了"],
    key=SESSION_KEY_FILTER
)

# タスク一覧表示
if st.session_state[SESSION_KEY_TASKS]:
    st.subheader("タスク一覧")
    
    for i, task in enumerate(st.session_state[SESSION_KEY_TASKS]):
        # フィルター適用
        if filter_option == "完了" and not task["done"]:
            continue
        if filter_option == "未完了" and task["done"]:
            continue
        
        col1, col2, col3 = st.columns([1, 4, 0.5])
        
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
            # タスク表示（完了したら打ち消し線）
            if task["done"]:
                st.markdown(f"~~{task['task']}~~")
            else:
                st.text(task['task'])
        
        with col3:
            # 削除ボタン
            if st.button("🗑️", key=f"delete_{i}", help="タスクを削除"):
                st.session_state[SESSION_KEY_TASKS].pop(i)
                if save_tasks(st.session_state[SESSION_KEY_TASKS]):
                    st.rerun()
else:
    st.info("📭 タスクがまだありません。新しいタスクを追加してください！")

# サイドバーに統計情報
st.sidebar.markdown("### 📊 統計情報")
total_tasks = len(st.session_state[SESSION_KEY_TASKS])
completed_tasks = sum(1 for task in st.session_state[SESSION_KEY_TASKS] if task["done"])
pending_tasks = total_tasks - completed_tasks

st.sidebar.metric("総タスク数", total_tasks)
st.sidebar.metric("完了", completed_tasks)
st.sidebar.metric("未完了", pending_tasks)

if total_tasks > 0:
    progress = completed_tasks / total_tasks
    st.sidebar.progress(progress, text=f"{int(progress*100)}% 完了")
