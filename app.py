import streamlit as st
import google.generativeai as genai
import requests  # <-- Thư viện xử lý việc đăng nhập GitHub
from utils import init_system, hash_pass, load_db, save_db, USER_DB
from datetime import datetime

st.set_page_config(page_title="Gordon Rox - Trang chủ", page_icon="🏠", layout="wide")
init_system()

# ==========================================
# 🚀 XỬ LÝ ĐĂNG NHẬP GITHUB NGẦM
# ==========================================
query_params = st.query_params
if "code" in query_params:
    code = query_params["code"]
    st.query_params.clear() # Xóa URL rác cho đẹp web
    
    # 1. Đổi code lấy Access Token từ GitHub
    token_url = "https://github.com/login/oauth/access_token"
    data = {
        "client_id": st.secrets["GITHUB_CLIENT_ID"],
        "client_secret": st.secrets["GITHUB_CLIENT_SECRET"],
        "code": code
    }
    headers = {"Accept": "application/json"}
    res = requests.post(token_url, data=data, headers=headers)
    
    if res.status_code == 200:
        access_token = res.json().get("access_token")
        if access_token:
            # 2. Dùng Token xin tên người dùng
            user_url = "https://api.github.com/user"
            user_headers = {"Authorization": f"token {access_token}"}
            user_res = requests.get(user_url, headers=user_headers)
            
            if user_res.status_code == 200:
                github_user = user_res.json()
                username = github_user.get("login")
                
                # 3. Tạo tài khoản trong Database nếu chưa có
                users = load_db(USER_DB)
                if username not in users:
                    users[username] = {"password": "github_oauth_user", "fridge": []}
                    save_db(USER_DB, users)
                
                # 4. Đăng nhập thành công!
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.user_data = users[username]
                st.rerun()

# ==========================================
# 🎨 CSS (ĐÃ SỬA LỖI CHỮ TRẮNG TRÊN NỀN TRẮNG)
# ==========================================
st.markdown("""
    <style>
    .pricing-card { 
        background-color: white; 
        color: #222222; /* Bắt buộc chữ màu đen/xám đậm */
        padding: 25px; 
        border-radius: 12px; 
        text-align: center; 
        box-shadow: 0 4px 8px rgba(0,0,0,0.1); 
        margin-bottom: 20px; 
        border: 1px solid #eaeaea; 
    }
    .pricing-card h4 { color: #333333; }
    .pricing-card p { color: #555555; }
    .pricing-pro { border: 2px solid #ff7e5f; transform: scale(1.02); box-shadow: 0 8px 16px rgba(255,126,95,0.2); }
    .price { font-size: 2.5em; color: #ff7e5f; font-weight: 900; margin: 10px 0; }
    </style>
""", unsafe_allow_html=True)

st.title("👨‍🍳 GORDON ROX - HỆ THỐNG TRỢ LÝ BẾP ĐỘC QUYỀN")
st.markdown("---")

col_preview, col_auth = st.columns([1.5, 1], gap="large")

# ==========================================
# CỘT TRÁI: DÙNG THỬ & BẢNG GIÁ DỊCH VỤ
# ==========================================
with col_preview:
    tab_try, tab_pricing = st.tabs(["💡 Trải nghiệm AI", "💎 Gói Dịch Vụ (Pricing)"])
    
    with tab_try:
        st.caption("Khách vãng lai chỉ có thể hỏi công thức bằng chữ. Đăng nhập để mở khóa tính năng Phân tích Hình Ảnh!")
        if "preview_chat" not in st.session_state: st.session_state.preview_chat = []
        for msg in st.session_state.preview_chat:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
        prompt = st.chat_input("Hỏi thử công thức nấu ăn bằng chữ...")
        if prompt:
            st.session_state.preview_chat.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Gordon Rox đang suy nghĩ..."):
                    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction="Bạn là đầu bếp. Trả lời ngắn. Bắt buộc người dùng phải đăng nhập để được gửi ảnh.")
                    res = model.generate_content(prompt)
                    st.markdown(res.text)
                    st.session_state.preview_chat.append({"role": "assistant", "content": res.text})

    with tab_pricing:
        st.subheader("Nâng cấp căn bếp của bạn")
        p_col1, p_col2 = st.columns(2)
        
        with p_col1:
            st.markdown("""
            <div class='pricing-card'>
                <h4>Phụ Bếp (Free)</h4>
                <div class='price'>$0</div>
                <hr><p>✔️ Chat văn bản</p><p>❌ Nhận diện hình ảnh</p>
                <button style='width:100%; padding:8px; border-radius:5px; border:1px solid #ccc; color:#222; font-weight:bold;'>Đang Dùng</button>
            </div>
            """, unsafe_allow_html=True)
            
        with p_col2:
            st.markdown("""
            <div class='pricing-card pricing-pro'>
                <h4 style='color:#ff7e5f;'>Bếp Trưởng (Pro)</h4>
                <div class='price'>$4.99</div>
                <hr><p>✔️ Mở khóa <b>Tất cả tính năng</b></p><p>✔️ Phân tích độ tươi & Tủ lạnh</p>
                <button style='width:100%; padding:8px; border-radius:5px; background:#ff7e5f; color:white; border:none; font-weight:bold;'>Nâng Cấp Ngay</button>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# CỘT PHẢI: HỆ THỐNG ĐĂNG NHẬP / GITHUB AUTH
# ==========================================
with col_auth:
    if st.session_state.logged_in:
        st.success(f"🎉 Xin chào, **{st.session_state.username}**!")
        st.info("Trạng thái tài khoản: **Gói Bếp Trưởng VIP**")
        st.write("Bạn đã mở khóa các tính năng V.I.P. Hãy chọn menu bên trái để vào bếp!")
        if st.button("🔴 Đăng Xuất", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    else:
        st.subheader("🔐 Đăng Nhập Hệ Thống")
        
        # --- NÚT GITHUB XỊN SÒ (KHÔNG LỖI) ---
        try:
            client_id = st.secrets["GITHUB_CLIENT_ID"]
            auth_url = f"https://github.com/login/oauth/authorize?client_id={client_id}&scope=read:user"
            
            # Dùng nút link_button chính hãng của Streamlit
            st.link_button("🐙 Tiếp tục với GitHub", url=auth_url, use_container_width=True, type="primary")
            
        except KeyError:
            st.error("⚠️ Lỗi: Bạn chưa gắn GITHUB_CLIENT_ID vào két sắt (Secrets) của Streamlit.")

        st.markdown("<div style='text-align: center; color: gray; margin: 15px 0;'>— Hoặc dùng tài khoản truyền thống —</div>", unsafe_allow_html=True)
        
        # --- ĐĂNG NHẬP THỦ CÔNG ---
        with st.form("login_form"):
            user_in = st.text_input("Tên đăng nhập")
            pass_in = st.text_input("Mật khẩu", type="password")
            if st.form_submit_button("Đăng Nhập", use_container_width=True):
                users = load_db(USER_DB)
                if user_in in users and users[user_in]["password"] == hash_pass(pass_in):
                    st.session_state.logged_in = True
                    st.session_state.username = user_in
                    st.session_state.user_data = users[user_in]
                    st.rerun()
                else:
                    st.error("Sai tài khoản hoặc mật khẩu!")