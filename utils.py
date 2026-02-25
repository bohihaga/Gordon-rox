import streamlit as st
import google.generativeai as genai
import json
import os
import hashlib

USER_DB = "users_db.json"
FORUM_DB = "forum_messages.json"

def init_system():
    # 1. Kết nối AI an toàn
    try:
        API_KEY = st.secrets["GEMINI_API_KEY"] 
        genai.configure(api_key=API_KEY)
    except KeyError:
        st.error("⚠️ Lỗi Hệ Thống: Chưa có API Key.")
        st.stop()
        
    # 2. Tạo DB nếu chưa có
    if not os.path.exists(USER_DB):
        with open(USER_DB, "w", encoding="utf-8") as f: json.dump({}, f)
    if not os.path.exists(FORUM_DB):
        with open(FORUM_DB, "w", encoding="utf-8") as f: json.dump([], f)
        
    # 3. Biến trạng thái đăng nhập
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_db(file_name):
    with open(file_name, "r", encoding="utf-8") as f: return json.load(f)

def save_db(file_name, data):
    with open(file_name, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

# HÀM BẢO VỆ CÁC TRANG BÊN TRONG (Gác cổng)
def require_login():
    if not st.session_state.get("logged_in", False):
        st.warning("🔒 TÍNH NĂNG ĐỘC QUYỀN: Bạn cần Đăng Nhập ở Trang Chủ để sử dụng tính năng này!")
        st.info("👈 Hãy quay lại 'app' ở menu bên trái để đăng nhập nhé.")
        st.stop() # Chặn không cho code chạy tiếp
