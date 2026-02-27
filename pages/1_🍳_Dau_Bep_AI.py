import streamlit as st
import google.generativeai as genai
from PIL import Image
from ui import apply_theme, render_sidebar
from utils import load_db, save_db, USER_DB

# 1. BẮT BUỘC ĐỂ ĐẦU TIÊN
st.set_page_config(page_title="Gian Bếp Thông Minh", page_icon="🍳", layout="wide")

# 2. GỌI GIAO DIỆN CHUẨN (MÀU SÁNG & MENU TỪ ui.py)
apply_theme()
render_sidebar()

# 3. KIỂM TRA ĐĂNG NHẬP
if not st.session_state.get("logged_in"):
    st.markdown("<h2 style='text-align:center; color:#f97316; margin-top:15vh;'>🔒 TÍNH NĂNG V.I.P</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#94a3b8;'>Bạn cần Đăng Nhập để vào Gian Bếp.</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        if st.button("🏠 Về Trang Chủ", use_container_width=True, type="primary"):
            st.session_state.auth_view = "login"
            st.switch_page("app.py")
    st.stop()

# Khởi tạo trạng thái và AI
user_data = st.session_state.user_data
if "fridge" not in user_data: 
    user_data["fridge"] = []

if "chef_model" not in st.session_state:
    st.session_state.chef_model = genai.GenerativeModel('gemini-2.5-flash')

# ==========================================
# GIAO DIỆN CHÍNH: QUY TRÌNH 3 BƯỚC
# ==========================================
st.title("🍳 Gian Bếp Thông Minh")
st.caption("Quy trình khép kín: Quét ảnh nhập kho ➡️ Quản lý tủ lạnh ➡️ Gordon Rox lên thực đơn.")
st.write("<br>", unsafe_allow_html=True)

col_nhapkho, col_tulanh = st.columns(2, gap="large")

# ------------------------------------------
# CỘT 1: NHẬP KHO BẰNG AI
# ------------------------------------------
with col_nhapkho:
    st.markdown("### 📸 Bước 1: Quét ảnh nhập kho")
    st.markdown("<p style='font-size:0.9em; color:#64748b;'>Tải ảnh nguyên liệu bạn vừa mua về, AI sẽ tự nhận diện và cất vào tủ.</p>", unsafe_allow_html=True)
    
    img_file = st.file_uploader("Tải ảnh lên (JPG, PNG)...", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    
    if img_file:
        img = Image.open(img_file)
        st.image(img, width=350) 
        
        if st.button("🔍 AI Quét & Cất Vào Tủ", type="primary", use_container_width=True):
            with st.spinner("Gordon Rox đang phân tích ảnh..."):
                try:
                    # Yêu cầu AI chỉ trả về danh sách nguyên liệu
                    prompt = "Hãy nhìn vào ảnh này và liệt kê các nguyên liệu nấu ăn chính xác mà bạn thấy. Chỉ trả về một danh sách các nguyên liệu, phân tách nhau bằng dấu phẩy (,). Không giải thích, không viết thêm bất cứ câu chữ nào khác. Ví dụ: Thịt bò, Hành tây, Cà rốt, Cà chua."
                    response = st.session_state.chef_model.generate_content([prompt, img])
                    
                    # Xử lý kết quả trả về thành list (cắt khoảng trắng)
                    raw_items = response.text.split(',')
                    new_ingredients = [item.strip().capitalize() for item in raw_items if item.strip()]
                    
                    # Thêm vào tủ lạnh và loại bỏ trùng lặp
                    user_data["fridge"].extend(new_ingredients)
                    user_data["fridge"] = list(set(user_data["fridge"]))
                    
                    # Lưu vào Database
                    users = load_db(USER_DB)
                    users[st.session_state.username] = user_data
                    save_db(USER_DB, users)
                    
                    st.success(f"Đã cất vào tủ: {', '.join(new_ingredients)}")
                    st.rerun() # Tải lại trang để cập nhật cột Tủ Lạnh
                except Exception as e:
                    st.error("Lỗi phân tích hình ảnh hoặc chưa cấu hình API Key.")

# ------------------------------------------
# CỘT 2: QUẢN LÝ TỦ LẠNH & GỌI ĐẦU BẾP
# ------------------------------------------
with col_tulanh:
    st.markdown("### ❄️ Bước 2: Tủ lạnh của bạn")
    
    # Form nhập tay dự phòng
    with st.form("add_food_manual", clear_on_submit=True):
        new_food = st.text_input("Hoặc nhập tay nguyên liệu...", placeholder="VD: 2 quả trứng, nửa cái bắp cải...", label_visibility="collapsed")
        if st.form_submit_button("➕ Thêm tay", use_container_width=True):
            if new_food:
                user_data["fridge"].append(new_food.capitalize())
                user_data["fridge"] = list(set(user_data["fridge"]))
                users = load_db(USER_DB)
                users[st.session_state.username] = user_data
                save_db(USER_DB, users)
                st.rerun()
    
    # Hiển thị đồ trong tủ
    if user_data["fridge"]:
        st.markdown("**Đang có sẵn:**")
        for i, food in enumerate(user_data["fridge"]):
            cf1, cf2 = st.columns([8, 2])
            cf1.write(f"🥩 {food}")
            if cf2.button("❌", key=f"del_{i}"):
                user_data["fridge"].pop(i)
                users = load_db(USER_DB)
                users[st.session_state.username] = user_data
                save_db(USER_DB, users)
                st.rerun()
                
        st.write("<br>", unsafe_allow_html=True)
        st.markdown("### 🍲 Bước 3: Đứng bếp")
        # Nút thần thánh: Nấu từ tất cả đồ trong tủ
        if st.button("✨ Gordon Rox, Lên Thực Đơn!", type="primary", use_container_width=True):
            st.session_state.generate_recipe = True
    else:
        st.info("Tủ lạnh đang trống. Hãy tải ảnh lên hoặc nhập tay nhé!")

st.divider()

# ------------------------------------------
# KHU VỰC TRẢ KẾT QUẢ CỦA AI (BƯỚC 3)
# ------------------------------------------
if st.session_state.get("generate_recipe"):
    st.markdown("## 🧑‍🍳 Gordon Rox Đề Xuất")
    with st.spinner("Đang xào nấu dữ liệu từ tủ lạnh của bạn..."):
        try:
            # Gộp tất cả đồ trong tủ thành 1 chuỗi
            ingredients_str = ", ".join(user_data["fridge"])
            
            # Đặt lệnh cho AI
            prompt_recipe = f"Tủ lạnh của tôi đang có chính xác những nguyên liệu này: {ingredients_str}. Đóng vai siêu đầu bếp Gordon Rox (ngôn từ chuyên nghiệp, tự tin, thỉnh thoảng khen ngợi nguyên liệu), hãy gợi ý cho tôi 1 hoặc 2 món ăn tuyệt vời nhất có thể làm ra từ chúng (tôi có sẵn các gia vị cơ bản như mắm, muối, tiêu, dầu ăn). Trình bày công thức chi tiết, từng bước rõ ràng bằng Markdown."
            
            response_recipe = st.session_state.chef_model.generate_content(prompt_recipe)
            st.markdown(response_recipe.text)
            
            if st.button("Làm sạch tủ lạnh (Đã nấu xong)"):
                user_data["fridge"] = []
                users = load_db(USER_DB)
                users[st.session_state.username] = user_data
                save_db(USER_DB, users)
                st.session_state.generate_recipe = False
                st.rerun()
                
        except Exception as e:
            st.error("Hệ thống AI đang quá tải, vui lòng thử lại sau.")
