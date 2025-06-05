import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import tempfile
import streamlit.components.v1 as components

st.set_page_config(page_title="Skill Tree Map", layout="wide")
st.title("🚀 Skill Tree 시각화 앱")
st.markdown("Excel 파일을 업로드하고, 팀 → 공정 → 목표 → 기술 구조를 시각화합니다.")

uploaded_file = st.file_uploader("📂 엑셀 또는 CSV 파일을 업로드하세요", type=["xlsx", "csv"])

if uploaded_file:
    if uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    df = df[["팀구분", "공정", "목표/방법", "기술명", "아이템 관련 자료"]].dropna(how="all")

    G = nx.DiGraph()
    for _, row in df.iterrows():
        team, process, goal, tech, url = row
        G.add_edge(str(team), str(process))
        G.add_edge(str(process), str(goal))
        label = f'<a href="{url}" target="_blank">{tech}</a>' if pd.notnull(url) else tech
        G.add_edge(str(goal), label)

    net = Network(height="600px", width="100%", directed=True)
    net.from_nx(G)
    net.repulsion()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode='w', encoding='utf-8') as tmp_file:
        net.save_graph(tmp_file.name)
        html_content = open(tmp_file.name, "r", encoding="utf-8").read()
        components.html(html_content, height=650, scrolling=True)
else:
    st.info("📝 왼쪽에서 엑셀 또는 CSV 파일을 업로드하면 그래프가 표시됩니다.")
    st.write("🔄 앱이 정상적으로 실행 중입니다.")
