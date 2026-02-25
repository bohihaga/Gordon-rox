import streamlit as st
import google.generativeai as genai
import requests
from utils import init_system, hash_pass, load_db, save_db, USER_DB

# Bắt buộc dùng giao diện Rộng và Tiêu đề mới
st.set_page_config(page_title="Gordon Rox | AI Culinary", page_icon="✨", layout="wide", initial_sidebar_state="collapsed")
init_system()

# ==========================================
# 🎨 CSS MAGIC - BIẾN HÌNH THÀNH APP TIỀN TỶ
# ==========================================
st.markdown("""
    <style>
    /* Ép toàn bộ web sang nền tối gradient cực xịn */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    
    /* Ẩn Header mặc định của Streamlit */
    header {visibility: hidden;}
    
    /* Chữ tiêu đề phát sáng (Gradient Text) */
    .hero-title {
        font-size: 3.5rem;
        font-weight: 900;
        background: -webkit-linear-gradient(45deg, #f97316, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        padding-bottom: 10px;
        letter-spacing: -1px;
    }
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }

    /* Hiệu ứng Kính mờ (Glassmorphism) cho các khối */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, border 0.3s ease;
    }
    .glass-card:hover {
        border: 1px solid rgba(249, 115, 22, 0.3);
        transform: translateY(-2px);
    }

    /* Nút bấm Gradient sành điệu */
    .stButton>button {
        background: linear-gradient(90deg, #f97316, #ec4899);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        padding: 10px;
    }
    .stButton>button:hover {
        opacity: 0.9;
        box-shadow: 0 0 15px rgba(249, 115, 22, 0.4);
        transform: scale(1.02);
    }

    /* Style lại nút GitHub cho sang trọng */
    .stLinkButton>a>button {
        background-color: #ffffff10 !important;
        border: 1px solid #ffffff20 !important;
        color: white !important;
        border-radius: 8px;
        transition: all 0.3s;
    }
    .stLinkButton>a>button:hover {
        background-color: #ffffff20 !important;
        border: 1px solid #ffffff40 !important;
    }
    
    /* Làm đẹp thanh Chat Input */
    .stChatInputContainer {
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1) !important;
        background: rgba(0,0,0,0.2) !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🚀 XỬ LÝ ĐĂNG NHẬP GITHUB NGẦM
# ==========================================
query_params = st.query_params
if "code" in query_params:
    code = query_params["code"]
    st.query_params.clear()
    
    token_url = "https://github.com/login/oauth/access_token"
    data = {"client_id": st.secrets["GITHUB_CLIENT_ID"], "client_secret": st.secrets["GITHUB_CLIENT_SECRET"], "code": code}
    headers = {"Accept": "application/json"}
    res = requests.post(token_url, data=data, headers=headers)
    
    if res.status_code == 200 and res.json().get("access_token"):
        access_token = res.json().get("access_token")
        user_res = requests.get("https://api.github.com/user", headers={"Authorization": f"token {access_token}"})
        if user_res.status_code == 200:
            username = user_res.json().get("login")
            users = load_db(USER_DB)
            if username not in users:
                users[username] = {"password": "github_oauth_user", "fridge": []}
                save_db(USER_DB, users)
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_data = users[username]
            st.rerun()

# ==========================================
# 🌟 GIAO DIỆN CHÍNH (HERO SECTION)
# ==========================================
st.markdown("<h1 class='hero-title'>Gordon Rox AI ✨</h1>", unsafe_allow_html=True)
st.markdown("<div class='hero-subtitle'>Trợ lý ẩm thực cá nhân của bạn. Thông minh, sáng tạo và hoàn toàn tự động.</div>", unsafe_allow_html=True)

col_preview, col_auth = st.columns([1.2, 1], gap="large")

# --- CỘT TRÁI: KHU VỰC TRẢI NGHIỆM AI ---
with col_preview:
    st.markdown("""
    <div class="glass-card">
        <h3 style="margin-top:0; color:#e2e8f0;">💬 Chat trực tiếp với AI</h3>
        <p style="color:#94a3b8; font-size:0.9em;">(Phiên bản dùng thử - Chỉ hỗ trợ văn bản)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Khung chat Demo
    st.write("") 
    if "preview_chat" not in st.session_state: st.session_state.preview_chat = []
    
    chat_container = st.container(height=350)
    with chat_container:
        if len(st.session_state.preview_chat) == 0:
            st.caption("Hãy thử hỏi: 'Tôi có 2 quả trứng và ít hành tây, nấu món gì ngon?'")
        for msg in st.session_state.preview_chat:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
    prompt = st.chat_input("Hỏi Gordon Rox...")
    if prompt:
        st.session_state.preview_chat.append({"role": "user", "content": prompt})
        st.rerun() # Rerun để render tin nhắn ngay lập tức

    # Logic AI sinh chữ sau khi Rerun
    if len(st.session_state.preview_chat) > 0 and st.session_state.preview_chat[-1]["role"] == "user":
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Đang suy nghĩ..."):
                    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction="Trả lời ngắn gọn, ngầu như siêu đầu bếp. Kêu gọi người dùng đăng nhập để gửi ảnh tủ lạnh.")
                    res = model.generate_content(st.session_state.preview_chat[-1]["content"])
                    st.markdown(res.text)
                    st.session_state.preview_chat.append({"role": "assistant", "content": res.text})

# --- CỘT PHẢI: KHU VỰC ĐĂNG NHẬP (AUTH) ---
with col_auth:
    if st.session_state.logged_in:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <h2>🎉 Chào mừng trở lại!</h2>
            <h1 style="color:#f97316;">@{st.session_state.username}</h1>
            <p style="color:#94a3b8;">Hệ thống đã sẵn sàng. Hãy mở menu bên trái để truy cập Đầu Bếp AI, Tủ Lạnh và Diễn Đàn.</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if st.button("🔴 Đăng Xuất An Toàn", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    else:
        st.markdown("""
        <div class="glass-card">
            <h2 style="margin-top:0;">Truy cập Bếp Trưởng 🚀</h2>
            <p style="color:#94a3b8; margin-bottom: 20px;">Mở khóa tính năng nhận diện ảnh và lưu trữ tủ lạnh thông minh.</p>
        """, unsafe_allow_html=True)
        
        # Nút GitHub Xịn
        try:
            client_id = st.secrets["GITHUB_CLIENT_ID"]
            auth_url = f"https://github.com/login/oauth/authorize?client_id={client_id}&scope=read:user"
            st.link_button("Đăng nhập nhanh với GitHub 🐙", url=auth_url, use_container_width=True)
        except KeyError:
            st.error("⚠️ Lỗi API GitHub trong hệ thống.")

        st.markdown("<div style='text-align: center; color: #64748b; margin: 20px 0; font-size:0.8em;'>HOẶC DÙNG TÀI KHOẢN MẶC ĐỊNH</div>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Đăng Nhập", "Đăng Ký"])
        with tab1:
            with st.form("login_form"):
                user_in = st.text_input("Tài khoản", placeholder="Nhập username...")
                pass_in = st.text_input("Mật khẩu", type="password", placeholder="••••••••")
                if st.form_submit_button("VÀO BẾP", use_container_width=True):
                    users = load_db(USER_DB)
                    if user_in in users and users[user_in]["password"] == hash_pass(pass_in):
                        st.session_state.logged_in = True
                        st.session_state.username = user_in
                        st.session_state.user_data = users[user_in]
                        st.rerun()
                    else:
                        st.error("Sai tài khoản hoặc mật khẩu!")
        with tab2:
            with st.form("reg_form"):
                new_user = st.text_input("Tài khoản mới")
                new_pass = st.text_input("Mật khẩu mới", type="password")
                if st.form_submit_button("TẠO TÀI KHOẢN", use_container_width=True):
                    users = load_db(USER_DB)
                    if new_user in users: st.error("Tên này đã tồn tại!")
                    elif len(new_pass) < 4: st.error("Mật khẩu quá ngắn!")
                    else:
                        users[new_user] = {"password": hash_pass(new_pass), "fridge": []}
                        save_db(USER_DB, users)
                        st.success("Tuyệt vời! Hãy sang tab Đăng Nhập.")
                        
        st.markdown("</div>", unsafe_allow_html=True) # Đóng thẻ glass-card