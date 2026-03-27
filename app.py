import streamlit as st
from supabase import create_client, Client

st.set_page_config(page_title="Supabase Test", layout="wide")
st.title("Supabase Test")

@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

try:
    client = get_supabase()
    st.success("Supabase接続OK")
except Exception as e:
    st.error(f"Supabase接続失敗: {repr(e)}")
    st.stop()
