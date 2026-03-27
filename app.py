import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Job Matrix", layout="wide")

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

GRADES = {
    "G6": "平社員",
    "G5B": "シニアスタッフ",
    "G5A": "上位シニアスタッフ",
    "G4": "スーパーバイザー",
    "G3": "課長",
    "G2": "次長"
}

DEPARTMENTS = [
    "人事課","総務課","経理課","財務課","情報管理課",
    "エリア運営課","設備・運搬課","ナーサリー課",
    "マーケティング課","プロセス管理課",
    "インサイドコミュニケーション課","アウトサイドコミュニケーション課"
]

# =========================
# DEFAULT DATA
# =========================
def generate_default():
    data = []
    for dept in DEPARTMENTS:
        for g, name in GRADES.items():
            data.append({
                "department": dept,
                "grade": g,
                "grade_name": name,
                "role_summary": f"{name}として{dept}の業務を担当",
                "responsibility": "担当業務の遂行 / 改善",
                "kpi": "業務達成率 / 品質 / コスト"
            })
    return pd.DataFrame(data)

# =========================
# DB
# =========================
def save_to_db(df, memo):
    supabase.table("job_matrix").insert({
        "data": df.to_dict(orient="records"),
        "memo": memo,
        "created_at": datetime.now().isoformat()
    }).execute()

def load_history():
    res = supabase.table("job_matrix").select("*").order("created_at", desc=True).execute()
    return res.data

# =========================
# SESSION
# =========================
if "df" not in st.session_state:
    st.session_state.df = generate_default()

df = st.session_state.df

# =========================
# HEADER
# =========================
st.title("🌱 Job Matrix（バイオ燃料事業）")

# =========================
# FILTER
# =========================
col1, col2, col3 = st.columns(3)
dept_filter = col1.multiselect("部門", DEPARTMENTS)
grade_filter = col2.multiselect("グレード", list(GRADES.keys()))
keyword = col3.text_input("検索")

filtered = df.copy()

if dept_filter:
    filtered = filtered[filtered["department"].isin(dept_filter)]

if grade_filter:
    filtered = filtered[filtered["grade"].isin(grade_filter)]

if keyword:
    filtered = filtered[filtered.apply(lambda x: keyword in str(x.values), axis=1)]

# =========================
# TABS
# =========================
tab1, tab2, tab3, tab4 = st.tabs(["📊 一覧", "✏️ 編集", "📂 履歴", "⚙️ 設定"])

# =========================
# TAB1 VIEW
# =========================
with tab1:
    st.subheader("一覧ビュー")

    for dept in filtered["department"].unique():
        with st.expander(f"🏢 {dept}", expanded=False):
            sub = filtered[filtered["department"] == dept]
            st.dataframe(sub, use_container_width=True)

# =========================
# TAB2 EDIT
# =========================
with tab2:
    st.subheader("編集")

    edited = st.data_editor(
        filtered,
        use_container_width=True,
        num_rows="dynamic"
    )

    if st.button("💾 保存"):
        st.session_state.df.update(edited)
        save_to_db(st.session_state.df, "manual save")
        st.success("保存完了")

# =========================
# TAB3 HISTORY
# =========================
with tab3:
    st.subheader("履歴")

    history = load_history()

    for h in history:
        with st.expander(f"{h['created_at']} - {h['memo']}"):
            df_hist = pd.DataFrame(h["data"])
            st.dataframe(df_hist)

            if st.button(f"復元 {h['created_at']}"):
                st.session_state.df = df_hist
                st.success("復元完了")

# =========================
# TAB4 SETTINGS
# =========================
with tab4:
    st.subheader("データ管理")

    if st.button("初期化"):
        st.session_state.df = generate_default()
        st.success("リセット完了")

    st.download_button(
        "Excel出力",
        data=st.session_state.df.to_csv(index=False),
        file_name="job_matrix.csv"
    )

    uploaded = st.file_uploader("CSVアップロード")

    if uploaded:
        df_new = pd.read_csv(uploaded)
        st.session_state.df = df_new
        st.success("読み込み完了")
