import streamlit as st
import base64
from io import BytesIO
from PIL import Image
import uuid
from utils import load_db, save_db, FORUM_DB
from datetime import datetime

st.set_page_config(page_title="Cộng Đồng", page_icon="🌍", layout="centered", initial_sidebar_state="expanded")

# CSS VÀ SIDEBAR KÈM ĐỊNH DẠNG MẠNG XÃ HỘI DARK MODE
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Playfair+Display:ital,wght@1,600&display=swap');
    body, p, h1, h2, h3, h4, h5, h6, span, div, input, textarea { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0f1115; color: #f8fafc; }
    header {visibility: hidden;}
    [data-testid="stSidebarNav"] { display: none !important; }
    [data-testid="stSidebar"] { background-color: #16181d; border-right: 1px solid #272a30; }
    .sidebar-logo { font-family: 'Playfair Display', serif !important; font-size: 2.2rem; color: #e2e8f0; margin-bottom: 25px; padding-left: 10px; font-style: italic; }
    
    /* Giao diện Bài Viết Mạng Xã Hội */
    .post-box { background: #16181d; padding: 25px; border-radius: 16px; margin-bottom: 25px; border: 1px solid #272a30; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
    .post-author { font-size: 1.1em; font-weight: 600; color: #f97316; }
    .post-time { font-size: 0.8em; color: #64748b; margin-bottom: 12px; }
    .post-content { font-size: 1.05em; margin-bottom: 15px; color: #e2e8f0; line-height: 1.6;}
    .comment-box { background-color: #1e2026; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid #f97316; color: #cbd5e1; }
    
    .stButton>button { border-radius: 8px; font-weight: 600; transition: all 0.2s; }
    .stButton>button:hover { border-color: #f97316 !important; color: #f97316 !important; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div class='sidebar-logo'>Gordon Rox</div>", unsafe_allow_html=True)
    st.page_link("app.py", label="Trang chủ", icon="🏠")
    st.page_link("pages/1_🍳_Dau_Bep_AI.py", label="Phân tích món ăn", icon="🍳")
    st.page_link("pages/2_❄️_Tu_Lanh.py", label="Quản lý Tủ lạnh", icon="❄️")
    st.page_link("pages/3_🌍_Dien_Dan.py", label="Mạng xã hội", icon="🌍")
    st.markdown("<div style='flex-grow: 1; min-height: 45vh;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        if st.session_state.get("logged_in"):
            st.markdown(f"<div style='font-weight: 600; font-size:1.1em; margin-bottom:10px;'>👤 {st.session_state.username}</div>", unsafe_allow_html=True)
            if st.button("🔴 Đăng Xuất", use_container_width=True):
                st.session_state.logged_in = False
                st.switch_page("app.py")
        else:
            st.markdown("<div style='color: #94a3b8; font-size: 0.9em; text-align: center; margin-bottom:10px;'>Bạn chưa đăng nhập</div>", unsafe_allow_html=True)
            if st.button("🔑 Sign In / Up", type="primary", use_container_width=True):
                st.session_state.auth_view = "login"
                st.switch_page("app.py")

if not st.session_state.get("logged_in"):
    st.markdown("<h2 style='text-align:center; color:#f97316; margin-top:15vh;'>🔒 CỘNG ĐỒNG KHÉP KÍN</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#94a3b8;'>Đăng nhập để xem hàng ngàn công thức từ cộng đồng Gordon Rox.</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        if st.button("🏠 Về Trang Chủ Đăng Nhập", use_container_width=True, type="primary"):
            st.session_state.auth_view = "login"
            st.switch_page("app.py")
    st.stop()

# ==========================================
def encode_image(uploaded_file):
    img = Image.open(uploaded_file)
    img.thumbnail((600, 600))
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

st.title("🌍 Mạng Xã Hội Ẩm Thực")
with st.expander("📝 TẠO BÀI VIẾT MỚI", expanded=True):
    with st.form("post_form", clear_on_submit=True):
        msg = st.text_area("Hôm nay bạn muốn khoe món gì?", height=100)
        img_upload = st.file_uploader("Đính kèm 1 tấm ảnh (Tùy chọn)", type=["jpg", "jpeg", "png"])
        if st.form_submit_button("🚀 Đăng Bài", type="primary"):
            if msg:
                posts = load_db(FORUM_DB)
                new_post = {
                    "id": str(uuid.uuid4()),
                    "name": st.session_state.username,
                    "time": datetime.now().strftime("%d/%m - %H:%M"),
                    "msg": msg,
                    "image": encode_image(img_upload) if img_upload else None,
                    "comments": []
                }
                posts.append(new_post)
                save_db(FORUM_DB, posts)
                st.success("Lên sóng thành công!")
                st.rerun()

st.divider()
posts = load_db(FORUM_DB)

for post_idx, post in enumerate(reversed(posts)):
    if isinstance(post, dict):
        post_id = post.get("id", f"old_{post_idx}")
        author = post.get("name", "Ẩn danh")
        time = post.get("time", "")
        content = post.get("msg", post.get("message", ""))
        img_b64 = post.get("image", None)
        comments = post.get("comments", [])
        
        st.markdown(f"""
            <div class="post-box">
                <div class="post-author">🧑‍🍳 @{author}</div>
                <div class="post-time">🕒 {time}</div>
                <div class="post-content">{content}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if img_b64:
            try:
                img_data = base64.b64decode(img_b64)
                st.image(Image.open(BytesIO(img_data)), use_column_width=True)
            except: pass
        
        with st.expander(f"💬 Bình luận ({len(comments)})"):
            for cmt in comments:
                st.markdown(f"<div class='comment-box'><b style='color:white;'>@{cmt['name']}</b>: {cmt['text']}</div>", unsafe_allow_html=True)
            
            col_cmt, col_btn = st.columns([4, 1])
            new_cmt = col_cmt.text_input("Viết bình luận...", key=f"input_{post_id}", label_visibility="collapsed")
            if col_btn.button("Gửi", key=f"btn_{post_id}"):
                if new_cmt:
                    actual_index = len(posts) - 1 - post_idx
                    if "comments" not in posts[actual_index]: posts[actual_index]["comments"] = []
                    posts[actual_index]["comments"].append({"name": st.session_state.username, "text": new_cmt})
                    save_db(FORUM_DB, posts)
                    st.rerun()
        st.write("<br>", unsafe_allow_html=True)
