import streamlit as st
from utils import require_login, load_db, save_db, FORUM_DB
from datetime import datetime

st.set_page_config(page_title="Cộng Đồng", page_icon="🌍")
require_login()

st.title("🌍 Bảng Tin Đầu Bếp")
st.write(f"Bạn đang đăng bài với tư cách: **{st.session_state.username}**")

# clear_on_submit=True giúp tự động xóa chữ sau khi bấm đăng bài
with st.form("post_form", clear_on_submit=True):
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

# Hiển thị bài viết từ mới nhất đến cũ nhất
for post in reversed(posts):
    with st.container(border=True):
        # Dùng .get() để tránh lỗi nếu thiếu dữ liệu
        st.markdown(f"**🧑‍🍳 @{post.get('name', 'Ẩn danh')}** *(lúc {post.get('time', '')})*")
        
        # Lấy nội dung: nếu không có 'msg' thì tìm 'message' (hỗ trợ bài viết cũ)
        noi_dung = post.get('msg', post.get('message', ''))
        st.write(noi_dung)