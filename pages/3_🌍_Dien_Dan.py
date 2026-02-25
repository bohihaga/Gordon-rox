import streamlit as st
import base64
from io import BytesIO
from PIL import Image
import uuid
from utils import require_login, load_db, save_db, FORUM_DB
from datetime import datetime

st.set_page_config(page_title="Cộng Đồng", page_icon="🌍", layout="centered")
require_login()

# CSS làm đẹp bài đăng
st.markdown("""
    <style>
    .post-box { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); margin-bottom: 25px; border: 1px solid #f0f0f0; }
    .post-author { font-size: 1.1em; font-weight: bold; color: #ff7e5f; }
    .post-time { font-size: 0.8em; color: gray; margin-bottom: 10px; }
    .post-content { font-size: 1.05em; margin-bottom: 15px; color: #333; }
    .comment-box { background-color: #f9f9f9; padding: 10px; border-radius: 8px; margin-bottom: 5px; border-left: 3px solid #ddd; }
    </style>
""", unsafe_allow_html=True)

st.title("🌍 Mạng Xã Hội Ẩm Thực")
st.write(f"Tài khoản: **@{st.session_state.username}**")

# Hàm mã hóa ảnh để lưu vào JSON
def encode_image(uploaded_file):
    img = Image.open(uploaded_file)
    img.thumbnail((600, 600)) # Thu nhỏ ảnh để web không bị nặng
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

# KHU VỰC ĐĂNG BÀI MỚI
with st.expander("📝 TẠO BÀI VIẾT MỚI", expanded=True):
    with st.form("post_form", clear_on_submit=True):
        msg = st.text_area("Hôm nay bạn muốn khoe món gì?", height=100)
        img_upload = st.file_uploader("Đính kèm 1 tấm ảnh (Tùy chọn)", type=["jpg", "jpeg", "png"])
        
        if st.form_submit_button("🚀 Đăng Bài", type="primary"):
            if msg:
                posts = load_db(FORUM_DB)
                new_post = {
                    "id": str(uuid.uuid4()), # ID ngẫu nhiên cho bài viết
                    "name": st.session_state.username,
                    "time": datetime.now().strftime("%d/%m - %H:%M"),
                    "msg": msg,
                    "image": encode_image(img_upload) if img_upload else None,
                    "comments": [] # Danh sách bình luận
                }
                posts.append(new_post)
                save_db(FORUM_DB, posts)
                st.success("Lên sóng thành công!")
                st.rerun()

st.divider()
posts = load_db(FORUM_DB)

# HIỂN THỊ FEED BÀI VIẾT (Từ mới nhất đến cũ nhất)
for post_idx, post in enumerate(reversed(posts)):
    # Đảm bảo bài viết cũ không bị lỗi nếu thiếu key
    if isinstance(post, dict):
        post_id = post.get("id", f"old_{post_idx}")
        author = post.get("name", "Ẩn danh")
        time = post.get("time", "")
        content = post.get("msg", post.get("message", ""))
        img_b64 = post.get("image", None)
        comments = post.get("comments", [])
        
        # Bắt đầu vẽ UI cho Bài viết
        st.markdown(f"""
            <div class="post-box">
                <div class="post-author">🧑‍🍳 @{author}</div>
                <div class="post-time">🕒 {time}</div>
                <div class="post-content">{content}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Hiển thị ảnh nếu có
        if img_b64:
            try:
                img_data = base64.b64decode(img_b64)
                st.image(Image.open(BytesIO(img_data)), use_column_width=True)
            except: pass
        
        # Khu vực Bình luận
        with st.expander(f"💬 Bình luận ({len(comments)})"):
            # In danh sách bình luận
            for cmt in comments:
                st.markdown(f"<div class='comment-box'><b>@{cmt['name']}</b>: {cmt['text']}</div>", unsafe_allow_html=True)
            
            # Khung nhập bình luận mới
            col_cmt, col_btn = st.columns([4, 1])
            new_cmt = col_cmt.text_input("Viết bình luận...", key=f"input_{post_id}", label_visibility="collapsed")
            if col_btn.button("Gửi", key=f"btn_{post_id}"):
                if new_cmt:
                    # Cập nhật DB
                    actual_index = len(posts) - 1 - post_idx # Tìm đúng vị trí bài trong mảng gốc
                    if "comments" not in posts[actual_index]:
                        posts[actual_index]["comments"] = []
                        
                    posts[actual_index]["comments"].append({
                        "name": st.session_state.username,
                        "text": new_cmt
                    })
                    save_db(FORUM_DB, posts)
                    st.rerun()
        st.write("---")