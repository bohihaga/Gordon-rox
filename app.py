import streamlit as st
import google.generativeai as genai
import requests
from utils import init_system, hash_pass, load_db, save_db, USER_DB

# 1. Cấu hình trang: Bắt buộc để đầu tiên
st.set_page_config(page_title="Gordon Rox | AI Culinary", page_icon="🧑‍🍳", layout="wide", initial_sidebar_state="expanded")
init_system()

# Khởi tạo các biến session state
if "auth_view" not in st.session_state: st.session_state.auth_view = "home"
if "preview_chat" not in st.session_state: st.session_state.preview_chat = []
if "theme_mode" not in st.session_state: st.session_state.theme_mode = "Dark" # Mặc định là Dark

# ==========================================
# 🎨 HỆ THỐNG GIAO DIỆN (THEME & CSS)
# ==========================================
# Thiết lập màu sắc dựa trên lựa chọn người dùng
if st.session_state.theme_mode == "Dark":
    bg_color = "#0f1115"
    text_color = "#f8fafc"
    card_bg = "#16181d"
    sidebar_bg = "#16181d"
    border_color = "#272a30"
else:
    bg_color = "#ffffff"
    text_color = "#1e293b"
    card_bg = "#f1f5f9"
    sidebar_bg = "#f8fafc"
    border_color = "#e2e8f0"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Playfair+Display:ital,wght@1,600&display=swap');
    
    body, p, h1, h2, h3, h4, h5, h6, span, div, input, textarea, button {{
        font-family: 'Inter', sans-serif !important;
    }}

    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    
    /* 🔥 XÓA SẠCH CÁC THÀNH PHẦN RAW VÀ CROP GIAO DIỆN 🔥 */
    footer {{ visibility: hidden !important; height: 0px !important; }} 
    #MainMenu {{ visibility: hidden !important; }}
    [data-testid="stHeader"] {{ background-color: transparent !important; }}
    [data-testid="stToolbar"] {{ display: none !important; }}
    [data-testid="stSidebarNav"] {{ display: none !important; }}
    
    /* Tối ưu Sidebar */
    [data-testid="stSidebar"] {{ 
        background-color: {sidebar_bg}; 
        border-right: 1px solid {border_color}; 
    }}
    
    .sidebar-logo {{ 
        font-family: 'Playfair Display', serif !important; 
        font-size: 2.2rem; color: {text_color}; margin-bottom: 25px; padding-left: 10px; font-style: italic;
    }}

    /* Thẻ tính năng (Cards) */
    .glass-card-btn {{
        background: {card_bg}; border: 1px solid {border_color}; border-radius: 16px; padding: 25px 15px;
        text-align: center; transition: all 0.2s ease; height: 100%;
        display: flex; flex-direction: column; justify-content: center; align-items: center; cursor: pointer;
        color: {text_color};
    }}
    .glass-card-btn:hover {{ border-color: #f97316; transform: translateY(-3px); }}
    .glass-card-icon {{ font-size: 2.2rem; margin-bottom: 15px; }}
    .glass-card-title {{ font-weight: 600; font-size: 1.1rem; }}
    
    /* Form đăng nhập */
    .unified-auth-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 24px;
        padding: 40px 30px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.1);
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🚀 XỬ LÝ ĐĂNG NHẬP (SSO)
# ==========================================
query_params = st.query_params
if "code" in query_params and "state" in query_params:
    code = query_params["code"]
    state = query_params["state"]
    st.query_params.clear() 
    username = None
    
    if state == "github":
        try:
            token_url = "https://github.com/login/oauth/access_token"
            res = requests.post(token_url, data={"client_id": st.secrets["GITHUB_CLIENT_ID"], "client_secret": st.secrets["GITHUB_CLIENT_SECRET"], "code": code}, headers={"Accept": "application/json"})
            if res.status_code == 200 and res.json().get("access_token"):
                access_token = res.json().get("access_token")
                user_res = requests.get("https://api.github.com/user", headers={"Authorization": f"token {access_token}"})
                if user_res.status_code == 200: username = f"{user_res.json().get('login')} (GitHub)"
        except: pass
    elif state == "discord":
        try:
            token_url = "https://discord.com/api/oauth2/token"
            data = {"client_id": st.secrets["DISCORD_CLIENT_ID"], "client_secret": st.secrets["DISCORD_CLIENT_SECRET"], "grant_type": "authorization_code", "code": code, "redirect_uri": "https://gordon-rox.streamlit.app/"}
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            res = requests.post(token_url, data=data, headers=headers)
            if res.status_code == 200 and res.json().get("access_token"):
                access_token = res.json().get("access_token")
                user_res = requests.get("https://discord.com/api/users/@me", headers={"Authorization": f"Bearer {access_token}"})
                if user_res.status_code == 200: username = f"{user_res.json().get('username')} (Discord)"
        except: pass

    if username:
        users = load_db(USER_DB)
        if username not in users:
            users[username] = {"password": "oauth_user_no_pass", "fridge": []}
            save_db(USER_DB, users)
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.auth_view = "home"
        st.rerun()

# ==========================================
# 📱 THANH BÊN (SIDEBAR) 
# ==========================================
with st.sidebar:
    st.markdown("<div class='sidebar-logo'>Gordon Rox</div>", unsafe_allow_html=True)
    
    # Chế độ đổi màu nền
    st.write("🌓 **Giao diện**")
    st.session_state.theme_mode = st.radio("Chọn màu nền:", ["Dark", "Light"], label_visibility="collapsed", horizontal=True)
    
    st.divider()
    st.page_link("app.py", label="Trang chủ", icon="🏠")
    st.page_link("pages/1_🍳_Dau_Bep_AI.py", label="Phân tích món ăn", icon="🍳")
    st.page_link("pages/2_❄️_Tu_Lanh.py", label="Quản lý Tủ lạnh", icon="❄️")
    st.page_link("pages/3_🌍_Dien_Dan.py", label="Mạng xã hội", icon="🌍")
    
    st.markdown("<div style='flex-grow: 1; min-height: 30vh;'></div>", unsafe_allow_html=True)
    
    with st.container(border=True):
        if st.session_state.get("logged_in"):
            st.markdown(f"👤 **{st.session_state.username}**")
            if st.button("🔴 Đăng Xuất", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.auth_view = "home"
                st.rerun()
        else:
            st.markdown("🔒 *Chưa đăng nhập*")
            if st.button("🔑 Sign In / Up", type="primary", use_container_width=True):
                st.session_state.auth_view = "login"
                st.rerun()

# ==========================================
# 🖥️ NỘI DUNG CHÍNH (TRANG CHỦ)
# ==========================================
if st.session_state.auth_view == "home":
    greeting = st.session_state.username if st.session_state.get("logged_in") else "Bạn"
    st.markdown(f"<h1 style='text-align: center; font-size: 3rem; margin-top: 20px; font-weight: 800;'>Xin chào, <span style='color:#f97316;'>{greeting}</span>!</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; margin-bottom: 40px;'>Hôm nay chúng ta nấu gì nhỉ?</p>", unsafe_allow_html=True)
    
    col_q1, col_q2, col_q3 = st.columns(3, gap="medium")
    def action_card(col, icon, title, url):
        with col:
            st.markdown(f"""<a href="{url}" target="_self" style="text-decoration: none;"><div class="glass-card-btn"><div class="glass-card-icon">{icon}</div><div class="glass-card-title">{title}</div></div></a>""", unsafe_allow_html=True)
    
    action_card(col_q1, "📸", "Phân tích món ăn", "Dau_Bep_AI")
    action_card(col_q2, "❄️", "Kiểm tra tủ lạnh", "Tu_Lanh")
    action_card(col_q3, "🌍", "Cộng đồng ẩm thực", "Dien_Dan")

    st.write("<br>", unsafe_allow_html=True)
    
    # Khung Chat
    chat_container = st.container(height=350)
    with chat_container:
        if not st.session_state.preview_chat:
            st.markdown("<div style='text-align: center; color: #64748b; margin-top: 130px;'>Nhập nguyên liệu bạn đang có vào đây...</div>", unsafe_allow_html=True)
        for msg in st.session_state.preview_chat:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
                
    prompt = st.chat_input("Hỏi nhanh Gordon Rox...")
    if prompt:
        st.session_state.preview_chat.append({"role": "user", "content": prompt})
        st.rerun()

# ==========================================
# 🔥 GIAO DIỆN ĐĂNG NHẬP (UNIFIED CARD)
# ==========================================
elif st.session_state.auth_view == "login":
    c1, c2, c3 = st.columns([1, 1.6, 1])
    with c2:
        st.markdown("<div class='unified-auth-card'><h2 style='text-align:center;'>👋 Đăng Nhập</h2>", unsafe_allow_html=True)
        
        # SSO Buttons
        col_gh, col_dc = st.columns(2)
        with col_gh:
            try: st.link_button("🐙 GitHub", url=f"https://github.com/login/oauth/authorize?client_id={st.secrets['GITHUB_CLIENT_ID']}&scope=read:user&state=github", use_container_width=True)
            except: pass
        with col_dc:
            try: st.link_button("🎮 Discord", url=f"https://discord.com/api/oauth2/authorize?client_id={st.secrets['DISCORD_CLIENT_ID']}&redirect_uri=https://gordon-rox.streamlit.app/&response_type=code&scope=identify&state=discord", use_container_width=True)
            except: pass

        with st.form("login_form"):
            user_in = st.text_input("Tài khoản")
            pass_in = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("🚀 Vào Bếp Ngay", use_container_width=True):
                users = load_db(USER_DB)
                if user_in in users and users[user_in]["password"] == hash_pass(pass_in):
                    st.session_state.logged_in = True
                    st.session_state.username = user_in
                    st.session_state.auth_view = "home"
                    st.rerun()
                else: st.error("Lỗi đăng nhập!")
        
        if st.button("← Quay về", use_container_width=True):
            st.session_state.auth_view = "home"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

