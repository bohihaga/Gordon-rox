import streamlit as st
import google.generativeai as genai
from PIL import Image
from ui import apply_theme, render_sidebar
from utils import load_db, save_db, USER_DB

# 1. BẮT BUỘC ĐỂ ĐẦU TIÊN
st.set_page_config(page_title="Gian Bếp Thông Minh", page_icon="🍳", layout="wide")
apply_theme()
render_sidebar()

# 2. KIỂM TRA ĐĂNG NHẬP
if not st.session_state.get("logged_in"):
    st.markdown("<h2 style='text-align:center; color:#f97316; margin-top:15vh;'>🔒 TÍNH NĂNG V.I.P</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#94a3b8;'>Bạn cần Đăng Nhập để vào Gian Bếp.</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        if st.button("🏠 Về Trang Chủ", use_container_width=True, type="primary"):
            st.session_state.auth_view = "login"
            st.switch_page("app.py")
    st.stop()

# Khởi tạo data
user_data = st.session_state.user_data
if "fridge" not in user_data: 
    user_data["fridge"] = []

if "chef_model" not in st.session_state:
    st.session_state.chef_model = genai.GenerativeModel('gemini-2.5-flash')

# ==========================================
# GIAO DIỆN CHÍNH
# ==========================================
st.title("🍳 Gian Bếp Thông Minh")
st.write("---")

# CHIA ĐÔI MÀN HÌNH NHƯ Ý BẠN
col_left, col_right = st.columns([1.2, 1.8], gap="large")

# ==========================================
# 👈 CỘT TRÁI: NHẬP VÀ LƯU TRỮ (KHO / TỦ LẠNH)
# ==========================================
with col_left:
    st.markdown("### 🧺 1. Khu vực Lưu trữ")
    
    # 1.1 Quét ảnh
    st.markdown("<p style='font-size:0.9em; color:#64748b; margin-bottom:5px;'>Tải ảnh nguyên liệu, AI sẽ quét và bỏ vào danh sách.</p>", unsafe_allow_html=True)
    img_file = st.file_uploader("Tải ảnh...", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    
    if img_file:
        img = Image.open(img_file)
        st.image(img, use_column_width=True) 
        if st.button("🔍 Quét ảnh & Thêm vào kho", type="primary", use_container_width=True):
            with st.spinner("Đang nhận diện nguyên liệu..."):
                try:
                    prompt = "Liệt kê các nguyên liệu nấu ăn trong ảnh. Chỉ trả về danh sách, phân tách bằng dấu phẩy (,). Không giải thích thêm. Ví dụ: Cà chua, Trứng, Thịt bò."
                    response = st.session_state.chef_model.generate_content([prompt, img])
                    
                    raw_items = response.text.split(',')
                    new_ingredients = [item.strip().capitalize() for item in raw_items if item.strip()]
                    
                    user_data["fridge"].extend(new_ingredients)
                    user_data["fridge"] = list(set(user_data["fridge"])) # Xóa trùng lặp
                    
                    # Lưu Data
                    users = load_db(USER_DB)
                    users[st.session_state.username] = user_data
                    save_db(USER_DB, users)
                    st.rerun()
                except Exception as e:
                    st.error("Lỗi AI hoặc API Key!")

    # 1.2 Nhập tay
    with st.form("manual_add", clear_on_submit=True):
        st.markdown("<p style='font-size:0.9em; color:#64748b; margin-bottom:0;'>Hoặc nhập tay nếu có sẵn:</p>", unsafe_allow_html=True)
        new_food = st.text_input("Nguyên liệu...", placeholder="VD: Hành lá, mắm muối...", label_visibility="collapsed")
        if st.form_submit_button("➕ Thêm nhanh", use_container_width=True):
            if new_food:
                user_data["fridge"].append(new_food.capitalize())
                user_data["fridge"] = list(set(user_data["fridge"]))
                users = load_db(USER_DB)
                users[st.session_state.username] = user_data
                save_db(USER_DB, users)
                st.rerun()

    # 1.3 Hiển thị Kho
    st.markdown("<br><b>📋 Danh sách nguyên liệu hiện có:</b>", unsafe_allow_html=True)
    with st.container(height=250, border=True):
        if user_data["fridge"]:
            for i, food in enumerate(user_data["fridge"]):
                cf1, cf2 = st.columns([8, 2])
                cf1.write(f"🥦 {food}")
                if cf2.button("❌", key=f"del_{i}"):
                    user_data["fridge"].pop(i)
                    users = load_db(USER_DB)
                    users[st.session_state.username] = user_data
                    save_db(USER_DB, users)
                    st.rerun()
        else:
            st.info("Kho đang trống.")

# ==========================================
# 👉 CỘT PHẢI: AI ĐẦU BẾP NẤU MÓN
# ==========================================
with col_right:
    st.markdown("### 🍲 2. Khu vực Lên món")
    
    if not user_data["fridge"]:
        st.warning("👈 Hãy cung cấp nguyên liệu ở cột bên trái trước, AI sẽ giúp bạn nấu món ngon!")
    else:
        st.success(f"Đã sẵn sàng **{len(user_data['fridge'])}** loại nguyên liệu.")
        
        # Nút Nấu Ăn
        if st.button("✨ GORDON ROX, HÃY LÊN THỰC ĐƠN!", type="primary", use_container_width=True):
            st.session_state.is_cooking = True
            
        st.write("---")
        
        # Xử lý kết quả trả về
        if st.session_state.get("is_cooking"):
            with st.spinner("🔥 Đầu bếp Gordon Rox đang xào nấu dữ liệu..."):
                try:
                    ingredients_str = ", ".join(user_data["fridge"])
                    prompt_recipe = f"Tôi đang có các nguyên liệu: {ingredients_str}. Đóng vai Gordon Ramsay nhưng gọi tên là Gordon Rox. Ngôn từ tự tin, chuyên nghiệp, hơi gắt gỏng nhưng hữu ích. Hãy gợi ý cho tôi 1 món ăn NGON NHẤT có thể làm từ chúng (có thể dùng thêm gia vị cơ bản). Hướng dẫn từng bước cụ thể bằng Markdown."
                    
                    response_recipe = st.session_state.chef_model.generate_content(prompt_recipe)
                    
                    # Hiển thị món ăn
                    with st.container(border=True):
                        st.markdown(response_recipe.text)
                    
                    # Nút dọn dẹp sau khi nấu
                    if st.button("🧹 Đã nấu xong! Làm sạch tủ lạnh", use_container_width=True):
                        user_data["fridge"] = []
                        users = load_db(USER_DB)
                        users[st.session_state.username] = user_data
                        save_db(USER_DB, users)
                        st.session_state.is_cooking = False
                        st.rerun()
                        
                except Exception as e:
                    st.error("AI đang quá tải, thử lại nhé!")
