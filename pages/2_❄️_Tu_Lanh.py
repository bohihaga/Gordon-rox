import streamlit as st
from utils import require_login, load_db, save_db, USER_DB

st.set_page_config(page_title="Tủ Lạnh", page_icon="❄️")
require_login()

st.title(f"❄️ Tủ Lạnh Của {st.session_state.username}")
st.write("Quản lý nguyên liệu để AI có thể tự động lấy thông tin.")

users = load_db(USER_DB)
my_fridge = users[st.session_state.username].get("fridge", [])

with st.form("add_item"):
    new_item = st.text_input("Thêm đồ vào tủ (VD: Hành tây, Thịt bò...)")
    if st.form_submit_button("Thêm vào tủ"):
        if new_item:
            my_fridge.append(new_item)
            users[st.session_state.username]["fridge"] = my_fridge
            save_db(USER_DB, users)
            st.success("Đã thêm!")
            st.rerun()

st.divider()
for i, item in enumerate(my_fridge):
    col1, col2 = st.columns([4, 1])
    with col1: st.markdown(f"- **{item}**")
    with col2: 
        if st.button("Xóa", key=f"del_{i}"):
            my_fridge.pop(i)
            users[st.session_state.username]["fridge"] = my_fridge
            save_db(USER_DB, users)
            st.rerun()