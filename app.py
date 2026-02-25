import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import os

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Bếp AI Masterchef", page_icon="👨‍🍳", layout="wide")

# --- KẾT NỐI AI ---
try:
    API_KEY = st.secrets["GEMINI_API_KEY"] 
    genai.configure(api_key=API_KEY)
except KeyError:
    st.error("⚠️ Lỗi: Không tìm thấy API Key trong két sắt (secrets).")
    st.stop()

# ==========================================
# 🌟 TÍNH NĂNG 1: GIỚI HẠN CHỦ ĐỀ CỦA AI (GUARDRAILS)
# ==========================================
luat_cua_ai = """
Bạn là siêu đầu bếp Gordon Rox. BẠN BỊ GIỚI HẠN CHỦ ĐỀ.
Quy tắc bắt buộc: Bạn CHỈ được phép trả lời các câu hỏi liên quan đến ẩm thực, nấu ăn, công thức, nguyên liệu, và an toàn thực phẩm. 
Nếu người dùng hỏi về các chủ đề khác (toán học, lập trình, chính trị, lịch sử, v.v.), BẮT BUỘC phải từ chối lịch sự và nhắc họ rằng bạn chỉ là một đầu bếp, chỉ biết nấu ăn.
"""
# Cài đặt luật vào "não" AI
model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=luat_cua_ai)

# --- KHỞI TẠO BỘ NHỚ AI ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "ai_session" not in st.session_state:
    st.session_state.ai_session = model.start_chat(history=[])

# ==========================================
# 🌟 TÍNH NĂNG 2: CHIA TAB (AI VÀ DIỄN ĐÀN)
# ==========================================
st.title("👨‍🍳 GORDON ROX - CỘNG ĐỒNG ẨM THỰC")
st.divider()

# Tạo 2 thẻ (Tab) để chuyển đổi qua lại
tab1, tab2 = st.tabs(["🤖 Trợ lý Bếp AI", "🌍 Diễn đàn Đầu bếp"])

# ------------------------------------------
# TAB 1: KHU VỰC TRÒ CHUYỆN VỚI AI
# ------------------------------------------
with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.write("### 📸 1. Phân tích ảnh đầu vào")
        uploaded_file = st.file_uploader("Kéo thả ảnh nguyên liệu vào đây", type=["jpg", "png", "jpeg"], key="main_upload")
        anh_gui_di = None
        if uploaded_file:
            anh_gui_di = Image.open(uploaded_file)
            st.image(anh_gui_di, use_column_width=True)

    with col2:
        st.write("### 🤖 2. Khởi tạo câu hỏi")
        che_do = st.radio("Chọn tính năng:", ["🍳 Gợi ý món ăn", "🤢 Soi thực phẩm hỏng"])
        
        if st.button("🚀 Gửi ảnh cho AI", type="primary"):
            if not anh_gui_di:
                st.warning("⚠️ Bạn ơi, tải ảnh lên trước đã nhé!")
            else:
                with st.spinner("Gordon Rox đang nhìn ảnh..."):
                    try:
                        if che_do == "🍳 Gợi ý món ăn":
                            prompt = "Hãy nhìn ảnh nguyên liệu này, liệt kê chúng và gợi ý 3 món ăn ngon."
                        else:
                            prompt = "Đánh giá xem đồ ăn trong ảnh có bị mốc/hỏng không."
                        
                        st.session_state.chat_history.append({"role": "user", "content": f"{prompt} [Đã đính kèm ảnh]"})
                        response = st.session_state.ai_session.send_message([prompt, anh_gui_di])
                        st.session_state.chat_history.append({"role": "ai", "content": response.text})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Có lỗi xảy ra: {e}")

    st.divider()
    st.write("### 💬 Khung Chat với AI")
    
    # In lịch sử chat
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user", avatar="🧑‍🍳"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(message["content"])

    # ==========================================
    # 🌟 TÍNH NĂNG 3: UPLOAD ẢNH KHI ĐANG CHAT
    # ==========================================
    st.write("---")
    st.caption("📎 Bạn có muốn gửi thêm ảnh vào đoạn chat không?")
    anh_chat_them = st.file_uploader("Upload ảnh bổ sung (Tùy chọn)", type=["jpg", "png", "jpeg"], key="chat_upload")
    
    user_reply = st.chat_input("Hỏi Gordon Rox (Nhớ là chỉ được hỏi đồ ăn thôi nhé!)...")

    if user_reply:
        # Lưu tin nhắn người dùng
        noi_dung_hien_thi = user_reply
        if anh_chat_them:
            noi_dung_hien_thi += " [Đã gửi kèm 1 ảnh mới]"
            
        st.session_state.chat_history.append({"role": "user", "content": noi_dung_hien_thi})
        
        # Gửi cho AI (Kèm ảnh nếu có)
        with st.chat_message("user", avatar="🧑‍🍳"):
            st.markdown(noi_dung_hien_thi)
            if anh_chat_them:
                st.image(anh_chat_them, width=200)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Đang suy nghĩ..."):
                try:
                    if anh_chat_them:
                        img_chat = Image.open(anh_chat_them)
                        response = st.session_state.ai_session.send_message([user_reply, img_chat])
                    else:
                        response = st.session_state.ai_session.send_message(user_reply)
                        
                    st.markdown(response.text)
                    st.session_state.chat_history.append({"role": "ai", "content": response.text})
                except Exception as e:
                    st.error(f"Lỗi: {e}")

# ------------------------------------------
# TAB 2: DIỄN ĐÀN GIAO LƯU (NGƯỜI VỚI NGƯỜI)
# ------------------------------------------
with tab2:
    st.header("🌍 Diễn đàn Cộng đồng Gordon Rox")
    st.markdown("Nơi các siêu đầu bếp chia sẻ kinh nghiệm và chém gió!")
    
    # Tạo một file txt để lưu tin nhắn diễn đàn
    FILE_DIEN_DAN = "forum_messages.json"
    
    # Nếu file chưa có thì tạo mới
    if not os.path.exists(FILE_DIEN_DAN):
        with open(FILE_DIEN_DAN, "w", encoding="utf-8") as f:
            json.dump([], f)

    # Đọc tin nhắn từ file
    with open(FILE_DIEN_DAN, "r", encoding="utf-8") as f:
        tin_nhan_dien_dan = json.load(f)

    # Hiển thị tin nhắn diễn đàn
    st.write("---")
    for tn in tin_nhan_dien_dan:
        with st.chat_message("user", avatar="🔥"):
            st.markdown(f"**Khách ẩn danh:** {tn}")

    # Ô nhập tin nhắn cho diễn đàn
    tin_nhan_moi = st.chat_input("Nhắn gì đó cho mọi người trên diễn đàn...")
    if tin_nhan_moi:
        tin_nhan_dien_dan.append(tin_nhan_moi)
        # Lưu lại vào file
        with open(FILE_DIEN_DAN, "w", encoding="utf-8") as f:
            json.dump(tin_nhan_dien_dan, f, ensure_ascii=False)
        st.rerun()