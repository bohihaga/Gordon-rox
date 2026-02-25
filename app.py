import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import os
from datetime import datetime

# ==========================================
# 1. CẤU HÌNH TRANG WEB & CSS
# ==========================================
st.set_page_config(page_title="Gordon Rox - Masterchef AI", page_icon="👨‍🍳", layout="wide")

def load_css():
    st.markdown("""
        <style>
        .main { background-color: #f9f9f9; }
        h1, h2, h3 { color: #d32f2f; font-family: 'Arial Black', sans-serif; }
        .stButton>button { border-radius: 20px; transition: 0.3s; }
        .stButton>button:hover { transform: scale(1.05); }
        .forum-msg { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0px 4px 6px rgba(0,0,0,0.1); margin-bottom: 10px; border-left: 5px solid #d32f2f; }
        .forum-time { font-size: 0.8em; color: gray; }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. KHỞI TẠO HỆ THỐNG & AI
# ==========================================
def init_system():
    try:
        API_KEY = st.secrets["GEMINI_API_KEY"] 
        genai.configure(api_key=API_KEY)
    except KeyError:
        st.error("⚠️ HỆ THỐNG CẢNH BÁO: Chưa cấu hình API Key trong bảo mật Streamlit!")
        st.stop()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Khởi tạo file diễn đàn nếu chưa có
    if not os.path.exists("forum_messages.json"):
        with open("forum_messages.json", "w", encoding="utf-8") as f:
            json.dump([], f)

# ==========================================
# 3. THANH ĐIỀU KHIỂN BÊN TRÁI (SIDEBAR)
# ==========================================
def render_sidebar():
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/1830/1830839.png", width=120)
        st.title("⚙️ Tùy chỉnh AI")
        st.divider()
        
        # Người dùng tự cấu hình AI
        st.subheader("Khẩu vị của bạn")
        diet_mode = st.selectbox("Chế độ ăn:", ["Bình thường", "Ăn chay (Vegan)", "Giảm cân (Eatclean)", "Keto"])
        
        st.subheader("Tính cách Đầu bếp")
        tone_mode = st.select_slider("Thái độ của Gordon Rox:", options=["Hiền lành", "Chuyên nghiệp", "Gắt gỏng (Chuẩn Ramsay)"], value="Chuyên nghiệp")
        
        st.divider()
        if st.button("🗑️ Xóa bộ nhớ Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.pop("ai_session", None) # Xóa session cũ
            st.rerun()
            
        st.caption("Phiên bản: Gordon Rox 5.0 Pro")
        return diet_mode, tone_mode

# ==========================================
# 4. THIẾT LẬP BỘ NÃO AI (GUARDRAILS & PERSONA)
# ==========================================
def setup_ai_model(diet_mode, tone_mode):
    # Kết hợp các tùy chọn của người dùng vào luật của AI
    luat_cua_ai = f"""
    Bạn là siêu đầu bếp Gordon Rox. BẠN BỊ GIỚI HẠN CHỦ ĐỀ CỰC KỲ NGHIÊM NGẶT.
    1. Chủ đề: CHỈ trả lời về ẩm thực, nấu ăn, công thức, nguyên liệu. Nếu hỏi ngoài luồng (Toán, Code, Lịch sử...), hãy mắng mỏ lịch sự và từ chối.
    2. Chế độ ăn của khách: Khách đang ăn theo chế độ '{diet_mode}'. Hãy ưu tiên gợi ý phù hợp với chế độ này.
    3. Tính cách của bạn: Hãy cư xử theo thái độ '{tone_mode}'. Nếu là 'Gắt gỏng', hãy dùng từ ngữ mạnh, chê bai nguyên liệu nếu nó héo úa, nhưng cuối cùng vẫn đưa ra lời khuyên nấu ăn ngon. Nếu 'Hiền lành', hãy động viên họ.
    """
    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=luat_cua_ai)
    
    if "ai_session" not in st.session_state:
        st.session_state.ai_session = model.start_chat(history=[])
        
    return model

# ==========================================
# 5. GIAO DIỆN CHAT VỚI AI (TAB 1)
# ==========================================
def render_chat_tab():
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown("### 📸 Tải ảnh nguyên liệu")
        uploaded_file = st.file_uploader("Kéo thả hoặc chọn ảnh từ máy tính", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        anh_gui_di = None
        if uploaded_file:
            anh_gui_di = Image.open(uploaded_file)
            st.image(anh_gui_di, use_column_width=True, caption="Nguyên liệu đang chờ xử lý...")

    with col2:
        st.markdown("### 🎯 Mục tiêu hôm nay")
        che_do = st.radio("Gordon Rox cần làm gì?", ["Gợi ý công thức nấu ăn 🥘", "Kiểm tra độ tươi của thực phẩm 🤢"], label_visibility="collapsed")
        st.write("")
        if st.button("🚀 XEM XÉT NGUYÊN LIỆU NÀY", type="primary", use_container_width=True):
            if not anh_gui_di:
                st.error("Gordon Rox không bị mù! Hãy đưa ảnh đây!")
            else:
                with st.spinner("Đang phân tích hình ảnh..."):
                    prompt = "Gợi ý 3 món ăn ngon từ ảnh này." if "Gợi ý" in che_do else "Đồ ăn này còn ăn được không hay phải vứt đi?"
                    st.session_state.chat_history.append({"role": "user", "content": f"*{prompt}* [Đã đính kèm ảnh]"})
                    try:
                        response = st.session_state.ai_session.send_message([prompt, anh_gui_di])
                        st.session_state.chat_history.append({"role": "ai", "content": response.text})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Lỗi kết nối AI: {e}")

    st.divider()
    st.markdown("### 💬 Trò chuyện với Gordon Rox")
    
    # Render lịch sử
    for message in st.session_state.chat_history:
        avatar_icon = "🧑‍🍳" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar_icon):
            st.markdown(message["content"])

    # Box chat và upload thêm ảnh
    with st.container():
        anh_chat_them = st.file_uploader("📎 Đính kèm ảnh vào tin nhắn (Tùy chọn)", type=["jpg", "png"], key="extra_img")
        user_reply = st.chat_input("Hỏi công thức, xin mẹo vặt, hoặc cãi lại Gordon Rox...")

        if user_reply:
            content_display = user_reply + (" [Có ảnh đính kèm]" if anh_chat_them else "")
            st.session_state.chat_history.append({"role": "user", "content": content_display})
            
            with st.chat_message("user", avatar="🧑‍🍳"):
                st.markdown(content_display)
                if anh_chat_them: st.image(Image.open(anh_chat_them), width=150)

            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Gordon Rox đang gõ..."):
                    try:
                        payload = [user_reply, Image.open(anh_chat_them)] if anh_chat_them else user_reply
                        response = st.session_state.ai_session.send_message(payload)
                        st.markdown(response.text)
                        st.session_state.chat_history.append({"role": "ai", "content": response.text})
                    except Exception as e:
                        st.error(f"Lỗi: {e}")

# ==========================================
# 6. GIAO DIỆN DIỄN ĐÀN (TAB 2)
# ==========================================
def render_forum_tab():
    st.header("🌍 Diễn đàn Hội Đầu Bếp Toàn Cầu")
    st.markdown("Chia sẻ thành quả, bóc phốt nhà hàng, hoặc khoe công thức của bạn!")
    
    # Khu vực đăng bài
    with st.form("forum_post_form", clear_on_submit=True):
        col_name, col_msg = st.columns([1, 3])
        with col_name:
            user_name = st.text_input("Tên của bạn:", placeholder="Bếp trưởng tương lai...")
        with col_msg:
            user_msg = st.text_input("Bạn muốn nói gì?", placeholder="Món thịt kho tàu của AI cho hôm nay hơi mặn...")
        
        submit_post = st.form_submit_button("📢 Đăng bài lên diễn đàn")
        
        if submit_post:
            if user_name.strip() and user_msg.strip():
                # Thêm ngày giờ hiện tại
                now = datetime.now().strftime("%d/%m/%Y - %H:%M")
                new_post = {"name": user_name, "time": now, "message": user_msg}
                
                # Đọc và lưu file
                with open("forum_messages.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                data.append(new_post)
                with open("forum_messages.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)
                st.success("Đã đăng bài!")
                st.rerun()
            else:
                st.warning("Vui lòng điền đủ Tên và Nội dung!")

    st.divider()
    
    # Hiển thị các bài đăng
    try:
        with open("forum_messages.json", "r", encoding="utf-8") as f:
            posts = json.load(f)
            
        if not posts:
            st.info("Chưa có ai đăng bài. Hãy là người mở bát!")
        else:
            # In ngược từ mới nhất đến cũ nhất
            for post in reversed(posts):
                st.markdown(f"""
                <div class="forum-msg">
                    <strong>🧑‍🍳 {post.get('name', 'Ẩn danh')}</strong> <span class="forum-time">({post.get('time', 'Vừa xong')})</span><br>
                    {post.get('message', '')}
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.error("Đang bảo trì diễn đàn...")

# ==========================================
# 7. CHẠY ỨNG DỤNG CHÍNH (MAIN PROCESS)
# ==========================================
def main():
    load_css()
    init_system()
    
    # Thiết lập giao diện
    st.title("🍳 HỆ THỐNG TRỢ LÝ BẾP: GORDON ROX")
    st.caption("AI nhận diện hình ảnh & Tư vấn dinh dưỡng chuẩn Quốc tế")
    
    # Xử lý Logic từ Sidebar
    diet_mode, tone_mode = render_sidebar()
    setup_ai_model(diet_mode, tone_mode)
    
    # Render Tabs
    tab1, tab2 = st.tabs(["🤖 Không gian bếp AI", "👥 Cộng đồng giao lưu"])
    with tab1:
        render_chat_tab()
    with tab2:
        render_forum_tab()

# Kích hoạt chương trình
if __name__ == "__main__":
    main()