import streamlit as st
from utils import require_login, load_db, save_db, FORUM_DB
from datetime import datetime

st.set_page_config(page_title="Cộng Đồng", page_icon="🌍")
require_login()

st.title("🌍 Bảng Tin Đầu Bếp")
st.write(f"Bạn đang đăng bài với tư cách: **{st.session_state.username}**")

with st.form("post_form"):
    msg = st.text_area("Bạn nấu món gì hôm nay?")
    if st.form_submit_button("📢 Đăng bài"):
        if msg:
            posts = load_db(FORUM_DB)
            posts.append({
                "name": st.session_state.username,
                "time": datetime.now().strftime("%d/%m - %H:%M"),
                "msg": msg
            })
            save_db(FORUM_DB, posts)
            st.success("Đã đăng!")
            st.rerun()

st.divider()
posts = load_db(FORUM_DB)
for post in reversed(posts):
    with st.container(border=True):
        st.markdown(f"**🧑‍🍳 @{post['name']}** *(lúc {post['time']})*")
        st.write(post['msg'])