import streamlit as st
import google.generativeai as genai
import requests
from utils import init_system, hash_pass, load_db, save_db, USER_DB

# Cấu hình trang: Sidebar mở sẵn, giao diện Wide
st.set_page_config(page_title="Gordon Rox | AI Culinary", page_icon="✨", layout="wide", initial_sidebar_state="expanded")
init_system()

# Khởi tạo máy trạng thái
if "auth_view" not in st.session_state: st.session_state.auth_view = "home"
if "preview_chat" not in st.session_state: st.session_state.preview_chat = []

# ==========================================
# 🎨 CSS MAGIC - CHUẨN VENICE AI / GEMINI
# ==========================================
st.markdown("""
    <style>
    /* Nền tối gradient sâu, sang trọng */
    .stApp { background: linear-gradient(135deg, #090e17 0%, #161230 100%); color: #f8fafc; }
    header {visibility: hidden;}
    
    /* Sidebar làm mờ */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.4);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255,255,255,0.05);
    }
    .sidebar-logo { font-size: 1.5rem; font-weight: 900; background: -webkit-linear-gradient(45deg, #f97316, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 20px; }

    /* ==========================================
       🌟 THIẾT KẾ CARD TÁC VỤ SIÊU MƯỢT 
       ========================================== */
    .glass-card-btn {
        background: rgba(30, 41, 59, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 25px 15px;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        cursor: pointer;
    }
    /* Hiệu ứng nổi bật khi di chuột vào Thẻ */
    .glass-card-btn:hover {
        background: rgba(45, 55, 72, 0.8);
        border-color: rgba(249, 115, 22, 0.4);
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .glass-card-icon { font-size: 2.5rem; margin-bottom: 12px; }
    .glass-card-title { font-weight: 600; font-size: 1.15rem; color: #ffffff; }
    .glass-card-subtitle { color:#94a3b8; font-size:0.9em; margin-top:6px; font-weight:400; }

    /* ========================================== */

    /* Các phần tử Auth */
    .auth-box { background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(20px); border: 1px solid #334155; border-radius: 20px; padding: 40px; box-shadow: 0 10px 40px rgba(0,0,0,0.5); text-align: center; }
    
    /* Hệ thống nút bấm */
    .stButton>button { border-radius: 8px; font-weight: 600; transition: all 0.3s ease; }
    .btn-primary>div>button { background: linear-gradient(90deg, #f97316, #ec4899); color: white; border: none; padding: 8px 16px; }
    .btn-primary>div>button:hover { opacity: 0.9; box-shadow: 0 0 15px rgba(249, 115, 22, 0.4); }
    .btn-outline>div>button { background: transparent; color: #f8fafc; border: 1px solid rgba(255,255,255,0.3); padding: 8px 16px; }
    .btn-outline>div>button:hover { border-color: #f97316; color: #f97316; background: rgba(255,255,255,0.05); }

    /* Chat Input */
    .stChatInputContainer { border-radius: 12px; border: 1px solid rgba(255,255,255,0.1) !important; background: rgba(0,0,0,0.3) !important; padding-bottom: 10px; }
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
    try:
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
                st.session_state.auth_view = "home"
                st.rerun()
    except: pass

# ==========================================
# 📱 THANH BÊN (SIDEBAR)
# ==========================================
with st.sidebar:
    st.markdown("<div class='sidebar-logo'>👨‍🍳 Gordon Rox AI</div>", unsafe_allow_html=True)

# ==========================================
# 🔝 THANH ĐIỀU HƯỚNG TRÊN CÙNG (TOP NAV)
# ==========================================
col_space, col_new_chat, col_user = st.columns([6, 1.5, 1.5], gap="small")

with col_new_chat:
    st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
    if st.button("✨ Cuộc trò chuyện mới", use_container_width=True):
        st.session_state.preview_chat = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col_user:
    if st.session_state.logged_in:
        with st.popover(f"👤 {st.session_state.username}"):
            st.write(f"Xin chào, **{st.session_state.username}**!")
            st.markdown('<div class="btn-outline">', unsafe_allow_html=True)
            if st.button("Đăng Xuất", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.auth_view = "home"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="btn-outline">', unsafe_allow_html=True)
        if st.button("Sign In / Up", use_container_width=True):
            st.session_state.auth_view = "login"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 🖥️ NỘI DUNG CHÍNH (MAIN CONTENT ROUTING)
# ==========================================

if st.session_state.auth_view == "home":
    greeting_name = st.session_state.username if st.session_state.logged_in else "Bạn"
    st.markdown(f"<h1 style='text-align: center; font-size: 3rem; margin: 20px 0 40px;'>Xin chào, {greeting_name}! <br>Hôm nay chúng ta nấu gì nhỉ?</h1>", unsafe_allow_html=True)

    col_q1, col_q2, col_q3 = st.columns(3, gap="medium")
    
    # 🛠️ NÂNG CẤP: THẺ BẤM LIỀN MẠCH, KHÔNG CÓ NÚT THỪA
    def quick_action_card(col, icon, title, subtitle, target_url):
        with col:
            # Bao bọc toàn bộ thẻ bằng thẻ <a> để click chuyển trang trực tiếp
            st.markdown(f"""
            <a href="{target_url}" target="_self" style="text-decoration: none; color: inherit; display: block;">
                <div class="glass-card-btn">
                    <div class="glass-card-icon">{icon}</div>
                    <div class="glass-card-title">{title}</div>
                    <div class="glass-card-subtitle">{subtitle}</div>
                </div>
            </a>
            """, unsafe_allow_html=True)

    # Khớp đúng URL của Streamlit (Tự động bỏ số và .py)
    quick_action_card(col_q1, "📸", "Phân tích món ăn", "Tải ảnh lên để AI nhận diện", "Dau_Bep_AI")
    quick_action_card(col_q2, "❄️", "Kiểm tra tủ lạnh", "Xem bạn đang còn nguyên liệu gì", "Tu_Lanh")
    quick_action_card(col_q3, "🌍", "Cộng đồng ẩm thực", "Khám phá công thức từ mọi người", "Dien_Dan")

    st.write("<br><br>", unsafe_allow_html=True)

    # Khung Chat dưới cùng
    chat_container = st.container(height=350)
    with chat_container:
        if not st.session_state.preview_chat:
             st.markdown("<div style='text-align: center; color: gray; margin-top: 130px;'>Nhập câu hỏi bên dưới để bắt đầu trò chuyện nhanh...</div>", unsafe_allow_html=True)
        for msg in st.session_state.preview_chat:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
    prompt = st.chat_input("Hỏi nhanh Gordon Rox (VD: Gợi ý bữa tối nhanh gọn)...")
    if prompt:
        st.session_state.preview_chat.append({"role": "user", "content": prompt})
        st.rerun()

    if len(st.session_state.preview_chat) > 0 and st.session_state.preview_chat[-1]["role"] == "user":
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("Đang suy nghĩ..."):
                    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction="Bạn là trợ lý bếp. Trả lời ngắn gọn, hữu ích. Khuyến khích người dùng dùng các tính năng nâng cao ở menu bên trái.")
                    res = model.generate_content(st.session_state.preview_chat[-1]["content"])
                    st.markdown(res.text)
                    st.session_state.preview_chat.append({"role": "assistant", "content": res.text})

# --- TRANG ĐĂNG NHẬP (LOGIN) ---
elif st.session_state.auth_view == "login":
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
        st.markdown("<h2>👋 Chào mừng trở lại</h2>", unsafe_allow_html=True)
        try:
            client_id = st.secrets["GITHUB_CLIENT_ID"]
            auth_url = f"https://github.com/login/oauth/authorize?client_id={client_id}&scope=read:user"
            st.link_button("🐙 Tiếp tục với GitHub", url=auth_url, use_container_width=True)
        except: pass
        st.markdown("<div style='margin: 15px 0; color: gray; font-size: 0.8em;'>HOẶC</div>", unsafe_allow_html=True)
        with st.form("login_form"):
            user_in = st.text_input("Tài khoản", placeholder="Nhập username...")
            pass_in = st.text_input("Mật khẩu", type="password")
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
                else: st.error("Sai thông tin!")
        st.write("---")
        col_reg, col_home = st.columns(2)
        with col_reg: 
            st.markdown('<div class="btn-outline">', unsafe_allow_html=True)
            if st.button("Đăng ký mới"): st.session_state.auth_view = "signup"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with col_home:
            st.markdown('<div class="btn-outline">', unsafe_allow_html=True)
            if st.button("← Trang Chủ"): st.session_state.auth_view = "home"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- TRANG ĐĂNG KÝ (SIGN UP) ---
elif st.session_state.auth_view == "signup":
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
        st.markdown("<h2 style='color:#f97316;'>🚀 Tạo tài khoản mới</h2>", unsafe_allow_html=True)
        with st.form("signup_form"):
            new_user = st.text_input("Tài khoản mới", placeholder="Chọn username...")
            new_pass = st.text_input("Mật khẩu", type="password", placeholder="Tối thiểu 4 ký tự")
            st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
            submit = st.form_submit_button("Đăng Ký Ngay")
            st.markdown('</div>', unsafe_allow_html=True)
            if submit:
                users = load_db(USER_DB)
                if new_user in users: st.error("Tên đã tồn tại!")
                elif len(new_pass) < 4: st.error("Mật khẩu quá ngắn!")
                else:
                    users[new_user] = {"password": hash_pass(new_pass), "fridge": []}
                    save_db(USER_DB, users)
                    st.success("Tạo thành công! Vui lòng đăng nhập.")
                    st.session_state.auth_view = "login"
                    st.rerun()
        st.write("---")
        col_log, col_home = st.columns(2)
        with col_log:
             st.markdown('<div class="btn-outline">', unsafe_allow_html=True)
             if st.button("Đã có tài khoản?"): st.session_state.auth_view = "login"; st.rerun()
             st.markdown('</div>', unsafe_allow_html=True)
        with col_home:
             st.markdown('<div class="btn-outline">', unsafe_allow_html=True)
             if st.button("← Trang Chủ"): st.session_state.auth_view = "home"; st.rerun()
             st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
