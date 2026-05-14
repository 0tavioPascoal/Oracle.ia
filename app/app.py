import uuid
import streamlit as st
import database as db
import ai_service as ai

st.set_page_config(
    page_title="Oracle.ia",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

db.init_db()
ai_client = ai.AIService()

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&family=Roboto:wght@300;400;500&display=swap');

        /* Variáveis de Cores Gemini Dark */
        :root {
            --bg-main: #131314;
            --bg-sidebar: #1e1f20;
            --text-main: #e3e3e3;
            --text-secondary: #c4c7c5;
            --hover-color: #333537;
            --accent-blue: #8ab4f8;
            --border-color: #444746;
        }

        html, body, [class*="css"] {
            font-family: 'Roboto', sans-serif;
            background-color: var(--bg-main);
            color: var(--text-main);
        }

        .stApp {
            background: var(--bg-main);
        }

        .block-container {
            max-width: 880px;
            padding-top: 2rem;
            padding-bottom: 160px;
        }

        [data-testid="stSidebar"] {
            background-color: var(--bg-sidebar) !important;
            border: none !important;
        }

        [data-testid="stSidebar"] .stButton button {
            border-radius: 50px !important;
            background-color: #1a1c1e !important;
            border: 1px solid var(--border-color) !important;
            color: var(--text-main) !important;
            padding: 10px 20px !important;
            font-weight: 500 !important;
            transition: all 0.3s;
            text-align: center !important;
            justify-content: center !important;
        }

        [data-testid="stSidebar"] .stButton button:hover {
            background-color: var(--hover-color) !important;
            border-color: #8e918f !important;
        }

        div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column"] > .stButton button {
            background: transparent !important;
            border: none !important;
            border-radius: 0 50px 50px 0 !important;
            text-align: left !important;
            justify-content: flex-start !important;
            font-size: 14px !important;
            margin-bottom: 2px !important;
            width: 100% !important;
            color: var(--text-secondary) !important;
        }

        .sidebar-card {
            background: #282a2c;
            border-radius: 12px;
            padding: 16px;
            margin: 10px 0;
            font-size: 13px;
            color: var(--text-secondary);
            border: 1px solid rgba(255,255,255,0.05);
        }

        .hero-container {
            margin-top: 5vh;
            margin-bottom: 2rem;
        }

        .hero-title {
            font-family: 'Google Sans', sans-serif;
            font-size: 3.5rem;
            font-weight: 500;
            background: linear-gradient(90deg, #4285f4, #9b72cb, #d96570, #4285f4);
            background-size: 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradient-flow 6s linear infinite;
        }

        @keyframes gradient-flow {
            0% { background-position: 0%; }
            100% { background-position: 200%; }
        }

        [data-testid="stChatMessage"] {
            background-color: transparent !important;
            margin-bottom: 1.5rem !important;
            border: none !important;
        }

        [data-testid="stChatMessageContent"] p {
            font-size: 16px;
            line-height: 1.6;
            color: var(--text-main);
        }

        [data-testid="chatAvatarIcon-user"] { background-color: #565869 !important; }
        [data-testid="chatAvatarIcon-assistant"] { 
            background: linear-gradient(45deg, #4285f4, #9b72cb) !important; 
        }

        code {
            color: #8ab4f8 !important;
            background: #212121 !important;
            padding: 0.2rem 0.4rem !important;
            border-radius: 4px !important;
            font-family: 'JetBrains Mono', monospace !important;
        }

        pre {
            background: #0e0e0e !important;
            border: 1px solid #333 !important;
            border-radius: 16px !important;
            padding: 1.5rem !important;
        }

        [data-testid="stChatInput"] {
            background-color: var(--bg-main) !important;
        }

        [data-testid="stChatInput"] > div {
            border-radius: 32px !important;
            border: 1px solid var(--border-color) !important;
            background-color: #1e1f20 !important;
            padding: 8px 16px !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }

        [data-testid="stChatInput"] textarea {
            color: var(--text-main) !important;
            font-size: 16px !important;
        }

        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-thumb { background: #3c4043; border-radius: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

def create_new_session():
    st.session_state.current_session = str(uuid.uuid4())[:8]
    st.session_state.messages = []

if "current_session" not in st.session_state:
    create_new_session()

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.markdown('<h2 style="font-family:Google Sans; color:white; font-size:22px; margin-bottom:20px;">Oracle.ia</h2>', unsafe_allow_html=True)
    
    if st.button("➕ Novo Chat", use_container_width=True):
        create_new_session()
        st.rerun()

    st.markdown('<div style="margin-top:25px; margin-bottom:10px; font-size:12px; color:#9aa0a6; font-weight:500; padding-left:10px;">RECENTE</div>', unsafe_allow_html=True)
    
    sessions = db.get_chat_sessions()
    if not sessions:
        st.caption("Sem conversas recentes.")

    for session in sessions:
        session_id = session["session_id"]
        title = session["title"]
        if st.button(f"💬 {title[:25]}...", key=f"chat_{session_id}", use_container_width=True):
            st.session_state.current_session = session_id
            st.session_state.messages = db.get_history_by_session(session_id)
            st.rerun()

    st.markdown('<div style="position: fixed; bottom: 20px; width: 260px;">', unsafe_allow_html=True)
    st.divider()
    
    total_messages = db.count_messages_by_session(st.session_state.current_session)
    st.markdown(
        f"""
        <div class="sidebar-card">
            <strong>Sessão Atual</strong><br>
            <span style="font-size:11px; opacity:0.7">ID: {st.session_state.current_session}</span><br>
            <span style="font-size:11px; opacity:0.7">Mensagens: {total_messages}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if total_messages > 0:
        if st.button("🗑️ Limpar Conversa", use_container_width=True):
            db.delete_session(st.session_state.current_session)
            create_new_session()
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

if len(st.session_state.messages) == 0:
    st.markdown(
        """
        <div class="hero-container">
            <h1 class="hero-title">Olá, desenvolvedor</h1>
            <p style="color:#c4c7c5; font-size:1.8rem; font-family:Google Sans; margin-top:-10px;">
                Como posso ajudar seu código hoje?
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    with st.chat_message("assistant"):
        st.markdown("Olá! Eu sou o **Oracle.ia**. Estou pronto para processar suas solicitações mantendo o contexto histórico via PostgreSQL.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Digite algo aqui...")

if prompt:
    user_message = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_message)
    db.save_message(st.session_state.current_session, "user", prompt)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        for chunk in ai_client.get_response_stream(st.session_state.messages):
            full_response += chunk
            placeholder.markdown(full_response + "▌")

        placeholder.markdown(full_response)

    assistant_message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(assistant_message)
    db.save_message(st.session_state.current_session, "assistant", full_response)

    st.rerun()