import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. BẮT BUỘC ĐỂ ĐẦU TIÊN
st.set_page_config(page_title="Đầu Bếp VIP", page_icon="🍳", layout="wide", initial_sidebar_state="expanded")

# 2. CSS CHUẨN VENICE (Copy từ app.py sang)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Playfair+Display:ital,wght@1,600&display=swap');
    body, p, h1, h2, h3, h4, h5, h6, span, div, input, textarea { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0f1115; color: #f8fafc; }
    header {visibility: hidden;}
    [data-testid="stSidebarNav"] { display: none !important; }
    [data-testid="stSidebar"] { background-color: #16181d; border-right: 1px solid #272a30; }
    .sidebar-logo { font-family: 'Playfair Display', serif !important; font-size: 2.2rem; color: #e2e8f0; margin-bottom: 25px; padding-left: 10px; font-style: italic; }
    .stChatInput { background-color: transparent !important; padding-bottom: 20px; }
    .stChatInputContainer { background-color: #1e2026 !important; border: 1px solid #333842 !important; border-radius: 16px !important; }
    .stChatInputContainer:focus-within { border-color: #f97316 !important; }
    .stChatInputContainer textarea { color: #f8fafc !important; }
    .stButton>button { border-radius: 8px; font-weight: 600; transition: all 0.2s; }
    .stButton>button:hover { border-color: #f97316 !important; color: #f97316 !important; }
    </style>
""", unsafe_allow_html=True)

# 3. SIDEBAR XỊN
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

# 4. KIỂM TRA ĐĂNG NHẬP (Giao diện đẹp thay vì cảnh báo vàng)
if not st.session_state.get("logged_in"):
    st.markdown("<h2 style='text-align:center; color:#f97316; margin-top:15vh;'>🔒 TÍNH NĂNG V.I.P</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#94a3b8;'>Bạn cần Đăng Nhập để sử dụng AI phân tích hình ảnh.</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        if st.button("🏠 Về Trang Chủ", use_container_width=True, type="primary"):
            st.session_state.auth_view = "login"
            st.switch_page("app.py")
    st.stop()

# ==========================================
# GIAO DIỆN CHÍNH CỦA TRANG
# ==========================================
st.title("📸 Đầu Bếp Thị Giác AI")
st.caption("Tải hình ảnh nguyên liệu hoặc món ăn lên đây, Gordon Rox sẽ phân tích cho bạn.")

if "full_ai_session" not in st.session_state:
    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction="Bạn là siêu đầu bếp Gordon Rox. Trả lời chuyên nghiệp, trình bày đẹp bằng Markdown.")
    st.session_state.full_ai_session = model.start_chat(history=[])
if "vip_chat" not in st.session_state:
    st.session_state.vip_chat = []

with st.expander("📎 Bấm vào đây để đính kèm hình ảnh (JPG, PNG)"):
    img_file = st.file_uploader("Tải ảnh lên...", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    if img_file:
        img = Image.open(img_file)
        st.image(img, height=200)
        if st.button("🚀 Phân tích ảnh này", type="primary"):
            with st.spinner("Đang phân tích..."):
                prompt = "Phân tích ảnh này và cho tôi biết công thức hoặc đánh giá của bạn."
                res = st.session_state.full_ai_session.send_message([prompt, img])
                st.session_state.vip_chat.append({"role": "user", "content": "📸 *[Đã gửi một hình ảnh]*"})
                st.session_state.vip_chat.append({"role": "assistant", "content": res.text})
                st.rerun()

st.divider()

for msg in st.session_state.vip_chat:
    icon = "🧑‍🍳" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=icon):
        st.markdown(msg["content"])
        
chat_text = st.chat_input("Nhập câu hỏi chi tiết về món ăn...")
if chat_text:
    st.session_state.vip_chat.append({"role": "user", "content": chat_text})
    with st.chat_message("user", avatar="🧑‍🍳"): st.markdown(chat_text)
    with st.chat_message("assistant", avatar="✨"):
        with st.spinner("Đang gõ..."):
            res = st.session_state.full_ai_session.send_message(chat_text)
            st.markdown(res.text)
            st.session_state.vip_chat.append({"role": "assistant", "content": res.text})text})
