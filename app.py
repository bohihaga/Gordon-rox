import streamlit as st
import google.generativeai as genai
import requests
from utils import init_system, hash_pass, load_db, save_db, USER_DB

# 1. Cấu hình trang (Bắt buộc để đầu tiên)
st.set_page_config(page_title="Gordon Rox | AI Culinary", page_icon="🧑‍🍳", layout="wide", initial_sidebar_state="expanded")
init_system()

# Khởi tạo các biến session
if "auth_view" not in st.session_state: st.session_state.auth_view = "home"
if "preview_chat" not in st.session_state: st.session_state.preview_chat = []
if "theme_mode" not in st.session_state: st.session_state.theme_mode = "Dark"

# ==========================================
# 🎨 HỆ THỐNG GIAO DIỆN CHUẨN MỰC
# ==========================================
# ĐÃ SỬA LỖI ĐẢO NGƯỢC: Chọn Light ra Light, chọn Dark ra Dark
if st.session_state.theme_mode == "Light":
    bg_color, text_color, card_bg, sidebar_bg, border_color = "#ffffff", "#1e293b", "#f8fafc", "#f1f5f9", "#e2e8f0"
    input_bg, input_border = "#ffffff", "#cbd5e1"
    btn_bg = "#f1f5f9"
else:
    bg_color, text_color, card_bg, sidebar_bg, border_color = "#0f1115", "#f8fafc", "#1e2026", "#16181d", "#272a30"
    input_bg, input_border = "#16181d", "#333842"
    btn_bg = "#1e2026" 

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Playfair+Display:ital,wght@1,600&display=swap');
    
    body, p, h1, h2, h3, h4, h5, h6, div, input, textarea {{ font-family: 'Inter', sans-serif !important; }}

    /* Ép màu nền và màu chữ TỔNG THỂ */
    .stApp {{ background-color: {bg_color} !important; }}
    div, p, span, a, label, h1, h2, h3, h4, h5, h6, li {{ color: {text_color} !important; }}
    a {{ text-decoration: none !important; }}
    
    /* 🔥 TRỊ LỖI Ô TEXT INPUT 🔥 */
    [data-baseweb="input"], [data-baseweb="input"] > div {{
        background-color: {input_bg} !important;
        border-color: {input_border} !important;
    }}
    input[type="text"], input[type="password"] {{
        color: {text_color} !important;
        background-color: {input_bg} !important;
        -webkit-text-fill-color: {text_color} !important;
    }}

    /* 🔥 TRỊ LỖI NÚT SSO (GITHUB/DISCORD/FB) BỊ Ô TRẮNG 🔥 */
    a[data-testid="stLinkButton"], a[data-testid="stLinkButton"] button, [data-testid="stButton"] button {{
        background-color: {btn_bg} !important; 
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
        border-radius: 10px !important; 
        font-weight: 600 !important;
        transition: all 0.2s !important; 
    }}
    
    a[data-testid="stLinkButton"]:hover, a[data-testid="stLinkButton"] button:hover, [data-testid="stButton"] button:hover {{ 
        border-color: #f97316 !important; 
        color: #f97316 !important; 
    }}

    /* 🔥 NÚT VÀO BẾP NGAY ÉP MÀU CAM 🔥 */
    [data-testid="stFormSubmitButton"] button {{ 
        background-color: #f97316 !important; 
        color: white !important; 
        border: none !important; 
        border-radius: 10px !important;
        font-weight: 600 !important;
    }}
    [data-testid="stFormSubmitButton"] button:hover {{ 
        background-color: #ea580c !important; 
        box-shadow: 0 5px 15px rgba(249, 115, 22, 0.3) !important; 
        color: white !important;
    }}

    /* Xử lý Chat Input */
    [data-testid="stBottom"], [data-testid="stBottom"] > div, [data-testid="stBottomBlock"] {{ background-color: {bg_color} !important; }}
    .stChatInputContainer {{ background-color: {input_bg} !important; border: 1px solid {input_border} !important; border-radius: 16px !important; }}
    .stChatInputContainer:focus-within {{ border-color: #f97316 !important; }}
    
    /* Làm sáng hộp Chatbox */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: {card_bg} !important; border-radius: 16px !important; border: 1px solid {border_color} !important; padding: 10px;
    }}

    /* Tẩy sạch Manage App & Header - CÀNG MẠNH TAY CÀNG TỐT */
    .viewerBadge_container, .viewerBadge_link, [data-testid="stAppDeployButton"], [data-testid="stToolbar"], footer, [data-testid="stFooter"], [class*="viewerBadge"] {{ 
        display: none !important; 
    }}
    #MainMenu {{ visibility: hidden !important; }}
    [data-testid="stHeader"] {{ background-color: transparent !important; }}
    
    /* Thiết kế Sidebar */
    [data-testid="stSidebarNav"] {{ display: none !important; }}
    [data-testid="stSidebar"] {{ background-color: {sidebar_bg} !important; border-right: 1px solid {border_color} !important; }}
    .sidebar-logo {{ font-family: 'Playfair Display', serif !important; font-size: 2.2rem; color: {text_color} !important; margin-bottom: 25px; padding-left: 10px; font-style: italic; }}
    
    /* Form Đăng Nhập Kính Mờ */
    .unified-auth-card {{
        background: {card_bg}; border: 1px solid {border_color}; border-radius: 24px; padding: 40px 30px; box-shadow: 0 20px 50px rgba(0,0,0,0.2);
    }}
    [data-testid="stForm"] {{ border: none !important; padding: 0 !important; background: transparent !important; }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🚀 XỬ LÝ ĐĂNG NHẬP ĐA NỀN TẢNG (SSO)
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
    elif state == "facebook":
        try:
            token_url = "https://graph.facebook.com/v19.0/oauth/access_token"
            params = {"client_id": st.secrets["FACEBOOK_CLIENT_ID"], "redirect_uri": "https://gordon-rox.streamlit.app/", "client_secret": st.secrets["FACEBOOK_CLIENT_SECRET"], "code": code}
            res = requests.get(token_url, params=params)
            if res.status_code == 200 and res.json().get("access_token"):
                access_token = res.json().get("access_token")
                user_res = requests.get(f"https://graph.facebook.com/me?fields=id,name&access_token={access_token}")
                if user_res.status_code == 200: username = f"{user_res.json().get('name')} (Facebook)"
        except: pass

    if username:
        users = load_db(USER_DB)
        if username not in users:
            users[username] = {"password": "oauth_user_no_pass", "fridge": []}
            save_db(USER_DB, users)
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.user_data = users[username]
        st.session_state.auth_view = "home"
        st.rerun()

# ==========================================
# 📱 THANH BÊN (SIDEBAR) 
# ==========================================
with st.sidebar:
    st.markdown("<div class='sidebar-logo'>Gordon Rox</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='font-weight:600; margin-bottom:5px;'>🌓 Giao diện:</div>", unsafe_allow_html=True)
    st.session_state.theme_mode = st.radio("Chọn màu:", ["Dark", "Light"], label_visibility="collapsed", horizontal=True)
    
    st.divider()
    
    st.page_link("app.py", label="Trang chủ", icon="🏠")
    st.page_link("pages/1_🍳_Dau_Bep_AI.py", label="Phân tích món ăn", icon="🍳")
    st.page_link("pages/2_❄️_Tu_Lanh.py", label="Quản lý Tủ lạnh", icon="❄️")
    st.page_link("pages/3_🌍_Dien_Dan.py", label="Mạng xã hội", icon="🌍")
    
    st.markdown("<div style='flex-grow: 1; min-height: 35vh;'></div>", unsafe_allow_html=True)
    
    with st.container(border=True):
        if st.session_state.get("logged_in"):
            st.markdown(f"<div style='font-weight: 600; font-size:1.1em; margin-bottom:10px;'>👤 {st.session_state.username}</div>", unsafe_allow_html=True)
            if st.button("🔴 Đăng Xuất", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.auth_view = "home"
                st.rerun()
        else:
            st.markdown("<div style='font-size: 0.9em; text-align: center; margin-bottom:10px;'>Bạn chưa đăng nhập</div>", unsafe_allow_html=True)
            if st.button("🔑 Sign In / Up", type="primary", use_container_width=True):
                st.session_state.auth_view = "login"
                st.rerun()

# ==========================================
# 🔝 GÓC TRÊN CÙNG BÊN PHẢI (NEW CHAT)
# ==========================================
if st.session_state.auth_view == "home":
    col_empty, col_new = st.columns([8.5, 1.5])
    with col_new:
        if st.button("✨ New chat", use_container_width=True):
            st.session_state.preview_chat = []
            st.rerun()

# ==========================================
# 🖥️ NỘI DUNG CHÍNH (TRANG CHỦ)
# ==========================================
if st.session_state.auth_view == "home":
    # CSS CỦA NÚT Ở TRANG CHỦ
    st.markdown(f"""
        <style>
        div[data-testid="column"] .stButton > button {{
            height: 90px !important; border-radius: 16px !important; font-size: 1.2rem !important;
            background-color: {sidebar_bg} !important; border: 1px solid {border_color} !important;
            display: flex !important; align-items: center !important; justify-content: center !important;
            color: {text_color} !important;
        }}
        div[data-testid="column"] .stButton > button:hover {{ border-color: #f97316 !important; transform: translateY(-3px) !important; color: #f97316 !important; }}
        </style>
    """, unsafe_allow_html=True)

    greeting_name = st.session_state.username if st.session_state.get("logged_in") else "Bạn"
    st.markdown(f"<h1 style='text-align: center; font-size: 3rem; margin: 10px 0 10px; font-weight: 800;'>Xin chào, <span style='color:#f97316;'>{greeting_name}</span>!</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; font-weight: 400; margin-bottom: 40px;'>Hôm nay chúng ta nấu gì nhỉ?</h3>", unsafe_allow_html=True)
    
    col_q1, col_q2, col_q3 = st.columns(3, gap="medium")
    
    with col_q1:
        if st.button("📸 Phân tích món ăn", use_container_width=True): st.switch_page("pages/1_🍳_Dau_Bep_AI.py")
        st.markdown("<p style='text-align:center; color:#64748b; font-size:0.85em; margin-top:-10px;'>Tải ảnh lên để AI nhận diện</p>", unsafe_allow_html=True)

    with col_q2:
        if st.button("❄️ Kiểm tra tủ lạnh", use_container_width=True): st.switch_page("pages/2_❄️_Tu_Lanh.py")
        st.markdown("<p style='text-align:center; color:#64748b; font-size:0.85em; margin-top:-10px;'>Xem bạn đang còn nguyên liệu gì</p>", unsafe_allow_html=True)

    with col_q3:
        if st.button("🌍 Cộng đồng ẩm thực", use_container_width=True): st.switch_page("pages/3_🌍_Dien_Dan.py")
        st.markdown("<p style='text-align:center; color:#64748b; font-size:0.85em; margin-top:-10px;'>Khám phá công thức từ mọi người</p>", unsafe_allow_html=True)
        
    st.write("<br>", unsafe_allow_html=True)
    
    chat_container = st.container(height=350)
    with chat_container:
        if not st.session_state.preview_chat: st.markdown("<div style='text-align: center; margin-top: 130px; font-weight: 400;'>Nhập nguyên liệu bạn đang có vào đây...</div>", unsafe_allow_html=True)
        for msg in st.session_state.preview_chat: 
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
                
    prompt = st.chat_input("Hỏi nhanh Gordon Rox (VD: Gợi ý bữa tối)...")
    if prompt:
        st.session_state.preview_chat.append({"role": "user", "content": prompt})
        st.rerun()
    if len(st.session_state.preview_chat) > 0 and st.session_state.preview_chat[-1]["role"] == "user":
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Đang suy nghĩ..."):
                    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction="Trả lời ngắn gọn, ngầu như đầu bếp. Kêu gọi dùng các mục ở thanh Menu bên trái.")
                    res = model.generate_content(st.session_state.preview_chat[-1]["content"])
                    st.markdown(res.text)
                    st.session_state.preview_chat.append({"role": "assistant", "content": res.text})

# ============================================================
# 🔥 GIAO DIỆN ĐĂNG NHẬP
# ============================================================
elif st.session_state.auth_view == "login":
    col1, col2, col3 = st.columns([1, 1.6, 1])
    with col2:
        st.markdown("""<div class='unified-auth-card'>
            <h2 style='text-align:center; margin-bottom:30px; font-weight:800; font-size: 1.9rem; white-space: nowrap;'>👋 Đăng Nhập Hệ Thống</h2>
        """, unsafe_allow_html=True)
        
        col_gh, col_dc, col_fb = st.columns(3)
        with col_gh:
            try: st.link_button("🐙 GitHub", url=f"https://github.com/login/oauth/authorize?client_id={st.secrets['GITHUB_CLIENT_ID']}&scope=read:user&state=github", use_container_width=True)
            except: st.button("🐙 GitHub", disabled=True, use_container_width=True)
        with col_dc:
            try: st.link_button("🎮 Discord", url=f"https://discord.com/api/oauth2/authorize?client_id={st.secrets['DISCORD_CLIENT_ID']}&redirect_uri=https://gordon-rox.streamlit.app/&response_type=code&scope=identify&state=discord", use_container_width=True)
            except: st.button("🎮 Discord", disabled=True, use_container_width=True)
        with col_fb:
            try: st.link_button("📘 Facebook", url=f"https://www.facebook.com/v19.0/dialog/oauth?client_id={st.secrets['FACEBOOK_CLIENT_ID']}&redirect_uri=https://gordon-rox.streamlit.app/&state=facebook&scope=public_profile", use_container_width=True)
            except: st.button("📘 Facebook", disabled=True, use_container_width=True)

        st.markdown("<div style='margin: 25px 0; font-size: 0.85em; text-align:center; letter-spacing: 1px;'>— HOẶC TÀI KHOẢN GORDON ROX —</div>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            user_in = st.text_input("Tài khoản", placeholder="Username")
            pass_in = st.text_input("Mật khẩu", type="password", placeholder="••••••")
            st.write("") 
            if st.form_submit_button("🚀 Vào Bếp Ngay", use_container_width=True):
                users = load_db(USER_DB)
                if user_in in users and users[user_in]["password"] == hash_pass(pass_in):
