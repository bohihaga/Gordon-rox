import streamlit as st
import google.generativeai as genai
from PIL import Image
from utils import require_login

st.set_page_config(page_title="Đầu Bếp VIP", page_icon="🍳", layout="wide")
require_login() # KIỂM TRA ĐĂNG NHẬP NGAY LẬP TỨC

st.title("🍳 Không Gian Bếp V.I.P")
st.markdown("Đặc quyền của bạn: Upload hình ảnh nguyên liệu, AI sẽ phân tích và ghi nhớ cuộc hội thoại.")

if "full_ai_session" not in st.session_state:
    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction="Bạn là siêu đầu bếp Gordon Rox phục vụ khách VIP. Hãy gọi khách bằng tên của họ.")
    st.session_state.full_ai_session = model.start_chat(history=[])
if "vip_chat" not in st.session_state:
    st.session_state.vip_chat = []

col1, col2 = st.columns([1, 2])
with col1:
    img_file = st.file_uploader("📸 Tải ảnh tủ lạnh/nguyên liệu", type=["png", "jpg", "jpeg"])
    img = Image.open(img_file) if img_file else None
    if img: st.image(img, use_column_width=True)

with col2:
    if st.button("🚀 Yêu Cầu AI Phân Tích Ảnh Này", type="primary"):
        if not img: st.error("Bạn chưa tải ảnh!")
        else:
            with st.spinner("Gordon Rox đang soi ảnh..."):
                prompt = "Hãy nhìn ảnh này và lên thực đơn chi tiết cho tôi."
                res = st.session_state.full_ai_session.send_message([prompt, img])
                st.session_state.vip_chat.append({"role": "user", "content": "[Đã gửi ảnh đính kèm]"})
                st.session_state.vip_chat.append({"role": "assistant", "content": res.text})
                
    st.divider()
    for msg in st.session_state.vip_chat:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
        
    chat_text = st.chat_input("Yêu cầu thêm chi tiết...")
    if chat_text:
        st.session_state.vip_chat.append({"role": "user", "content": chat_text})
        with st.chat_message("user"): st.markdown(chat_text)
        with st.chat_message("assistant"):
            res = st.session_state.full_ai_session.send_message(chat_text)
            st.markdown(res.text)
            st.session_state.vip_chat.append({"role": "assistant", "content": res.text})