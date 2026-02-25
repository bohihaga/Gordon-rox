import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import os
import hashlib
from datetime import datetime

# ==========================================
# 1. CẤU HÌNH & CSS NÂNG CAO
# ==========================================
st.set_page_config(page_title="Gordon Rox - Ultimate AI", page_icon="👑", layout="wide")

def load_css():
    st.markdown("""
        <style>
        .main { background-color: #f4f6f9; }
        .stButton>button { border-radius: 8px; font-weight: bold; border: none; transition: 0.3s; }
        .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0,0,0,0.15); }
        .welcome-box { background: linear-gradient(135deg, #ff7e5f, #feb47b); padding: 20px; border-radius: 15px; color: white; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .recipe-card { background: white; padding: 15px; border-radius: 10px; border-left: 5px solid #ff7e5f; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 10px; }
        .forum-msg { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 15px; }
        .forum-author { color: #ff7e5f; font-weight: bold; font-size: 1.1em; }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. CƠ SỞ DỮ LIỆU (DATABASE GIẢ LẬP)
# ==========================================
USER_DB_FILE = "users_db.json"
FORUM_DB_FILE = "forum_messages.json"

def init_db():
    if not os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f) # Dictionary lưu user
    if not os.path.exists(FORUM_DB_FILE):
        with open(FORUM_DB_FILE, "w", encoding="utf-8") as f:
            json.dump([], f) # List lưu bài viết

def load_users():
    with open(USER_DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(data):
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def hash_password(password):
    # Mã hóa mật khẩu để bảo mật (Không lưu pass thô)
    return hashlib.sha256(password.encode()).hexdigest()

# ==========================================
# 3. HỆ THỐNG XÁC THỰC (AUTHENTICATION)
# ==========================================
def auth_system():
    st.markdown("<h1 style='text-align: center; color: #ff7e5f;'>👨‍🍳 GORDON ROX MASTERCHEF</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: gray;'>Vui lòng đăng nhập để vào bếp</h4>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_register = st.tabs(["🔐 Đăng Nhập", "📝 Đăng Ký Tài Khoản Mới"])
        
        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Tên đăng nhập")
                password = st.text_input("Mật khẩu", type="password")
                submit_login = st.form_submit_button("Đăng Nhập", use_container_width=True)
                
                if submit_login:
                    users = load_users()
                    if username in users and users[username]["password"] == hash_password(password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_data = users[username]
                        st.success("Đăng nhập thành công! Đang vào bếp...")
                        st.rerun()
                    else:
                        st.error("Sai tên đăng nhập hoặc mật khẩu!")

        with tab_register:
            with st.form("register_form"):
                new_user = st.text_input("Chọn Tên đăng nhập")
                new_pass = st.text_input("Nhập Mật khẩu", type="password")
                confirm_pass = st.text_input("Xác nhận Mật khẩu", type="password")
                submit_register = st.form_submit_button("Đăng Ký", use_container_width=True)
                
                if submit_register:
                    users = load_users()
                    if new_user in users:
                        st.error("Tên đăng nhập này đã có người sử dụng!")
                    elif new_pass != confirm_pass:
                        st.error("Mật khẩu xác nhận không khớp!")
                    elif len(new_pass) < 4:
                        st.error("Mật khẩu phải dài ít nhất 4 ký tự!")
                    else:
                        # Tạo profile mới cho user
                        users[new_user] = {
                            "password": hash_password(new_pass),
                            "created_at": datetime.now().strftime("%d/%m/%Y"),
                            "fridge": [], # Tủ lạnh ảo
                            "diet": "Bình thường"
                        }
                        save_users(users)
                        st.success("Đăng ký thành công! Bạn có thể đăng nhập ngay.")

# ==========================================
# 4. KHỞI TẠO AI GORDON ROX
# ==========================================
def init_ai():
    try:
        API_KEY = st.secrets["GEMINI_API_KEY"] 
        genai.configure(api_key=API_KEY)
    except KeyError:
        st.error("⚠️ Lỗi Hệ Thống: Chưa có API Key.")
        st.stop()
        
    user_diet = st.session_state.user_data.get("diet", "Bình thường")
    system_prompt = f"""
    Bạn là Gordon Rox. 
    1. Chủ đề: CHỈ nói về ẩm thực, nấu ăn. TỪ CHỐI mọi chủ đề khác.
    2. Người dùng đang trò chuyện tên là: {st.session_state.username}. Hãy thỉnh thoảng gọi tên họ.
    3. Chế độ ăn của họ: {user_diet}.
    4. Cư xử chuyên nghiệp, có chút hài hước và am hiểu sâu sắc về dinh dưỡng.
    """
    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt)
    if "ai_session" not in st.session_state:
        st.session_state.ai_session = model.start_chat(history=[])
    return model

# ==========================================
# 5. CÁC TRANG CHỨC NĂNG (PAGES)
# ==========================================

def page_dashboard():
    # Khung Welcome
    st.markdown(f"""
    <div class="welcome-box">
        <h2 style='margin-bottom:0;'>Xin chào, {st.session_state.username}! 👋</h2>
        <p style='font-size: 1.1em; opacity: 0.9;'>Hôm nay là {datetime.now().strftime('%d/%m/%Y')}. Bếp đã nóng, chúng ta nấu gì đây?</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tính năng đề xuất theo thứ trong tuần
    st.subheader("💡 Gợi Ý Món Ngon Hôm Nay")
    thu = datetime.now().weekday() # 0 là Thứ 2, 6 là Chủ nhật
    
    thuc_don_tuan = [
        {"thu": "Thứ 2", "sang": "Phở Bò tái lăn (Nhiều năng lượng đầu tuần)", "trua": "Cơm Tấm sườn bì", "toi": "Cá kho tộ & Canh chua"},
        {"thu": "Thứ 3", "sang": "Bánh Mì ốp la", "trua": "Bún Chả Hà Nội", "toi": "Thịt luộc cà pháo"},
        {"thu": "Thứ 4", "sang": "Xôi xéo", "trua": "Cơm chiên hải sản", "toi": "Gà xào sả ớt"},
        {"thu": "Thứ 5", "sang": "Bún Bò Huế", "trua": "Mì Ý sốt bò băm", "toi": "Sườn xào chua ngọt"},
        {"thu": "Thứ 6", "sang": "Bánh cuốn", "trua": "Phở cuốn", "toi": "Thịt kho tàu & Dưa giá"},
        {"thu": "Thứ 7", "sang": "Bánh Canh cua", "trua": "Pizza tự làm", "toi": "Lẩu Thái hải sản (Họp mặt)"},
        {"thu": "Chủ Nhật", "sang": "Pancake xốt mật ong", "trua": "Gà nướng tiêu xanh", "toi": "Salad ức gà (Thanh lọc cơ thể)"},
    ]
    hom_nay = thuc_don_tuan[thu]
    
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f"<div class='recipe-card'><b>🌅 Bữa Sáng:</b><br>{hom_nay['sang']}</div>", unsafe_allow_html=True)
    with col2: st.markdown(f"<div class='recipe-card'><b>☀️ Bữa Trưa:</b><br>{hom_nay['trua']}</div>", unsafe_allow_html=True)
    with col3: st.markdown(f"<div class='recipe-card'><b>🌙 Bữa Tối:</b><br>{hom_nay['toi']}</div>", unsafe_allow_html=True)
    
    st.info("👆 Nếu không thích thực đơn này, hãy qua tab 'Đầu Bếp AI' để Gordon Rox thiết kế riêng cho bạn nhé!")

def page_ai_chef():
    st.title("🍳 Đầu Bếp AI Độc Quyền")
    st.markdown("---")
    
    col_img, col_action = st.columns([1, 1])
    with col_img:
        st.write("##### 1. Tải ảnh nguyên liệu")
        uploaded_file = st.file_uploader("Upload ảnh thực phẩm", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        anh_gui_di = Image.open(uploaded_file) if uploaded_file else None
        if anh_gui_di: st.image(anh_gui_di, use_column_width=True)

    with col_action:
        st.write("##### 2. Yêu cầu AI")
        if st.button("🚀 Viết Công Thức Từ Ảnh Này", type="primary", use_container_width=True):
            if not anh_gui_di:
                st.error("Bạn chưa tải ảnh lên kìa!")
            else:
                with st.spinner("Gordon Rox đang nghiên cứu ảnh..."):
                    prompt = "Phân tích ảnh, liệt kê nguyên liệu và chỉ tôi 2 cách nấu ngon nhất."
                    st.session_state.chat_history.append({"role": "user", "content": f"*{prompt}* [Ảnh đính kèm]"})
                    res = st.session_state.ai_session.send_message([prompt, anh_gui_di])
                    st.session_state.chat_history.append({"role": "ai", "content": res.text})
                    st.rerun()

    st.divider()
    st.subheader("💬 Khung Trò Chuyện Bếp Trưởng")
    for msg in st.session_state.chat_history:
        icon = "🧑‍💻" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=icon):
            st.markdown(msg["content"])
            
    user_input = st.chat_input(f"Gordon Rox đang nghe đây, {st.session_state.username} muốn hỏi gì?")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="🧑‍💻"): st.markdown(user_input)
        
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Đang nấu chữ..."):
                res = st.session_state.ai_session.send_message(user_input)
                st.markdown(res.text)
                st.session_state.chat_history.append({"role": "ai", "content": res.text})

def page_pantry():
    st.title("❄️ Tủ Lạnh Của Tôi")
    st.markdown("Quản lý những gì bạn đang có ở nhà để AI gợi ý tốt hơn.")
    
    users = load_users()
    my_fridge = users[st.session_state.username].get("fridge", [])
    
    # Khu vực thêm nguyên liệu
    with st.form("add_ingredient"):
        new_item = st.text_input("Nhập nguyên liệu mới (VD: 2 quả trứng, 1 mớ rau muống)")
        col_btn, _ = st.columns([1, 4])
        if col_btn.form_submit_button("➕ Thêm vào tủ"):
            if new_item:
                my_fridge.append(new_item)
                users[st.session_state.username]["fridge"] = my_fridge
                save_users(users)
                st.success(f"Đã thêm '{new_item}' vào tủ lạnh!")
                st.rerun()

    st.write("### 🧺 Đang có trong tủ:")
    if not my_fridge:
        st.info("Tủ lạnh của bạn đang trống rỗng. Hãy đi siêu thị nhé!")
    else:
        for idx, item in enumerate(my_fridge):
            col_text, col_del = st.columns([4, 1])
            with col_text: st.markdown(f"**{idx+1}.** {item}")
            with col_del:
                if st.button("🗑️ Xóa", key=f"del_{idx}"):
                    my_fridge.pop(idx)
                    users[st.session_state.username]["fridge"] = my_fridge
                    save_users(users)
                    st.rerun()
                    
        if st.button("🤖 Gordon Rox ơi, tủ lạnh vầy nấu gì được?", type="primary"):
            ingredients_list = ", ".join(my_fridge)
            prompt = f"Tủ lạnh của tôi đang có: {ingredients_list}. Tôi không có ảnh. Dựa vào danh sách này, gợi ý cho tôi 1 món ăn kết hợp chúng lại nhé."
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.spinner("Đang lục tủ lạnh..."):
                res = st.session_state.ai_session.send_message(prompt)
                st.session_state.chat_history.append({"role": "ai", "content": res.text})
                st.session_state.current_page = "🍳 Đầu Bếp AI" # Chuyển trang
                st.rerun()

def page_forum():
    st.title("🌍 Cộng Đồng Gordon Rox")
    st.caption("Khám phá công thức từ những đầu bếp khác!")
    st.write("---")
    
    # Không cần nhập tên nữa, hệ thống tự lấy tên đăng nhập
    with st.form("forum_post"):
        st.write(f"Đăng bài dưới tên: **{st.session_state.username}**")
        user_msg = st.text_area("Bạn muốn chia sẻ điều gì?")
        if st.form_submit_button("🚀 Đăng Bài"):
            if user_msg:
                with open(FORUM_DB_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data.append({
                    "name": st.session_state.username, 
                    "time": datetime.now().strftime("%d/%m/%Y - %H:%M"), 
                    "message": user_msg
                })
                with open(FORUM_DB_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)
                st.success("Đã đăng!")
                st.rerun()
    
    st.subheader("📰 Bảng Tin")
    with open(FORUM_DB_FILE, "r", encoding="utf-8") as f:
        posts = json.load(f)
    for post in reversed(posts):
        st.markdown(f"""
        <div class="forum-msg">
            <span class="forum-author">🧑‍🍳 @{post['name']}</span> <span style="color:gray;font-size:0.8em;">({post['time']})</span><br>
            <div style="margin-top:10px;">{post['message']}</div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 6. ROUTER CHÍNH (MAIN APP)
# ==========================================
def main():
    load_css()
    init_db()
    
    # Kiểm tra trạng thái đăng nhập
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        auth_system()
    else:
        # Nếu đã đăng nhập, khởi động AI và Giao diện chính
        init_ai()
        
        with st.sidebar:
            st.image("https://cdn-icons-png.flaticon.com/512/1830/1830839.png", width=100)
            st.markdown(f"### 👤 @{st.session_state.username}")
            st.divider()
            
            menu = ["📊 Dashboard", "🍳 Đầu Bếp AI", "❄️ Tủ Lạnh Của Tôi", "🌍 Diễn Đàn"]
            choice = st.radio("Menu Tùy Chọn:", menu)
            st.session_state.current_page = choice
            
            st.divider()
            if st.button("🔴 Đăng Xuất", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.pop("ai_session", None)
                st.rerun()
                
        # Điều hướng trang
        if st.session_state.current_page == "📊 Dashboard": page_dashboard()
        elif st.session_state.current_page == "🍳 Đầu Bếp AI": page_ai_chef()
        elif st.session_state.current_page == "❄️ Tủ Lạnh Của Tôi": page_pantry()
        elif st.session_state.current_page == "🌍 Diễn Đàn": page_forum()

if __name__ == "__main__":
    main()