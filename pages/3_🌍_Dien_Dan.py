import streamlit as st
from utils import require_login, load_db, save_db, FORUM_DB
from datetime import datetime

st.set_page_config(page_title="Cộng Đồng", page_icon="🌍")
require_login()

st.title("🌍 Bảng Tin Đầu Bếp")
st.write(f"Bạn đang đăng bài với tư cách: **{st.session_state.username}**")

# Xóa nội dung khung chat sau khi đăng bài
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
        # 🛠️ KIỂM TRA KIỂU DỮ LIỆU ĐỂ CHỐNG LỖI 🛠️
        if isinstance(post, dict):
            # 1. Nếu là cấu trúc xịn (Có Tên, Giờ, Nội dung)
            st.markdown(f"**🧑‍🍳 @{post.get('name', 'Ẩn danh')}** *(lúc {post.get('time', '')})*")
            noi_dung = post.get('msg', post.get('message', ''))
            st.write(noi_dung)
        else:
            # 2. Nếu là cấu trúc đồ cổ (Chỉ có mỗi dòng chữ)
            st.markdown("**🧑‍🍳 @Khách_ẩn_danh** *(Bài viết cũ)*")
            st.write(post)