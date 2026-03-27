import streamlit as st
from supabase import create_client

st.title("Supabase test")

try:
    supabase = create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )
    st.success("create_client 成功")
except Exception as e:
    st.error(f"create_client 失敗: {repr(e)}")
