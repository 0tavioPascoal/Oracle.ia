import streamlit as st
import database as db
import ai_service as ai
import uuid

# Configurações Iniciais
st.set_page_config(page_title="Mini Gemini", page_icon="♊", layout="wide")
db.init_db()
ai_client = ai.AIService()

# CSS Minimalista Gemini
st.markdown("""
    <style>
    .stApp { background-color: #131314; color: #E3E3E3; }
    [data-testid="stSidebar"] { background-color: #1E1F20; min-width: 300px; }
    .stChatInput { border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

# Inicialização do Estado
if "current_session" not in st.session_state:
    st.session_state.current_session = str(uuid.uuid4())[:8]
    st.session_state.messages = []

# --- SIDEBAR ---
with st.sidebar:
    st.title("♊ Meus Chats")
    
    if st.button("➕ Novo Chat", use_container_width=True):
        st.session_state.current_session = str(uuid.uuid4())[:8]
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.subheader("Histórico")
    
    sessions = db.get_chat_sessions()
    for s_id in sessions:
        hist_raw = db.get_history_by_session(s_id)
        
        # Lógica segura para o título do botão
        if hist_raw:
            # Pega o conteúdo da primeira mensagem (user)
            first_content = hist_raw[0].get('content', '')
            title = first_content[:25] + "..." if len(first_content) > 25 else first_content
        else:
            title = f"Chat {s_id}"
            
        if st.button(f"💬 {title}", key=f"btn_{s_id}", use_container_width=True):
            st.session_state.current_session = s_id
            st.session_state.messages = hist_raw
            st.rerun()

# --- ÁREA DE CHAT ---
st.title("♊ Mini Gemini")
st.info(f"Sessão ativa: {st.session_state.current_session}")

# Renderiza histórico na tela
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input de Mensagem
if prompt := st.chat_input("Pergunte algo..."):
    # Salva e mostra User
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    db.save_message(st.session_state.current_session, "user", prompt)

    # Gera resposta Assistant com CONTEXTO COMPLETO
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        # Enviamos todas as mensagens do state para a IA
        for chunk in ai_client.get_response_stream(st.session_state.messages):
            full_response += chunk
            placeholder.markdown(full_response + "▌")
        
        placeholder.markdown(full_response)
    
    # Salva Assistant
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    db.save_message(st.session_state.current_session, "assistant", full_response)