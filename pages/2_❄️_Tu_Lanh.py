import streamlit as st
import google.generativeai as genai
from PIL import Image
from utils import require_login, load_db, save_db, USER_DB

st.set_page_config(page_title="Tủ Lạnh Thông Minh", page_icon="❄️")
require_login()

st.title(f"❄️ Tủ Lạnh Của {st.session_state.username}")
st.write("Quản lý nguyên liệu thủ công hoặc để AI tự động quét qua hình ảnh chụp tủ lạnh.")

users = load_db(USER_DB)
my_fridge = users[st.session_state.username].get("fridge", [])

# TÍNH NĂNG MỚI: AI QUÉT ẢNH TỦ LẠNH
with st.expander("👁️ QUÉT TỦ LẠNH BẰNG AI (Tự động nhận diện)", expanded=True):
    scan_img = st.file_uploader("Chụp hoặc tải ảnh bên trong tủ lạnh của bạn lên đây", type=["jpg", "jpeg", "png"])
    if scan_img:
        img_fridge = Image.open(scan_img)
        st.image(img_fridge, height=250)
        
        if st.button("✨ Bắt đầu quét tự động", type="primary"):
            with st.spinner("AI đang đếm số củ cà rốt và mớ rau..."):
                model = genai.GenerativeModel('gemini-2.5-flash')
                prompt = "Nhìn vào ảnh này, liệt kê tên các loại thực phẩm, nguyên liệu nấu ăn có trong ảnh. TRẢ LỜI NGẮN GỌN BẰNG TIẾNG VIỆT, CÁCH NHAU BỞI DẤU PHẨY. Ví dụ: Cà chua, trứng gà, thịt heo."
                res = model.generate_content([prompt, img_fridge])
                
                # Tách kết quả thành danh sách và thêm vào tủ lạnh
                new_items = [item.strip().capitalize() for item in res.text.split(",") if item.strip()]
                my_fridge.extend(new_items)
                
                # Loại bỏ trùng lặp và lưu lại
                my_fridge = list(set(my_fridge))
                users[st.session_state.username]["fridge"] = my_fridge
                save_db(USER_DB, users)
                st.success(f"🎉 Đã nhận diện và thêm: {', '.join(new_items)}")
                st.rerun()

st.divider()

# Thêm thủ công
with st.form("add_item"):
    new_item = st.text_input("Hoặc gõ thêm thủ công (VD: Nước mắm, Hành củ...)")
    if st.form_submit_button("➕ Thêm vào tủ"):
        if new_item:
            my_fridge.append(new_item.capitalize())
            users[st.session_state.username]["fridge"] = my_fridge
            save_db(USER_DB, users)
            st.rerun()

# Danh sách đang có
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