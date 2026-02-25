import streamlit as st
import google.generativeai as genai
from utils import init_system, hash_pass, load_db, save_db, USER_DB
from datetime import datetime

st.set_page_config(page_title="Gordon Rox - Trang chủ", page_icon="🏠", layout="wide")
init_system()

# --- CSS CHO BẢNG GIÁ VÀ NÚT GOOGLE ---
st.markdown("""
    <style>
    .pricing-card { background: white; padding: 25px; border-radius: 12px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #eaeaea; }
    .pricing-pro { border: 2px solid #ff7e5f; transform: scale(1.02); box-shadow: 0 8px 16px rgba(255,126,95,0.2); }
    .price { font-size: 2.5em; color: #ff7e5f; font-weight: 900; margin: 10px 0; }
    .google-btn { display: flex; align-items: center; justify-content: center; background-color: white; color: #444; border: 1px solid #ccc; padding: 10px; border-radius: 5px; cursor: pointer; font-weight: bold; margin-bottom: 15px; transition: 0.3s; }
    .google-btn:hover { background-color: #f8f9fa; border-color: #aaa; }
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
    
    # TAB 1: DÙNG THỬ
    with tab_try:
        st.caption("Khách vãng lai chỉ có thể hỏi công thức bằng chữ. Đăng nhập để mở khóa tính năng Phân tích Hình Ảnh!")
        
        if "preview_chat" not in st.session_state:
            st.session_state.preview_chat = []
            
        for msg in st.session_state.preview_chat:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
        prompt = st.chat_input("Hỏi thử công thức nấu ăn bằng chữ...")
        if prompt:
            st.session_state.preview_chat.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Gordon Rox đang suy nghĩ..."):
                    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction="Bạn là đầu bếp. Hãy trả lời ngắn gọn. Nhắc người dùng đăng nhập hoặc mua gói Pro để có thể gửi ảnh cho bạn.")
                    res = model.generate_content(prompt)
                    st.markdown(res.text)
                    st.session_state.preview_chat.append({"role": "assistant", "content": res.text})

    # TAB 2: BẢNG GIÁ
    with tab_pricing:
        st.subheader("Nâng cấp căn bếp của bạn")
        p_col1, p_col2, p_col3 = st.columns(3)
        
        with p_col1:
            st.markdown("""
            <div class='pricing-card'>
                <h4>Phụ Bếp</h4>
                <div class='price'>$0</div><p style='color:gray'>/tháng</p>
                <hr>
                <p>✔️ Chat văn bản cơ bản</p>
                <p>✔️ Xem diễn đàn cộng đồng</p>
                <p>❌ Nhận diện hình ảnh</p>
                <button style='width:100%; padding:8px; border-radius:5px; border:1px solid #ccc;'>Gói Hiện Tại</button>
            </div>
            """, unsafe_allow_html=True)
            
        with p_col2:
            st.markdown("""
            <div class='pricing-card pricing-pro'>
                <h4 style='color:#ff7e5f;'>Bếp Trưởng (Pro)</h4>
                <div class='price'>$4.99</div><p style='color:gray'>/tháng</p>
                <hr>
                <p>✔️ Mở khóa <b>Tất cả tính năng</b></p>
                <p>✔️ Phân tích độ tươi bằng ảnh</p>
                <p>✔️ Quản lý tủ lạnh thông minh</p>
                <button style='width:100%; padding:8px; border-radius:5px; background:#ff7e5f; color:white; border:none; font-weight:bold;'>Nâng Cấp Ngay</button>
            </div>
            """, unsafe_allow_html=True)
            
        with p_col3:
            st.markdown("""
            <div class='pricing-card'>
                <h4>Đầu Bếp Xanh</h4>
                <div class='price'>$9.99</div><p style='color:gray'>/tháng</p>
                <hr>
                <p>✔️ Dành cho nhà hàng/Doanh nghiệp</p>
                <p>✔️ Gợi ý tái chế không rác thải</p>
                <p>✔️ Lên thực đơn chuyên sâu</p>
                <button style='width:100%; padding:8px; border-radius:5px; border:1px solid #ccc;'>Liên Hệ</button>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# CỘT PHẢI: HỆ THỐNG ĐĂNG NHẬP / GOOGLE AUTH
# ==========================================
with col_auth:
    if st.session_state.logged_in:
        st.success(f"🎉 Xin chào, **{st.session_state.username}**!")
        st.info("Trạng thái tài khoản: **Gói Phụ Bếp (Free)**")
        st.write("Bạn đã mở khóa các tính năng cơ bản. Hãy chọn menu bên trái để vào bếp!")
        if st.button("🔴 Đăng Xuất", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    else:
        st.subheader("🔐 Mở Khóa Đặc Quyền")
        
        # --- NÚT GOOGLE LOGIN (TEMPLATE) ---
        st.markdown("""
        <div class='google-btn' onclick="alert('Tính năng đang được phát triển!')">
            <img src='https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg' width='20' style='margin-right: 10px;'/>
            Tiếp tục với Google
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("⚠️ Chạy thử Đăng nhập Google (Demo)", use_container_width=True):
            st.info("Để nút Google này hoạt động thật, hệ thống cần được cấu hình OAuth2 trên Google Cloud Console.")
        
        st.markdown("<div style='text-align: center; color: gray; margin: 10px 0;'>— Hoặc đăng nhập thủ công —</div>", unsafe_allow_html=True)
        
        # --- FORM ĐĂNG NHẬP TRUYỀN THỐNG ---
        tab_login, tab_reg = st.tabs(["Đăng Nhập", "Đăng Ký"])
        
        with tab_login:
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
                    
        with tab_reg:
            with st.form("reg_form"):
                new_user = st.text_input("Tên đăng nhập mới")
                new_pass = st.text_input("Mật khẩu mới", type="password")
                if st.form_submit_button("Tạo Tài Khoản", use_container_width=True):
                    users = load_db(USER_DB)
                    if new_user in users: st.error("Tên này đã tồn tại!")
                    elif len(new_pass) < 4: st.error("Mật khẩu quá ngắn!")
                    else:
                        users[new_user] = {"password": hash_pass(new_pass), "fridge": []}
                        save_db(USER_DB, users)
                        st.success("Tạo thành công! Hãy sang tab Đăng Nhập.")