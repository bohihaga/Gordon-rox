import streamlit as st
import google.generativeai as genai
from PIL import Image
from utils import load_db, save_db, USER_DB

st.set_page_config(page_title="Tủ Lạnh", page_icon="❄️", layout="wide", initial_sidebar_state="expanded")

# CSS VÀ SIDEBAR
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Playfair+Display:ital,wght@1,600&display=swap');
    body, p, h1, h2, h3, h4, h5, h6, span, div, input, textarea { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0f1115; color: #f8fafc; }
    header {visibility: hidden;}
    [data-testid="stSidebarNav"] { display: none !important; }
    [data-testid="stSidebar"] { background-color: #16181d; border-right: 1px solid #272a30; }
    .sidebar-logo { font-family: 'Playfair Display', serif !important; font-size: 2.2rem; color: #e2e8f0; margin-bottom: 25px; padding-left: 10px; font-style: italic; }
    .stButton>button { border-radius: 8px; font-weight: 600; transition: all 0.2s; }
    .stButton>button:hover { border-color: #f97316 !important; color: #f97316 !important; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div class='sidebar-logo'>Gordon Rox</div>", unsafe_allow_html=True)
    st.page_link("app.py", label="Trang chủ", icon="🏠")
    st.page_link("pages/1_🍳_Dau_Bep_AI.py", label="Phân tích món ăn", icon="🍳")
    st.page_link("pages/2_❄️_Tu_Lanh.py", label="Quản lý Tủ lạnh", icon="❄️")
    st.page_link("pages/3_🌍_Dien_Dan.py", label="Mạng xã hội", icon="🌍")
    st.markdown("<div style='flex-grow: 1; min-height: 45vh;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        if st.session_state.get("logged_in"):
            st.markdown(f"<div style='font-weight: 600; font-size:1.1em; margin-bottom:10px;'>👤 {st.session_state.username}</div>", unsafe_allow_html=True)
            if st.button("🔴 Đăng Xuất", use_container_width=True):
                st.session_state.logged_in = False
                st.switch_page("app.py")
        else:
            st.markdown("<div style='color: #94a3b8; font-size: 0.9em; text-align: center; margin-bottom:10px;'>Bạn chưa đăng nhập</div>", unsafe_allow_html=True)
            if st.button("🔑 Sign In / Up", type="primary", use_container_width=True):
                st.session_state.auth_view = "login"
                st.switch_page("app.py")

if not st.session_state.get("logged_in"):
    st.markdown("<h2 style='text-align:center; color:#f97316; margin-top:15vh;'>🔒 TỦ LẠNH ĐANG KHOÁ</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        if st.button("🏠 Về Trang Chủ Đăng Nhập", use_container_width=True, type="primary"):
            st.session_state.auth_view = "login"
            st.switch_page("app.py")
    st.stop()

# ==========================================
st.title(f"❄️ Tủ Lạnh Của {st.session_state.username}")
users = load_db(USER_DB)
my_fridge = users[st.session_state.username].get("fridge", [])

with st.expander("👁️ QUÉT TỦ LẠNH BẰNG AI", expanded=True):
    scan_img = st.file_uploader("Tải ảnh bên trong tủ lạnh lên", type=["jpg", "jpeg", "png"])
    if scan_img:
        img_fridge = Image.open(scan_img)
        
        # ĐÃ SỬA LỖI Ở ĐÂY: Dùng width thay cho height
        st.image(img_fridge, width=400) 
        
        if st.button("✨ Quét tự động", type="primary"):
            with st.spinner("AI đang đếm nguyên liệu..."):
                model = genai.GenerativeModel('gemini-2.5-flash')
                prompt = "Nhìn vào ảnh này, liệt kê tên các loại thực phẩm. TRẢ LỜI NGẮN GỌN BẰNG TIẾNG VIỆT, CÁCH NHAU BỞI DẤU PHẨY."
                res = model.generate_content([prompt, img_fridge])
                new_items = [item.strip().capitalize() for item in res.text.split(",") if item.strip()]
                my_fridge.extend(new_items)
                my_fridge = list(set(my_fridge))
                users[st.session_state.username]["fridge"] = my_fridge
                save_db(USER_DB, users)
                st.success(f"🎉 Đã thêm: {', '.join(new_items)}")
                st.rerun()

st.divider()
with st.form("add_item"):
    new_item = st.text_input("Gõ thêm thủ công (VD: Nước mắm, Hành củ...)")
    if st.form_submit_button("➕ Thêm vào tủ"):
        if new_item:
            my_fridge.append(new_item.capitalize())
            users[st.session_state.username]["fridge"] = my_fridge
            save_db(USER_DB, users)
            st.rerun()

st.subheader(f"🧺 Đang có trong tủ ({len(my_fridge)} món):")
for i, item in enumerate(my_fridge):
    col1, col2 = st.columns([4, 1])
    with col1: st.markdown(f"- **{item}**")
    with col2: 
        if st.button("🗑️ Xóa", key=f"del_{i}"):
            my_fridge.pop(i)
            users[st.session_state.username]["fridge"] = my_fridge
            save_db(USER_DB, users)
            st.rerun()
