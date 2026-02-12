import os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


import streamlit as st
from graph.mygraph import graph
from connections.connect import set_weaviate_client, get_weaviate_client
from frontend.style import style
from frontend.streaming import *



@st.cache_resource
def get_weaviate_client1():
    return get_weaviate_client()

_wv_client = None
wv_client = get_weaviate_client1()
set_weaviate_client(wv_client)


st.set_page_config(
    page_title="...",
    layout="wide",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": None,
    },
)

st.markdown(style, unsafe_allow_html=True)


st.title("Поддержка сотрудников по внутренним нормативным документам")

organization_keys={
    'Альфа Ойл':'АЛЬФА ОЙЛ',
    'Трейд Ойл':'ТРЕЙД ОЙЛ',
    "Seсuriforce":"SECURIFORCE",
    "ОКС":"ОКС",
    "Munaizat":"MUNAIZAT",
    None:None
}

left, right = st.columns([.15, .75],width=1350)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "organization" not in st.session_state:
    st.session_state.organization = None
plan_steps = None

with left:
    with st.container(border=True,height=500):
        options = [k for k in organization_keys.keys() if k is not None]
        organization = st.pills("Организация", options,key="pills1",)
        st.session_state["organization"] = organization_keys[organization]


with right:
    chat_area = st.container(border=True, height=500)
    with chat_area:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

prompt = st.chat_input("Вопрос:")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_area:
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            answer_box = st.empty()
            full_answer = ""

            # --- NEW ---
            plan_steps = None   # 🧠 мысли / план

            sql_query_text = None
            sql_result_text = None
            wv_query_text = None
            wv_result_text = None

            for ev in sync_stream(stream_text(
                graph,
                st.session_state.messages,
                st.session_state.get("organization")
            )):
                print(f'event{ev["type"]}')
                # 🧠 ПЛАН (МЫСЛИ)
                if ev["type"] == "plan":
                    plan_steps = ev["data"]

                # 💬 ОСНОВНОЙ ТЕКСТ
                elif ev["type"] == "text":
                    full_answer += ev["data"]
                    answer_box.markdown(full_answer)

                # 🗄 SQL
                elif ev["type"] == "sql":
                    sql_query_text = ev["data"]

                elif ev["type"] == "sql_result":
                    sql_result_text = ev["data"]

                # 📚 WEAVIATE
                elif ev["type"] == "weaviate":
                    wv_query_text = ev["data"]

                elif ev["type"] == "weaviate_result":
                    wv_result_text = ev["data"]

            # ===============================
            # 🧠 ПОКАЗЫВАЕМ ПЛАН (КРАСИВО)
            # ===============================
            if plan_steps:
                with st.expander("🧠 мысли ассистента)", expanded=False):
                    for i, step in enumerate(plan_steps, 1):
                        st.markdown(f"**{i}.** {step}")

            # ===============================
            # SQL / WEAVIATE (КАК У ТЕБЯ)
            # ===============================
            if sql_query_text:
                with st.expander("SQL запрос", expanded=False):
                    st.markdown(f"```sql\n{sql_query_text}\n```")

            if sql_result_text:
                with st.expander("Результат SQL", expanded=False):
                    st.markdown(f"```\n{sql_result_text}\n```")

            if wv_query_text:
                with st.expander("Weaviate запрос", expanded=False):
                    st.markdown(f"```json\n{wv_query_text}\n```")

            if wv_result_text:
                with st.expander("Результат Weaviate", expanded=False):
                    st.markdown(f"```\n{wv_result_text}\n```")
    st.session_state.messages.append({"role": "assistant", "content": full_answer})