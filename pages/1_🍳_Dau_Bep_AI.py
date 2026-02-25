import streamlit as st
import google.generativeai as genai
from PIL import Image
from utils import require_login

st.set_page_config(page_title="Đầu Bếp VIP", page_icon="🍳", layout="wide")
require_login()

# CSS làm mượt giao diện chat giống Gemini
st.markdown("""
    <style>
    .stChatInput { padding-bottom: 20px; }
    .main { max-width: 900px; margin: 0 auto; }
    </style>
""", unsafe_allow_html=True)

st.title("✨ Gordon Rox - Trợ Lý Bếp Thông Minh")
st.caption("Trò chuyện trực tiếp với siêu đầu bếp. Tải ảnh lên nếu bạn cần phân tích món ăn.")

if "full_ai_session" not in st.session_state:
    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction="Bạn là siêu đầu bếp Gordon Rox. Trả lời chuyên nghiệp, trình bày đẹp bằng Markdown, xuống dòng rõ ràng.")
    st.session_state.full_ai_session = model.start_chat(history=[])
if "vip_chat" not in st.session_state:
    st.session_state.vip_chat = []

# Khu vực Upload ảnh được giấu gọn gàng
with st.expander("📎 Bấm vào đây để đính kèm hình ảnh món ăn / nguyên liệu"):
    img_file = st.file_uploader("Tải ảnh lên...", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    if img_file:
        img = Image.open(img_file)
        st.image(img, height=200)
        if st.button("🚀 Gửi ảnh này cho AI phân tích", type="primary"):
            with st.spinner("Đang nhìn ảnh..."):
                prompt = "Phân tích ảnh này và cho tôi biết công thức hoặc đánh giá của bạn."
                res = st.session_state.full_ai_session.send_message([prompt, img])
                st.session_state.vip_chat.append({"role": "user", "content": "📸 *[Đã gửi một hình ảnh]*"})
                st.session_state.vip_chat.append({"role": "assistant", "content": res.text})
                st.rerun()

st.divider()

# Khung Chat chính
for msg in st.session_state.vip_chat:
    icon = "🧑‍🍳" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=icon):
        st.markdown(msg["content"])
        
chat_text = st.chat_input("Nhập câu hỏi của bạn (VD: Trưa nay ăn gì?)...")
if chat_text:
    st.session_state.vip_chat.append({"role": "user", "content": chat_text})
    with st.chat_message("user", avatar="🧑‍🍳"): 
        st.markdown(chat_text)
        
    with st.chat_message("assistant", avatar="✨"):
        with st.spinner("Đang gõ..."):
            res = st.session_state.full_ai_session.send_message(chat_text)
            st.markdown(res.text)
            st.session_state.vip_chat.append({"role": "assistant", "content": res.text})