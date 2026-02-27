import streamlit as st
import google.generativeai as genai
import requests
from utils import init_system, hash_pass, load_db, save_db, USER_DB
from ui import apply_theme, render_sidebar # GỌI GIAO DIỆN VÀO

st.set_page_config(page_title="Gordon Rox | AI Culinary", page_icon="🧑‍🍳", layout="wide", initial_sidebar_state="expanded")
init_system()

if "auth_view" not in st.session_state: st.session_state.auth_view = "home"
if "preview_chat" not in st.session_state: st.session_state.preview_chat = []

apply_theme()    # Bật CSS màu sắc
render_sidebar() # Hiện Thanh Menu bên trái

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
            data = {"client_id": st.secrets["DISCORD_CLIENT_ID"], "client_secret": st.secrets["DISCORD_CLIENT_SECRET"], "grant_type": "authorization_code", "code": code, "redirect_uri": "https://gordonrox.streamlit.app/"}
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
            params = {"client_id": st.secrets["FACEBOOK_CLIENT_ID"], "redirect_uri": "https://gordonrox.streamlit.app/", "client_secret": st.secrets["FACEBOOK_CLIENT_SECRET"], "code": code}
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
    # CSS ép riêng cho 3 nút ở trang chủ
    sidebar_bg = "#16181d" if st.session_state.get("theme_mode", "Dark") == "Dark" else "#f8fafc"
    card_bg = "#1e2026" if st.session_state.get("theme_mode", "Dark") == "Dark" else "#f8fafc"
    border_color = "#272a30" if st.session_state.get("theme_mode", "Dark") == "Dark" else "#e2e8f0"
    text_color = "#f8fafc" if st.session_state.get("theme_mode", "Dark") == "Dark" else "#1e293b"
    
    st.markdown(f"""
        <style>
        div[data-testid="column"] .stButton > button {{
            height: 90px !important; border-radius: 16px !important; font-size: 1.2rem !important;
            background-color: {card_bg} !important; border: 1px solid {border_color} !important;
            display: flex !important; align-items: center !important; justify-content: center !important;
            color: {text_color} !important;
        }}
        div[data-testid="column"] .stButton > button:hover {{ border-color: #f97316 !important; transform: translateY(-3px) !important; color: #f97316 !important; }}
        </style>
    """, unsafe_allow_html=True)

    greeting_name = st.session_state.username if st.session_state.get("logged_in") else "Bạn"
    st.markdown(f"<h1 style='text-align: center; font-size: 3rem; margin: 10px 0 10px; font-weight: 800;'>Xin chào, <span style='color:#f97316;'>{greeting_name}</span>!</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center; font-weight: 400; margin-bottom: 40px; color:#64748b;'>Hôm nay chúng ta nấu gì nhỉ?</h3>", unsafe_allow_html=True)
    
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
    
    # CHATBOT AI GEMINI
    chat_container = st.container(height=350)
    with chat_container:
        if not st.session_state.preview_chat: 
            st.markdown("<div style='text-align: center; margin-top: 130px; font-weight: 400; color:#64748b;'>Nhập nguyên liệu bạn đang có vào đây...</div>", unsafe_allow_html=True)
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
                    try:
                        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction="Trả lời ngắn gọn, ngầu như đầu bếp.")
                        res = model.generate_content(st.session_state.preview_chat[-1]["content"])
                        st.markdown(res.text)
                        st.session_state.preview_chat.append({"role": "assistant", "content": res.text})
                    except Exception as e:
                        st.error("Hệ thống AI đang bảo trì hoặc chưa nhập API Key!")

# ============================================================
# 🔥 GIAO DIỆN ĐĂNG NHẬP 
# ==========================================
elif st.session_state.auth_view == "login":
    col1, col2, col3 = st.columns([1, 1.6, 1])
    with col2:
        st.markdown("""<div class='unified-auth-card'><h2 style='text-align:center; margin-bottom:30px; font-weight:800;'>👋 Đăng Nhập Hệ Thống</h2>""", unsafe_allow_html=True)
        
        col_gh, col_dc, col_fb = st.columns(3)
        with col_gh:
            try: st.link_button("🐙 GitHub", url=f"https://github.com/login/oauth/authorize?client_id={st.secrets['GITHUB_CLIENT_ID']}&scope=read:user&state=github", use_container_width=True)
            except: st.button("🐙 GitHub", disabled=True, use_container_width=True)
        with col_dc:
            try: st.link_button("🎮 Discord", url=f"https://discord.com/api/oauth2/authorize?client_id={st.secrets['DISCORD_CLIENT_ID']}&redirect_uri=https://gordonrox.streamlit.app/&response_type=code&scope=identify&state=discord", use_container_width=True)
            except: st.button("🎮 Discord", disabled=True, use_container_width=True)
        with col_fb:
            try: st.link_button("📘 Facebook", url=f"https://www.facebook.com/v19.0/dialog/oauth?client_id={st.secrets['FACEBOOK_CLIENT_ID']}&redirect_uri=https://gordonrox.streamlit.app/&state=facebook&scope=public_profile", use_container_width=True)
            except: st.button("📘 Facebook", disabled=True, use_container_width=True)

        st.markdown("<div style='margin: 25px 0; font-size: 0.85em; text-align:center; color:#64748b;'>— HOẶC TÀI KHOẢN GORDON ROX —</div>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            user_in = st.text_input("Tài khoản", placeholder="Username")
            pass_in = st.text_input("Mật khẩu", type="password", placeholder="••••••")
            st.write("") 
            if st.form_submit_button("🚀 Vào Bếp Ngay", use_container_width=True):
                users = load_db(USER_DB)
                if user_in in users and users[user_in]["password"] == hash_pass(pass_in):
                    st.session_state.logged_in = True
                    st.session_state.username = user_in
                    st.session_state.user_data = users[user_in]
                    st.session_state.auth_view = "home"
                    st.rerun()
                else: st.error("Thông tin không chính xác!")
        
        st.markdown(f"<hr style='border-color:rgba(150,150,150,0.2); margin: 25px 0;'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: 
            if st.button("✨ Tạo tài khoản mới", use_container_width=True): st.session_state.auth_view = "signup"; st.rerun()
        with c2:
            if st.button("← Về Trang chủ", use_container_width=True): st.session_state.auth_view = "home"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# 🔥 GIAO DIỆN ĐĂNG KÝ
# ============================================================
elif st.session_state.auth_view == "signup":
    col1, col2, col3 = st.columns([1, 1.6, 1])
    with col2:
        st.markdown("""<div class='unified-auth-card'><h2 style='text-align:center; margin-bottom:10px; font-weight:800; color:#f97316;'>🚀 Tạo Tài Khoản Mới</h2><p style='text-align:center; margin-bottom:30px; color:#64748b;'>Gia nhập cộng đồng đầu bếp AI ngay hôm nay.</p>""", unsafe_allow_html=True)
        
        with st.form("signup_form"):
            new_user = st.text_input("Tài khoản mong muốn", placeholder="Ví dụ: chef_alex")
            new_pass = st.text_input("Mật khẩu", type="password", placeholder="Tối thiểu 4 ký tự")
            st.write("")
            if st.form_submit_button("✨ Đăng Ký Ngay", use_container_width=True):
                users = load_db(USER_DB)
                if new_user in users: st.error("Tên này đã có người dùng!")
                elif len(new_pass) < 4: st.error("Mật khẩu hơi ngắn, thêm chút nữa đi!")
                else:
                    users[new_user] = {"password": hash_pass(new_pass), "fridge": []}
                    save_db(USER_DB, users)
                    st.success("Tuyệt vời! Đang chuyển sang đăng nhập...")
                    st.session_state.auth_view = "login"
                    st.rerun()
        
        st.markdown(f"<hr style='border-color:rgba(150,150,150,0.2); margin: 25px 0;'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
             if st.button("← Đã có tài khoản", use_container_width=True): st.session_state.auth_view = "login"; st.rerun()
        with c2:
             if st.button("🏠 Về Trang chủ", use_container_width=True): st.session_state.auth_view = "home"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
