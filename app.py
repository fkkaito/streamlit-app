import streamlit as st
import json
import os

# ページタイトルとアイコン設定
st.set_page_config(page_title="TODO App", page_icon="📝")

# 保存ファイルのパス
TODOS_FILE = "todos.json"

# セッション状態の初期化
if "tasks" not in st.session_state:
    if os.path.exists(TODOS_FILE):
        with open(TODOS_FILE, "r", encoding="utf-8") as f:
            st.session_state.tasks = json.load(f)
    else:
        st.session_state.tasks = []

if "new_task" not in st.session_state:
    st.session_state.new_task = ""

# タスクをJSONファイルに保存
def save_tasks():
    with open(TODOS_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.tasks, f, ensure_ascii=False, indent=2)

# ページレイアウト
st.title("📝 TODO アプリ")
st.markdown("---")

# タスク入力エリア
col1, col2 = st.columns([4, 1])

with col1:
    new_task = st.text_input(
        "新しいタスクを入力",
        key="task_input",
        placeholder="やることを入力してください..."
    )

with col2:
    if st.button("追加", key="add_button"):
        if new_task.strip():
            st.session_state.tasks.append({
                "task": new_task,
                "done": False
            })
            save_tasks()
            st.session_state.task_input = ""
            st.rerun()

st.markdown("---")

# フィルター機能
filter_option = st.selectbox(
    "タスク表示フィルター",
    ["すべて", "未完了", "完了"],
    key="filter"
)

# タスク一覧表示
if st.session_state.tasks:
    st.subheader("タスク一覧")
    
    for i, task in enumerate(st.session_state.tasks):
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
                st.session_state.tasks[i]["done"] = done
                save_tasks()
                st.rerun()
        
        with col2:
            # タスク表示（完了したら打ち消し線）
            if task["done"]:
                st.markdown(f"~~{task['task']}~~")
            else:
                st.text(task['task'])
        
        with col3:
            # 削除ボタン
            if st.button("🗑️", key=f"delete_{i}"):
                st.session_state.tasks.pop(i)
                save_tasks()
                st.rerun()
else:
    st.info("📭 タスクがまだありません。新しいタスクを追加してください！")

# サイドバーに統計情報
st.sidebar.markdown("### 📊 統計情報")
total_tasks = len(st.session_state.tasks)
completed_tasks = sum(1 for task in st.session_state.tasks if task["done"])
pending_tasks = total_tasks - completed_tasks

st.sidebar.metric("総タスク数", total_tasks)
st.sidebar.metric("完了", completed_tasks)
st.sidebar.metric("未完了", pending_tasks)

if total_tasks > 0:
    progress = completed_tasks / total_tasks
    st.sidebar.progress(progress, text=f"{int(progress*100)}% 完了")
