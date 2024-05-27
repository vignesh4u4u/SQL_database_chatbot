from huggingface_hub import InferenceClient
import os
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="transformers.utils.generic")
import mysql.connector
import streamlit as st
import pandas as pd

# Initialize chat history and inference client
chat_history = []
client = InferenceClient("mistralai/Mixtral-8x7B-Instruct-v0.1")


def format_prompt(message, history):
    prompt = "<s>"
    for user_prompt, bot_response in history:
        prompt += f"[INST] {user_prompt} [/INST]"
        prompt += f" {bot_response}  "
    prompt += f"[INST] {message} [/INST]"
    return prompt


generate_kwargs = dict(
    temperature=0.7,
    max_new_tokens=3000,
    top_p=0.95,
    repetition_penalty=1.1,
    do_sample=True,
    seed=42,
)


def generate_text(message, history):
    prompt = format_prompt(message, history)
    output = client.text_generation(prompt, **generate_kwargs)
    return output


with st.sidebar:
    database = st.text_input("SQL Database Name", max_chars=100, placeholder="Enter database name")
    password = st.text_input("SQL Database Password", max_chars=100, placeholder="Enter password", type="password")
    host = st.text_input("SQL Database Host Name", max_chars=100, placeholder="Enter host name")
    user = st.text_input("SQL Database User Name", max_chars=100, placeholder="Enter user name")

st.title("💬 Chatbot")
st.caption("🚀 A Streamlit chatbot powered by OpenAI")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


def connect_to_db(host, user, password, database):
    try:
        cnx = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            use_pure=True
        )
        return cnx
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return None


# Ensure table_columns is in session state
if "table_columns" not in st.session_state:
    st.session_state["table_columns"] = {}

if st.button("Connect to Database"):
    cnx = connect_to_db(host, user, password, database)
    if cnx:
        cursor = cnx.cursor()
        query = "SHOW TABLES;"
        cursor.execute(query)
        tables = cursor.fetchall()
        table_columns = {}
        for table in tables:
            table_name = table[0]
            column_query = f"SHOW COLUMNS FROM {table_name};"
            cursor.execute(column_query)
            columns = cursor.fetchall()
            column_names = [column[0] for column in columns]
            table_columns[table_name] = column_names
        cursor.close()
        cnx.close()
        st.session_state["table_columns"] = table_columns
        for table_name, columns in table_columns.items():
            st.write(f"Table: {table_name}")
            st.write(f"Columns: {', '.join(columns)}")

prompt = st.chat_input("Say something")

if prompt:
    st.session_state["messages"].append({"role": "user", "content": prompt})

    table_columns = st.session_state.get("table_columns", {})
    result = str(
        table_columns) + "\n\n\n" + "above given sql table data & corresponding columns given list format.this data into following question depends into automatically find the table name and table corresponding columns name in generate the SQL query output." + "\n" + prompt

    answer = generate_text(result, history=[])
    st.session_state["messages"].append({"role": "assistant", "content": answer})

    for msg in st.session_state["messages"]:
        st.chat_message(msg["role"]).write(msg["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)
