import streamlit as st

def apply_theme():
    # Cố định mã màu Light Theme siêu sang
    bg_color, text_color, card_bg, sidebar_bg, border_color = "#ffffff", "#1e293b", "#ffffff", "#f8fafc", "#e2e8f0"
    input_bg, input_border = "#f1f5f9", "#cbd5e1"
    btn_bg = "#ffffff"

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Playfair+Display:ital,wght@1,600&display=swap');
        
        body, p, h1, h2, h3, h4, h5, h6, div, input, textarea {{ font-family: 'Inter', sans-serif !important; }}
        .stApp {{ background-color: {bg_color} !important; }}
        div, p, span, a, label, h1, h2, h3, h4, h5, h6, li {{ color: {text_color} !important; }}
        a {{ text-decoration: none !important; }}
        
        /* Cứu hộ nút mở Menu */
        [data-testid="collapsedControl"] {{ display: flex !important; background-color: {sidebar_bg} !important; border-radius: 8px !important; border: 1px solid {border_color} !important; z-index: 999999 !important; }}
        [data-testid="collapsedControl"] svg {{ fill: #f97316 !important; }}

        /* Tối giản ô nhập liệu text */
        [data-baseweb="input"], [data-baseweb="input"] > div {{ background-color: {input_bg} !important; border-color: {input_border} !important; border-radius: 8px !important; }}
        input[type="text"], input[type="password"] {{ color: {text_color} !important; background-color: {input_bg} !important; -webkit-text-fill-color: {text_color} !important; }}

        /* Ô Kéo thả File (File Uploader) - Làm đậm viền nét đứt */
        [data-testid="stFileUploadDropzone"] {{
            background-color: #f8fafc !important;
            border: 2px dashed #94a3b8 !important; /* Nét đứt màu xám đậm, rất dễ nhìn */
            border-radius: 12px !important;
        }}
        [data-testid="stFileUploadDropzone"] div, [data-testid="stFileUploadDropzone"] span, [data-testid="stMarkdownContainer"] p {{ color: #475569 !important; }}

        /* Nút bấm thường & SSO */
        [data-testid="stLinkButton"] a, [data-testid="stLinkButton"] button, [data-testid="stButton"] button {{
            background-color: {btn_bg} !important; color: {text_color} !important; border: 1px solid #cbd5e1 !important;
            border-radius: 10px !important; font-weight: 600 !important; transition: all 0.2s !important; box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important;
        }}
        [data-testid="stLinkButton"] a:hover, [data-testid="stLinkButton"] button:hover, [data-testid="stButton"] button:hover {{ border-color: #f97316 !important; color: #f97316 !important; transform: translateY(-1px); }}

        /* Nút Submit màu Cam nổi bật */
        [data-testid="stFormSubmitButton"] button {{ background-color: #f97316 !important; color: white !important; border: none !important; border-radius: 10px !important; }}
        [data-testid="stFormSubmitButton"] button:hover {{ background-color: #ea580c !important; color: white !important; transform: translateY(-1px); }}

        /* ==========================================
           🔥 NÂNG CẤP KHU VỰC CHAT CHUYÊN NGHIỆP 🔥
           ========================================== */
           
        /* 1. Mảng trắng ở đáy - Xóa sổ hoàn toàn */
        [data-testid="stBottom"], [data-testid="stBottom"] > div, .stBottomBlock {{ background-color: transparent !important; }}
        
        /* 2. Thanh nhập lệnh (Chat Input) - Nổi bật, sang trọng */
        .stChatInputContainer, [data-testid="stChatInput"] {{ 
            background-color: #ffffff !important; 
            border: 1px solid #94a3b8 !important; /* Viền xám đậm thanh lịch */
            border-radius: 16px !important; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.06) !important; /* Bóng đổ 3D nhẹ */
        }}
        .stChatInputContainer:focus-within {{ 
            border-color: #f97316 !important; 
            box-shadow: 0 4px 15px rgba(249,115,22,0.1) !important; 
        }}
        .stChatInputContainer textarea, [data-testid="stChatInputTextArea"] {{ color: #1e293b !important; -webkit-text-fill-color: #1e293b !important; }}
        
        /* 3. Khung bọc to bên ngoài (Container Tủ lạnh, Chat) - Sắc nét hơn */
        [data-testid="stVerticalBlockBorderWrapper"] {{ 
            background-color: {card_bg} !important; 
            border-radius: 16px !important; 
            border: 1px solid #cbd5e1 !important; /* Thay màu siêu nhạt thành Xám khói để tạo giới hạn rõ ràng */
            padding: 15px !important; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.03) !important; 
        }}

        /* 4. Bong bóng tin nhắn (Chat Message) - Style giống ChatGPT */
        [data-testid="stChatMessage"] {{
            background-color: #f8fafc !important; /* Nền xám xanh cực nhạt */
            border: 1px solid #e2e8f0 !important;
            border-radius: 12px !important;
            padding: 12px 18px !important;
            margin-bottom: 12px !important;
        }}

        /* Xóa sạch Manage App và Header rác */
        footer, [data-testid="stFooter"], .viewerBadge_container, .viewerBadge_link, [class^="viewerBadge"], [data-testid="stAppDeployButton"] {{ display: none !important; visibility: hidden !important; opacity: 0 !important; }}
        #MainMenu, [data-testid="stToolbar"], [data-testid="stHeader"] {{ display: none !important; }}
        [data-testid="stSidebarNav"] {{ display: none !important; }}
        
        /* Sidebar thiết kế Sáng */
        [data-testid="stSidebar"] {{ background-color: {sidebar_bg} !important; border-right: 1px solid {border_color} !important; }}
        .sidebar-logo {{ font-family: 'Playfair Display', serif !important; font-size: 2.2rem; color: #f97316 !important; margin-bottom: 25px; padding-left: 10px; font-style: italic; font-weight: 800; }}
        
        /* Auth Card - Bo góc, bóng đổ xịn xò */
        .unified-auth-card {{ background: {card_bg}; border: 1px solid {border_color}; border-radius: 24px; padding: 40px 30px; box-shadow: 0 10px 40px rgba(0,0,0,0.05); }}
        [data-testid="stForm"] {{ border: none !important; padding: 0 !important; background: transparent !important; }}
        </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.markdown("<div class='sidebar-logo'>Gordon Rox</div>", unsafe_allow_html=True)
        
        st.page_link("app.py", label="Trang chủ", icon="🏠")
        st.page_link("pages/1_🍳_Dau_Bep_AI.py", label="Gian Bếp AI", icon="🍳")
        st.page_link("pages/3_🌍_Dien_Dan.py", label="Mạng xã hội", icon="🌍")
        
        st.markdown("<div style='flex-grow: 1; min-height: 40vh;'></div>", unsafe_allow_html=True)
        
        with st.container(border=True):
            if st.session_state.get("logged_in"):
                st.markdown(f"<div style='font-weight: 600; font-size:1.1em; margin-bottom:10px;'>👤 {st.session_state.username}</div>", unsafe_allow_html=True)
                if st.button("🔴 Đăng Xuất", use_container_width=True):
                    st.session_state.logged_in = False
                    st.session_state.auth_view = "home"
                    st.switch_page("app.py")
            else:
                st.markdown("<div style='font-size: 0.9em; text-align: center; margin-bottom:10px; color: #64748b;'>Bạn chưa đăng nhập</div>", unsafe_allow_html=True)
                if st.button("🔑 Sign In / Up", type="primary", use_container_width=True):
                    st.session_state.auth_view = "login"
                    st.switch_page("app.py")
