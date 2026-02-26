import streamlit as st
import google.generativeai as genai
import requests
from utils import init_system, hash_pass, load_db, save_db, USER_DB

# Cấu hình trang (Collapsed sidebar mặc định cho khách)
st.set_page_config(page_title="Gordon Rox | AI Culinary", page_icon="✨", layout="wide", initial_sidebar_state="collapsed")
init_system()

# Khởi tạo máy trạng thái điều hướng màn hình
if "auth_view" not in st.session_state:
    st.session_state.auth_view = "home"

# ==========================================
# 🎨 CSS MAGIC - NAVBAR & FORM ĐĂNG NHẬP
# ==========================================
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); color: #f8fafc; }
    header {visibility: hidden;}
    
    /* Chữ tiêu đề Navbar */
    .nav-logo { font-size: 1.8rem; font-weight: 900; background: -webkit-linear-gradient(45deg, #f97316, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; cursor: pointer; }
    
    /* Giao diện Glassmorphism */
    .glass-card { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 16px; padding: 30px; box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1); }
    
    /* Định dạng form đăng nhập trung tâm */
    .auth-box { background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(20px); border: 1px solid #334155; border-radius: 20px; padding: 40px; box-shadow: 0 10px 40px rgba(0,0,0,0.5); text-align: center; }
    
    /* Nút bấm mặc định */
    .stButton>button { border-radius: 8px; font-weight: 600; transition: all 0.3s ease; width: 100%; }
    
    /* Nút Gradient (Sign Up / Hành động chính) */
    .btn-primary>div>button { background: linear-gradient(90deg, #f97316, #ec4899); color: white; border: none; }
    .btn-primary>div>button:hover { opacity: 0.9; box-shadow: 0 0 15px rgba(249, 115, 22, 0.4); transform: scale(1.02); }
    
    /* Nút Viền (Sign In) */
    .btn-outline>div>button { background: transparent; color: #f8fafc; border: 1px solid rgba(255,255,255,0.3); }
    .btn-outline>div>button:hover { border-color: #f97316; color: #f97316; }
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
            st.session_state.auth_view = "home" # Trả về trang chủ sau khi đăng nhập
            st.rerun()

# ==========================================
# 🗺️ THANH ĐIỀU HƯỚNG TRÊN CÙNG (TOP NAVBAR)
# ==========================================
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([6, 2, 1, 1], gap="small")

with nav_col1:
    st.markdown("<div class='nav-logo'>👨‍🍳 Gordon Rox AI</div>", unsafe_allow_html=True)

if st.session_state.logged_in:
    with nav_col3:
        st.write(f"👋 **{st.session_state.username}**")
    with nav_col4:
        st.markdown('<div class="btn-outline">', unsafe_allow_html=True)
        if st.button("Đăng Xuất"):
            st.session_state.logged_in = False
            st.session_state.auth_view = "home"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # Nút điều hướng góc phải cho khách
    with nav_col3:
        st.markdown('<div class="btn-outline">', unsafe_allow_html=True)
        if st.button("Sign In"): st.session_state.auth_view = "login"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with nav_col4:
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("Sign Up"): st.session_state.auth_view = "signup"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin-top: 5px;'>", unsafe_allow_html=True)

# ==========================================
# 🖥️ ĐIỀU CHUYỂN CÁC MÀN HÌNH (ROUTING)
# ==========================================

# --- MÀN HÌNH 1: TRANG CHỦ (LANDING PAGE) ---
if st.session_state.auth_view == "home":
    st.markdown("<h1 style='font-size: 4rem; text-align: center; margin-top: 20px; font-weight: 900; background: -webkit-linear-gradient(45deg, #f97316, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Chuẩn Mực Ẩm Thực Tương Lai</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 1.2rem; margin-bottom: 40px;'>Khám phá công thức vô tận và quản lý tủ lạnh của bạn bằng Trí Tuệ Nhân Tạo.</p>", unsafe_allow_html=True)
    
    col_empty1, col_center, col_empty2 = st.columns([1, 2, 1])
    with col_center:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("💬 Trải nghiệm nhanh Bếp Trưởng AI")
        if "preview_chat" not in st.session_state: st.session_state.preview_chat = []
        
        chat_container = st.container(height=300)
        with chat_container:
            if len(st.session_state.preview_chat) == 0:
                st.caption("Ví dụ: 'Chỉ tôi cách làm bít tết chuẩn nhà hàng 5 sao.'")
            for msg in st.session_state.preview_chat:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
                
        prompt = st.chat_input("Hỏi công thức nấu ăn ngay...")
        if prompt:
            st.session_state.preview_chat.append({"role": "user", "content": prompt})
            st.rerun()

        if len(st.session_state.preview_chat) > 0 and st.session_state.preview_chat[-1]["role"] == "user":
            with chat_container:
                with st.chat_message("assistant"):
                    with st.spinner("Đang suy nghĩ..."):
                        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction="Trả lời chuyên nghiệp, nhắc người dùng Sign Up để lưu công thức.")
                        res = model.generate_content(st.session_state.preview_chat[-1]["content"])
                        st.markdown(res.text)
                        st.session_state.preview_chat.append({"role": "assistant", "content": res.text})
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.session_state.logged_in:
            st.success("Bạn đã đăng nhập! Mở thanh Menu bên trái (dấu > góc trên cùng) để vào Bếp nhé!")

# --- MÀN HÌNH 2: ĐĂNG NHẬP (SIGN IN) ---
elif st.session_state.auth_view == "login":
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
        st.markdown("<h2>Chào mừng trở lại</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:gray; margin-bottom: 30px;'>Đăng nhập để vào không gian bếp của bạn</p>", unsafe_allow_html=True)
        
        # Nút GitHub Xịn
        try:
            client_id = st.secrets["GITHUB_CLIENT_ID"]
            auth_url = f"https://github.com/login/oauth/authorize?client_id={client_id}&scope=read:user"
            st.link_button("Đăng nhập nhanh với GitHub 🐙", url=auth_url, use_container_width=True)
        except: pass
        
        st.markdown("<div style='margin: 15px 0; color: gray; font-size: 0.8em;'>HOẶC</div>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            user_in = st.text_input("Tài khoản", placeholder="Nhập username...")
            pass_in = st.text_input("Mật khẩu", type="password", placeholder="••••••••")
            st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
            submit = st.form_submit_button("Đăng Nhập")
            st.markdown('</div>', unsafe_allow_html=True)
            
            if submit:
                users = load_db(USER_DB)
                if user_in in users and users[user_in]["password"] == hash_pass(pass_in):
                    st.session_state.logged_in = True
                    st.session_state.username = user_in
                    st.session_state.user_data = users[user_in]
                    st.session_state.auth_view = "home"
                    st.rerun()
                else:
                    st.error("Sai tài khoản hoặc mật khẩu!")
                    
        st.write("---")
        if st.button("Chưa có tài khoản? Đăng ký ngay"):
            st.session_state.auth_view = "signup"
            st.rerun()
            
        if st.button("🏠 Quay lại Trang Chủ"):
            st.session_state.auth_view = "home"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- MÀN HÌNH 3: ĐĂNG KÝ (SIGN UP) ---
elif st.session_state.auth_view == "signup":
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
        st.markdown("<h2 style='color:#f97316;'>Tạo Tài Khoản Mới</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:gray; margin-bottom: 30px;'>Gia nhập cộng đồng siêu đầu bếp ngay hôm nay</p>", unsafe_allow_html=True)
        
        with st.form("signup_form"):
            new_user = st.text_input("Tài khoản mới", placeholder="Chọn username...")
            new_pass = st.text_input("Mật khẩu", type="password", placeholder="Tối thiểu 4 ký tự")
            st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
            submit = st.form_submit_button("Đăng Ký Tài Khoản")
            st.markdown('</div>', unsafe_allow_html=True)
            
            if submit:
                users = load_db(USER_DB)
                if new_user in users: st.error("Tên này đã có người sử dụng!")
                elif len(new_pass) < 4: st.error("Mật khẩu phải từ 4 ký tự trở lên!")
                else:
                    users[new_user] = {"password": hash_pass(new_pass), "fridge": []}
                    save_db(USER_DB, users)
                    st.success("Thành công! Hãy chuyển sang Đăng Nhập.")
                    
        st.write("---")
        if st.button("Đã có tài khoản? Đăng nhập"):
            st.session_state.auth_view = "login"
            st.rerun()
            
        if st.button("🏠 Quay lại Trang Chủ"):
            st.session_state.auth_view = "home"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
