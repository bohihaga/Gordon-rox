import streamlit as st

def apply_theme():
    if "theme_mode" not in st.session_state: 
        st.session_state.theme_mode = "Dark"
        
    if st.session_state.theme_mode == "Dark":
        bg_color, text_color, card_bg, sidebar_bg, border_color = "#0f1115", "#f8fafc", "#1e2026", "#16181d", "#272a30"
        input_bg, input_border = "#16181d", "#333842"
        btn_bg = "#1e2026"
    else:
        bg_color, text_color, card_bg, sidebar_bg, border_color = "#ffffff", "#1e293b", "#f8fafc", "#f1f5f9", "#e2e8f0"
        input_bg, input_border = "#ffffff", "#cbd5e1"
        btn_bg = "#f1f5f9"

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Playfair+Display:ital,wght@1,600&display=swap');
        
        body, p, h1, h2, h3, h4, h5, h6, div, input, textarea {{ font-family: 'Inter', sans-serif !important; }}
        .stApp {{ background-color: {bg_color} !important; }}
        div, p, span, a, label, h1, h2, h3, h4, h5, h6, li {{ color: {text_color} !important; }}
        a {{ text-decoration: none !important; }}
        
        [data-testid="collapsedControl"] {{ display: flex !important; background-color: {sidebar_bg} !important; border-radius: 8px !important; border: 1px solid {border_color} !important; z-index: 999999 !important; }}
        [data-testid="collapsedControl"] svg {{ fill: #f97316 !important; }}

        [data-baseweb="input"], [data-baseweb="input"] > div {{ background-color: {input_bg} !important; border-color: {input_border} !important; }}
        input[type="text"], input[type="password"] {{ color: {text_color} !important; background-color: {input_bg} !important; -webkit-text-fill-color: {text_color} !important; }}

        [data-testid="stLinkButton"] a, [data-testid="stLinkButton"] button, [data-testid="stButton"] button {{
            background-color: {btn_bg} !important; color: {text_color} !important; border: 1px solid {border_color} !important;
            border-radius: 12px !important; font-weight: 600 !important; transition: all 0.2s !important; box-shadow: none !important;
        }}
        [data-testid="stLinkButton"] a:hover, [data-testid="stLinkButton"] button:hover, [data-testid="stButton"] button:hover {{ border-color: #f97316 !important; color: #f97316 !important; }}

        [data-testid="stFormSubmitButton"] button {{ background-color: #f97316 !important; color: white !important; border: none !important; border-radius: 10px !important; }}
        [data-testid="stFormSubmitButton"] button:hover {{ background-color: #ea580c !important; color: white !important; }}

        /* 🔥 TRIỆT TIÊU TOÀN BỘ MẢNG TRẮNG Ở ĐÁY VÀ KHUNG CHAT 🔥 */
        [data-testid="stBottom"], [data-testid="stBottom"] > div, .stBottomBlock, div[class*="stBottom"] {{ 
            background-color: transparent !important; 
            background: transparent !important;
        }}
        .stChatInputContainer {{ 
            background-color: {input_bg} !important; 
            border: 1px solid {input_border} !important; 
            border-radius: 16px !important; 
        }}
        [data-testid="stVerticalBlockBorderWrapper"] {{ background-color: {card_bg} !important; border-radius: 16px !important; border: 1px solid {border_color} !important; padding: 10px; }}

        /* 🔥 HỦY DIỆT MANAGE APP VÀ RÁC STREAMLIT 🔥 */
        footer, [data-testid="stFooter"], .viewerBadge_container, .viewerBadge_link, [class^="viewerBadge"], [data-testid="stAppDeployButton"] {{ display: none !important; visibility: hidden !important; opacity: 0 !important; }}
        #MainMenu, [data-testid="stToolbar"] {{ display: none !important; }}
        [data-testid="stHeader"] {{ background-color: transparent !important; }}
        [data-testid="stSidebarNav"] {{ display: none !important; }}
        [data-testid="stSidebar"] {{ background-color: {sidebar_bg} !important; border-right: 1px solid {border_color} !important; }}
        .sidebar-logo {{ font-family: 'Playfair Display', serif !important; font-size: 2.2rem; color: #f97316 !important; margin-bottom: 25px; padding-left: 10px; font-style: italic; font-weight: 800; }}
        .unified-auth-card {{ background: {card_bg}; border: 1px solid {border_color}; border-radius: 24px; padding: 40px 30px; box-shadow: 0 20px 50px rgba(0,0,0,0.2); }}
        [data-testid="stForm"] {{ border: none !important; padding: 0 !important; background: transparent !important; }}
        </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.markdown("<div class='sidebar-logo'>Gordon Rox</div>", unsafe_allow_html=True)
        
        st.markdown("🌓 **Chế độ hiển thị**")
        current_theme = st.session_state.get("theme_mode", "Dark")
        new_theme = st.radio("Chọn màu:", ["Dark", "Light"], index=0 if current_theme=="Dark" else 1, label_visibility="collapsed", horizontal=True)
        
        if new_theme != current_theme:
            st.session_state.theme_mode = new_theme
            st.rerun()
        
        st.divider()
        st.page_link("app.py", label="Trang chủ", icon="🏠")
        st.page_link("pages/1_🍳_Dau_Bep_AI.py", label="Phân tích món ăn", icon="🍳")
        st.page_link("pages/2_❄️_Tu_Lanh.py", label="Quản lý Tủ lạnh", icon="❄️")
        st.page_link("pages/3_🌍_Dien_Dan.py", label="Mạng xã hội", icon="🌍")
        
        st.markdown("<div style='flex-grow: 1; min-height: 35vh;'></div>", unsafe_allow_html=True)
        
        with st.container(border=True):
            if st.session_state.get("logged_in"):
                st.markdown(f"<div style='font-weight: 600; font-size:1.1em; margin-bottom:10px;'>👤 {st.session_state.username}</div>", unsafe_allow_html=True)
                if st.button("🔴 Đăng Xuất", use_container_width=True):
                    st.session_state.logged_in = False
                    st.session_state.auth_view = "home"
                    st.switch_page("app.py")
            else:
                st.markdown("<div style='font-size: 0.9em; text-align: center; margin-bottom:10px;'>Bạn chưa đăng nhập</div>", unsafe_allow_html=True)
                if st.button("🔑 Sign In / Up", type="primary", use_container_width=True):
                    st.session_state.auth_view = "login"
                    st.switch_page("app.py")
