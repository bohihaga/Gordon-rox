import streamlit as st
import datetime
from ui import apply_theme, render_sidebar

# 1. CẤU HÌNH TRANG
st.set_page_config(page_title="Cộng Đồng Ẩm Thực", page_icon="🌍", layout="wide")

# 2. BẬT GIAO DIỆN & MENU CHUẨN
apply_theme()
render_sidebar()

# 3. KIỂM TRA ĐĂNG NHẬP
if not st.session_state.get("logged_in"):
    st.markdown("<h2 style='text-align:center; color:#f97316; margin-top:15vh;'>🔒 CỘNG ĐỒNG V.I.P</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#94a3b8;'>Bạn cần Đăng Nhập để tham gia mạng xã hội ẩm thực.</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    with col2:
        if st.button("🏠 Về Trang Chủ", use_container_width=True, type="primary"):
            st.session_state.auth_view = "login"
            st.switch_page("app.py")
    st.stop()

# ==========================================
# KHỞI TẠO DATA MẠNG XÃ HỘI (Demo)
# ==========================================
if "community_posts" not in st.session_state:
    st.session_state.community_posts = [
        {
            "id": 1,
            "author": "Gordon Rox (Bot)", 
            "time": "2 giờ trước", 
            "title": "🔥 Thử thách dọn sạch tủ lạnh cuối tuần!", 
            "content": "Chào các bếp trưởng! Cuối tuần rồi, hãy mở tủ lạnh ra, ném tất cả nguyên liệu thừa vào phần Gian Bếp AI để tôi thiết kế cho bạn một món ăn đẳng cấp Michelin nhé. Ai làm được món ngon nhất nhớ khoe lên đây!", 
            "likes": 156
        },
        {
            "id": 2,
            "author": "Chef_Linh99", 
            "time": "5 giờ trước", 
            "title": "Giải cứu cà chua và trứng", 
            "content": "Nhờ Gordon Rox gợi ý mà mình mới biết món Trứng chưng cà chua kiểu Ý (Shakshuka) ngon đến thế. Công thức siêu đơn giản mà ăn hao cơm cực kỳ. Cảm ơn app!", 
            "likes": 42
        }
    ]

# Lấy dữ liệu Tủ Lạnh hiện tại của user để Tích Hợp
user_data = st.session_state.get("user_data", {})
user_fridge = user_data.get("fridge", [])

# ==========================================
# GIAO DIỆN CHÍNH
# ==========================================
st.title("🌍 Mạng Xã Hội Ẩm Thực")
st.caption("Nơi chia sẻ thành quả nấu nướng và giao lưu cùng các đầu bếp V.I.P")
st.write("---")

# Chia 2 Tab: Bảng tin và Đăng bài
tab_feed, tab_post = st.tabs(["📰 Bảng tin Cộng đồng", "✍️ Đăng bài chia sẻ"])

# ------------------------------------------
# TAB 2: ĐĂNG BÀI (CÓ TÍCH HỢP GIAN BẾP)
# ------------------------------------------
with tab_post:
    st.markdown("### 📝 Chia sẻ món ngon của bạn")
    
    # Khu vực Tích hợp
    st.markdown("💡 **Tích hợp thông minh:**")
    if user_fridge:
        st.success(f"Tủ lạnh của bạn đang có **{len(user_fridge)}** nguyên liệu: {', '.join(user_fridge)}")
        use_fridge = st.checkbox("📥 Tự động đính kèm danh sách nguyên liệu này vào bài viết")
    else:
        st.info("Tủ lạnh của bạn đang trống. Hãy qua trang 'Gian Bếp AI' để thêm nguyên liệu nhé!")
        use_fridge = False

    # Form nhập liệu bài viết
    with st.form("new_post_form", clear_on_submit=True):
        post_title = st.text_input("Tiêu đề món ăn / Chủ đề:", placeholder="VD: Siêu phẩm Bò bít tết tối nay...")
        
        # Tạo nội dung mặc định nếu user tick chọn dùng tủ lạnh
        default_content = ""
        
        post_content = st.text_area("Câu chuyện / Công thức của bạn:", height=150, placeholder="Chia sẻ cảm nghĩ, công thức hoặc hình ảnh bạn vừa nấu...")
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            submitted = st.form_submit_button("🚀 Đăng bài lên Cộng đồng", use_container_width=True)
            
            if submitted and post_title and post_content:
                # Trộn nội dung nếu có tích hợp tủ lạnh
                final_content = post_content
                if use_fridge:
                    final_content += f"\n\n👉 *Nguyên liệu mình dùng từ tủ lạnh: {', '.join(user_fridge)}*"
                
                # Tạo bài viết mới
                new_post = {
                    "id": len(st.session_state.community_posts) + 1,
                    "author": st.session_state.username,
                    "time": "Vừa xong",
                    "title": post_title,
                    "content": final_content,
                    "likes": 0
                }
                # Đẩy lên đầu danh sách
                st.session_state.community_posts.insert(0, new_post)
                st.success("🎉 Đăng bài thành công! Qua Bảng tin để xem nhé.")
                st.rerun()
            elif submitted:
                st.error("⚠️ Vui lòng nhập đủ Tiêu đề và Nội dung!")

# ------------------------------------------
# TAB 1: BẢNG TIN (FEED)
# ------------------------------------------
with tab_feed:
    # Nút làm mới bảng tin
    col_re, _ = st.columns([2, 8])
    with col_re:
        if st.button("🔄 Làm mới Feed"):
            st.rerun()
            
    st.write("<br>", unsafe_allow_html=True)
    
    # Hiển thị danh sách bài viết
    for post in st.session_state.community_posts:
        with st.container(border=True):
            # Header bài viết (Avatar + Tên + Thời gian)
            c1, c2 = st.columns([1, 15])
            with c1:
                st.markdown(f"<div style='background-color:#e2e8f0; border-radius:50%; width:40px; height:40px; display:flex; align-items:center; justify-content:center; font-size:1.2em;'>🧑‍🍳</div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div style='line-height:1.2;'><b>{post['author']}</b><br><span style='color:#64748b; font-size:0.8em;'>{post['time']}</span></div>", unsafe_allow_html=True)
            
            st.write("")
            # Nội dung bài viết
            st.markdown(f"#### {post['title']}")
            st.markdown(post['content'])
            
            st.divider()
            
            # Tương tác (Like)
            c_like, c_cmt, c_space = st.columns([2, 2, 8])
            with c_like:
                # Tạo key duy nhất cho mỗi nút Like để không bị lỗi
                if st.button(f"❤️ Thích ({post['likes']})", key=f"like_{post['id']}"):
                    post['likes'] += 1
                    st.rerun()
            with c_cmt:
                st.button(f"💬 Bình luận", key=f"cmt_{post['id']}")
        
        st.write("<br>", unsafe_allow_html=True)
