import streamlit as st
import google.generativeai as genai
import requests
from utils import init_system, hash_pass, load_db, save_db, USER_DB

# Cấu hình trang: Giao diện rộng, Sidebar luôn mở
st.set_page_config(page_title="Gordon Rox | Venice UI", page_icon="✨", layout="wide", initial_sidebar_state="expanded")
init_system()

if "auth_view" not in st.session_state: st.session_state.auth_view = "home"
if "preview_chat" not in st.session_state: st.session_state.preview_chat = []

# ==========================================
# 🎨 CSS MAGIC - CHUẨN VENICE AI (FIX LỖI PHÔNG)
# ==========================================
st.markdown("""
    <style>
    /* Đổi toàn bộ font chữ sang Inter (Chuẩn UI quốc tế) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Playfair+Display:ital,wght@1,600&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif !important;
    }

    /* Nền tối sâu và sang trọng */
    .stApp { background-color: #0f1115; color: #f8fafc; }
    header {visibility: hidden;}
    
    /* Ẩn hoàn toàn Menu xấu xí mặc định của Streamlit */
    [data-testid="stSidebarNav"] { display: none !important; }

    /* ==========================================
       🌟 THIẾT KẾ SIDEBAR (GIỐNG VENICE AI)
       ========================================== */
    [data-testid="stSidebar"] {
        background-color: #16181d;
        border-right: 1px solid #272a30;
    }
    
    /* Logo Font Serif sang trọng giống chữ "Venice" */
    .sidebar-logo { 
        font-family: 'Playfair Display', serif; 
        font-size: 2rem; 
        color: #e2e8f0; 
        margin-bottom: 30px; 
        padding-left: 10px;
        font-style: italic;
    }

    /* Đẩy phần User Profile xuống đáy Sidebar */
    .sidebar-bottom-spacer { flex-grow: 1; min-height: 40vh; }
    
    .user-profile-box {
        background-color: #1e2026;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #272a30;
        margin-top: auto;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }

    /* ==========================================
       🌟 FIX LỖI PHÔNG & GIAO DIỆN CHAT
       ========================================== */
    /* Ghi đè nền trắng của khung chat */
    .stChatInput { background-color: transparent !important; padding-bottom: 20px; }
    .stChatInputContainer { 
        background-color: #1e2026 !important; 
        border: 1px solid #333842 !important; 
        border-radius: 16px !important; 
    }
    .stChatInputContainer:focus-within { border-color: #f97316 !important; }
    .stChatInputContainer textarea { color: #f8fafc !important; }
    .stChatInputContainer textarea::placeholder { color: #64748b !important; }

    /* ==========================================
       🌟 THẺ TÁC VỤ (QUICK ACTIONS) ĐÃ LÀM ĐẸP
       ========================================== */
    .glass-card-btn {
        background: #16181d;
        border: 1px solid #272a30;
        border-radius: 16px;
        padding: 25px 15px;
        text-align: center;
        transition: all 0.2s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        cursor: pointer;
    }
    .glass-card-btn:hover {
        background: #1e2026;
        border-color: #f97316;
        transform: translateY(-3px);
    }
    .glass-card-icon { font-size: 2.2rem; margin-bottom: 15px; }
    .glass-card-title { font-weight: 600; font-size: 1.1rem; color: #f8fafc; }
    .glass-card-subtitle { color:#64748b; font-size:0.85em; margin-top:8px; }

    /* Buttons */
    .btn-new-chat>div>button { background: transparent; border: 1px solid #333842; color: #f8fafc; border-radius: 20px; padding: 5px 15px; float: right;}
    .btn-new-chat>div>button:hover { border-color: #f8fafc; }
    
    .btn-primary>div>button { background: #f97316; color: white; border: none; border-radius: 8px; width: 100%; }
    .btn-primary>div>button:hover { background: #ea580c; }
    .btn-outline>div>button { background: transparent; border: 1px solid #333842; color: #e2e8f0; width: 100%; border-radius: 8px;}
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
    try:
        token_url = "https://github.com/login/oauth/access_token"
        res = requests.post(token_url, data={"client_id": st.secrets["GITHUB_CLIENT_ID"], "client_secret": st.secrets["GITHUB_CLIENT_SECRET"], "code": code}, headers={"Accept": "application/json"})
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
                st.session_state.auth_view = "home"
                st.rerun()
    except: pass

# ==========================================
# 📱 THANH BÊN (SIDEBAR CẤU TRÚC MỚI)
# ==========================================
with st.sidebar:
    # 1. Logo phong cách Venice
    st.markdown("<div class='sidebar-logo'>Gordon Rox</div>", unsafe_allow_html=True)
    
    # 2. Thanh Menu Tự Chế (Đẹp & Sạch)
    st.page_link("app.py", label="Trang chủ", icon="🏠")
    st.page_link("pages/1_🍳_Dau_Bep_AI.py", label="Phân tích món ăn", icon="🍳")
    st.page_link("pages/2_❄️_Tu_Lanh.py", label="Quản lý Tủ lạnh", icon="❄️")
    st.page_link("pages/3_🌍_Dien_Dan.py", label="Mạng xã hội", icon="🌍")
    
    # 3. Khoảng trống đẩy User Profile xuống đáy
    st.markdown("<div class='sidebar-bottom-spacer'></div>", unsafe_allow_html=True)
    
    # 4. Khu vực User Profile (Đáy Sidebar)
    st.markdown("<div class='user-profile-box'>", unsafe_allow_html=True)
    if st.session_state.logged_in:
        st.markdown(f"<div style='font-weight: 600; font-size:1.1em;'>👤 {st.session_state.username}</div>", unsafe_allow_html=True)
        st.markdown('<div class="btn-outline">', unsafe_allow_html=True)
        if st.button("Đăng Xuất"):
            st.session_state.logged_in = False
            st.session_state.auth_view = "home"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("<div style='color: #94a3b8; font-size: 0.9em; text-align: center;'>Bạn chưa đăng nhập</div>", unsafe_allow_html=True)
        st.markdown('<div class="btn-outline">', unsafe_allow_html=True)
        if st.button("Đăng nhập / Đăng ký"):
            st.session_state.auth_view = "login"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 🔝 GÓC TRÊN CÙNG BÊN PHẢI (NEW CHAT)
# ==========================================
if st.session_state.auth_view == "home":
    col_empty, col_new = st.columns([8, 2])
    with col_new:
        st.markdown('<div class="btn-new-chat">', unsafe_allow_html=True)
        if st.button("📝 New chat"):
            st.session_state.preview_chat = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 🖥️ NỘI DUNG CHÍNH 
# ==========================================
if st.session_state.auth_view == "home":
    greeting_name = st.session_state.username if st.session_state.logged_in else "Bạn"
    st.markdown(f"<h1 style='text-align: center; font-size: 2.8rem; margin: 10px 0 40px; font-weight: 800;'>Xin chào, {greeting_name}!<br>Hôm nay chúng ta nấu gì nhỉ?</h1>", unsafe_allow_html=True)

    # 3 Thẻ chức năng bọc bằng thẻ <a>
    col_q1, col_q2, col_q3 = st.columns(3, gap="medium")
    def quick_action_card(col, icon, title, subtitle, target_url):
        with col:
            st.markdown(f"""
            <a href="{target_url}" target="_self" style="text-decoration: none; color: inherit; display: block;">
                <div class="glass-card-btn">
                    <div class="glass-card-icon">{icon}</div>
                    <div class="glass-card-title">{title}</div>
                    <div class="glass-card-subtitle">{subtitle}</div>
                </div>
            </a>
            """, unsafe_allow_html=True)

    quick_action_card(col_q1, "📸", "Phân tích món ăn", "Tải ảnh lên để AI nhận diện", "Dau_Bep_AI")
    quick_action_card(col_q2, "❄️", "Kiểm tra tủ lạnh", "Xem bạn đang còn nguyên liệu gì", "Tu_Lanh")
    quick_action_card(col_q3, "🌍", "Cộng đồng ẩm thực", "Khám phá công thức từ mọi người", "Dien_Dan")

    st.write("<br><br>", unsafe_allow_html=True)

    # Khung Chat dùng thử (Đã sửa lỗi nền trắng)
    chat_container = st.container(height=350)
    with chat_container:
        if not st.session_state.preview_chat:
             st.markdown("<div style='text-align: center; color: #333842; margin-top: 130px; font-weight: 600;'>Nhập câu hỏi bên dưới để bắt đầu...</div>", unsafe_allow_html=True)
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
                    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction="Trả lời ngắn gọn, hữu ích. Khuyên dùng các chức năng bên menu trái.")
                    res = model.generate_content(st.session_state.preview_chat[-1]["content"])
                    st.markdown(res.text)
                    st.session_state.preview_chat.append({"role": "assistant", "content": res.text})

# --- TRANG ĐĂNG NHẬP / ĐĂNG KÝ (Giữ nguyên logic bảo mật) ---
elif st.session_state.auth_view == "login":
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div class='auth-box'><h2>👋 Đăng nhập</h2>", unsafe_allow_html=True)
        try:
            client_id = st.secrets["GITHUB_CLIENT_ID"]
            auth_url = f"https://github.com/login/oauth/authorize?client_id={client_id}&scope=read:user"
            st.link_button("🐙 Tiếp tục với GitHub", url=auth_url, use_container_width=True)
        except: pass
        st.markdown("<div style='margin: 15px 0; color: #64748b; font-size: 0.8em;'>HOẶC</div>", unsafe_allow_html=True)
        with st.form("login_form"):
            user_in = st.text_input("Tài khoản")
            pass_in = st.text_input("Mật khẩu", type="password")
            st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
            if st.form_submit_button("Vào bếp"):
                users = load_db(USER_DB)
                if user_in in users and users[user_in]["password"] == hash_pass(pass_in):
                    st.session_state.logged_in = True
                    st.session_state.username = user_in
                    st.session_state.user_data = users[user_in]
                    st.session_state.auth_view = "home"
                    st.rerun()
                else: st.error("Sai thông tin!")
            st.markdown('</div>', unsafe_allow_html=True)
        st.write("---")
        c1, c2 = st.columns(2)
        with c1: 
            st.markdown('<div class="btn-outline">', unsafe_allow_html=True)
            if st.button("Tạo tài khoản"): st.session_state.auth_view = "signup"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="btn-outline">', unsafe_allow_html=True)
            if st.button("← Quay lại"): st.session_state.auth_view = "home"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.auth_view == "signup":
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div class='auth-box'><h2 style='color:#f97316;'>🚀 Đăng ký</h2>", unsafe_allow_html=True)
        with st.form("signup_form"):
            new_user = st.text_input("Tài khoản mới")
            new_pass = st.text_input("Mật khẩu", type="password")
            st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
            if st.form_submit_button("Đăng ký ngay"):
                users = load_db(USER_DB)
                if new_user in users: st.error("Tên đã tồn tại!")
                elif len(new_pass) < 4: st.error("Mật khẩu quá ngắn!")
                else:
                    users[new_user] = {"password": hash_pass(new_pass), "fridge": []}
                    save_db(USER_DB, users)
                    st.success("Tạo thành công!")
                    st.session_state.auth_view = "login"
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.write("---")
        c1, c2 = st.columns(2)
        with c1:
             st.markdown('<div class="btn-outline">', unsafe_allow_html=True)
             if st.button("Đã có tài khoản"): st.session_state.auth_view = "login"; st.rerun()
             st.markdown('</div>', unsafe_allow_html=True)
        with c2:
             st.markdown('<div class="btn-outline">', unsafe_allow_html=True)
             if st.button("← Quay lại"): st.session_state.auth_view = "home"; st.rerun()
             st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

