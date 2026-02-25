import streamlit as st
import google.generativeai as genai
from utils import init_system, hash_pass, load_db, save_db, USER_DB
from datetime import datetime

st.set_page_config(page_title="Gordon Rox - Trang chủ", page_icon="🏠", layout="wide")
init_system()

st.title("👨‍🍳 GORDON ROX - HỆ THỐNG TRỢ LÝ BẾP")
st.markdown("---")

col_preview, col_auth = st.columns([1.5, 1])

# --- CỘT TRÁI: DÙNG THỬ BẢN GIỚI HẠN (PREVIEW) ---
with col_preview:
    st.subheader("💡 Trải nghiệm AI (Bản Dùng Thử)")
    st.caption("Khách vãng lai chỉ có thể hỏi bằng chữ. Đăng nhập để mở khóa tính năng Phân tích Hình Ảnh!")
    
    if "preview_chat" not in st.session_state:
        st.session_state.preview_chat = []
        
    for msg in st.session_state.preview_chat:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
        
    prompt = st.chat_input("Hỏi thử công thức nấu ăn bằng chữ...")
    if prompt:
        st.session_state.preview_chat.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Đang phản hồi bản dùng thử..."):
                model = genai.GenerativeModel('gemini-2.5-flash', system_instruction="Bạn là đầu bếp. Hãy trả lời ngắn gọn. Nhắc người dùng đăng nhập để gửi ảnh cho bạn.")
                res = model.generate_content(prompt)
                st.markdown(res.text)
                st.session_state.preview_chat.append({"role": "assistant", "content": res.text})

# --- CỘT PHẢI: HỆ THỐNG ĐĂNG NHẬP ---
with col_auth:
    if st.session_state.logged_in:
        st.success(f"🎉 Xin chào, {st.session_state.username}!")
        st.write("Bạn đã mở khóa toàn bộ tính năng. Hãy chọn các trang bên menu trái để trải nghiệm!")
        if st.button("🔴 Đăng Xuất"):
            st.session_state.logged_in = False
            st.rerun()
    else:
        st.subheader("🔐 Mở Khóa Tính Năng V.I.P")
        tab_login, tab_reg = st.tabs(["Đăng Nhập", "Đăng Ký"])
        
        with tab_login:
            user_in = st.text_input("Tên đăng nhập")
            pass_in = st.text_input("Mật khẩu", type="password")
            if st.button("Đăng Nhập", type="primary"):
                users = load_db(USER_DB)
                if user_in in users and users[user_in]["password"] == hash_pass(pass_in):
                    st.session_state.logged_in = True
                    st.session_state.username = user_in
                    st.session_state.user_data = users[user_in]
                    st.rerun()
                else:
                    st.error("Sai tài khoản hoặc mật khẩu!")
                    
        with tab_reg:
            new_user = st.text_input("Tên đăng nhập mới")
            new_pass = st.text_input("Mật khẩu mới", type="password")
            if st.button("Tạo Tài Khoản"):
                users = load_db(USER_DB)
                if new_user in users: st.error("Tên này đã tồn tại!")
                elif len(new_pass) < 4: st.error("Mật khẩu quá ngắn!")
                else:
                    users[new_user] = {"password": hash_pass(new_pass), "fridge": []}
                    save_db(USER_DB, users)
                    st.success("Tạo thành công! Hãy sang tab Đăng Nhập.")