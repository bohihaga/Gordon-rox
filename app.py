import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Bếp AI Masterchef", page_icon="👨‍🍳", layout="wide")

# --- KẾT NỐI AI (ĐÃ BẢO MẬT API KEY) ---
# Lấy API Key từ "két sắt" (secrets) của Streamlit
try:
    API_KEY = st.secrets["GEMINI_API_KEY"] 
    genai.configure(api_key=API_KEY)
except KeyError:
    st.error("⚠️ Lỗi: Không tìm thấy API Key trong két sắt (secrets). Hãy kiểm tra lại cài đặt!")
    st.stop() # Dừng chạy code nếu không có key

model = genai.GenerativeModel('gemini-2.5-flash') # Hoặc gemini-2.0-flash nếu bạn thích

# ==========================================
# 🌟 TÍNH NĂNG MỚI: TẠO BỘ NHỚ CHO CHATBOT
# ==========================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [] # Lưu lịch sử tin nhắn để hiển thị
if "ai_session" not in st.session_state:
    st.session_state.ai_session = model.start_chat(history=[]) # Lưu phiên làm việc của Google AI

# --- CSS LÀM ĐẸP GIAO DIỆN ---
st.markdown("""
    <style>
    .stChatInput { padding-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR (THANH BÊN TRÁI) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1830/1830839.png", width=100)
    st.title("🎛️ Bảng điều khiển")
    che_do = st.radio("Chọn tính năng:", ["🍳 Gợi ý món ăn", "🤢 Soi thực phẩm hỏng"])
    st.divider()
    
    # Nút xóa trí nhớ
    if st.button("🗑️ Xóa cuộc trò chuyện mới"):
        st.session_state.chat_history = []
        st.session_state.ai_session = model.start_chat(history=[])
        st.rerun()

# --- GIAO DIỆN CHÍNH ---
st.title("👨‍🍳 TRỢ LÝ BẾP AI (CHẾ ĐỘ TRÒ CHUYỆN)")
st.markdown("Tải ảnh lên để bắt đầu, sau đó bạn có thể chat để hỏi thêm chi tiết!")
st.divider()

# Khu vực up ảnh và nút khởi tạo ở trên cùng
col1, col2 = st.columns([1, 1])
with col1:
    uploaded_file = st.file_uploader("📸 Bước 1: Kéo thả ảnh nguyên liệu vào đây", type=["jpg", "png", "jpeg"])
    anh_gui_di = None
    if uploaded_file:
        anh_gui_di = Image.open(uploaded_file)
        with st.expander("🖼️ Xem ảnh đã tải lên", expanded=False):
            st.image(anh_gui_di, use_column_width=True)

with col2:
    st.write("🤖 Bước 2: Bắt đầu câu chuyện")
    if st.button("🚀 Gửi ảnh cho AI", type="primary"):
        if not anh_gui_di:
            st.warning("⚠️ Bạn ơi, tải ảnh lên trước đã nhé!")
        else:
            with st.spinner("AI đang nhìn ảnh và suy nghĩ..."):
                try:
                    # Quyết định câu hỏi đầu tiên dựa theo chế độ
                    if che_do == "🍳 Gợi ý món ăn":
                        prompt = "Hãy nhìn ảnh nguyên liệu này, liệt kê chúng và gợi ý 3 món ăn ngon."
                    else:
                        prompt = "Hãy nhìn ảnh này và đóng vai chuyên gia an toàn thực phẩm, đánh giá xem đồ ăn có bị mốc/hỏng không."
                    
                    # Lưu tin nhắn của người dùng (gồm text và chữ [Đã gửi ảnh])
                    st.session_state.chat_history.append({"role": "user", "content": f"{prompt} [Đã đính kèm ảnh]"})
                    
                    # Gửi cả ảnh và text cho AI trong phiên chat
                    response = st.session_state.ai_session.send_message([prompt, anh_gui_di])
                    
                    # Lưu câu trả lời của AI
                    st.session_state.chat_history.append({"role": "ai", "content": response.text})
                    st.rerun() # Tải lại trang để hiện tin nhắn
                except Exception as e:
                    st.error(f"Có lỗi xảy ra: {e}")

st.divider()

# ==========================================
# 🌟 TÍNH NĂNG MỚI: KHU VỰC CHAT (HIỂN THỊ TIN NHẮN)
# ==========================================
st.subheader("💬 Khung Chat")

# In ra toàn bộ lịch sử trò chuyện từ trước đến nay
for message in st.session_state.chat_history:
    if message["role"] == "user":
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar="👨‍🍳"):
            st.markdown(message["content"])

# ==========================================
# 🌟 TÍNH NĂNG MỚI: Ô NHẬP TIN NHẮN CHAT
# ==========================================
# st.chat_input sẽ tạo ra một thanh gõ chữ dính ở dưới cùng màn hình
user_reply = st.chat_input("Hỏi thêm AI (VD: Hướng dẫn chi tiết món số 1, Đổi món khác...)")

if user_reply:
    # 1. Hiển thị ngay tin nhắn của bạn lên màn hình
    st.session_state.chat_history.append({"role": "user", "content": user_reply})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_reply)
        
    # 2. Gửi tin nhắn cho AI và chờ nó trả lời
    with st.chat_message("assistant", avatar="👨‍🍳"):
        with st.spinner("Đang gõ..."):
            try:
                # Gửi tiếp vào cái session cũ để nó nhớ ngữ cảnh
                response = st.session_state.ai_session.send_message(user_reply)
                st.markdown(response.text)
                # Lưu câu trả lời vào trí nhớ
                st.session_state.chat_history.append({"role": "ai", "content": response.text})
            except Exception as e:
                st.error(f"Lỗi: {e}")