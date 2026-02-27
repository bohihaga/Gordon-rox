import streamlit as st
import google.generativeai as genai
from PIL import Image
from ui import apply_theme, render_sidebar # GỌI GIAO DIỆN CHUẨN VÀO ĐÂY

# 1. BẮT BUỘC ĐỂ ĐẦU TIÊN
st.set_page_config(page_title="Đầu Bếp VIP", page_icon="🍳", layout="wide", initial_sidebar_state="expanded")

# 2. ÁP DỤNG MÀU SẮC VÀ THANH MENU (Thay cho đống code dài ngoằng cũ)
apply_theme()
render_sidebar()

# 3. KIỂM TRA ĐĂNG NHẬP
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
        
        # Dùng width thay cho height
        st.image(img, width=400) 
        
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
            st.session_state.vip_chat.append({"role": "assistant", "content": res.text})
