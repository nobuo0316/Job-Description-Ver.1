import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Job Matrix", layout="wide")
st.title("🌱 Job Matrix (REST版)")

SUPABASE_URL = st.secrets["SUPABASE_URL"].rstrip("/")
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

def headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

def save_to_db(df):
    requests.post(
        f"{SUPABASE_URL}/rest/v1/job_matrix",
        headers=headers(),
        json={"data": df.to_dict(orient="records"), "created_at": datetime.now().isoformat()}
    )

def load_history():
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/job_matrix",
        headers=headers(),
        params={"select":"*","order":"created_at.desc"}
    )
    return r.json()

df = pd.DataFrame([{"department":"人事課","grade":"G6","role":"sample"}])
st.dataframe(df)

if st.button("保存"):
    save_to_db(df)
    st.success("saved")

if st.button("履歴取得"):
    st.write(load_history())
