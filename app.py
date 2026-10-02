import streamlit as st

from rag_service import ask_codebase, search_code

st.set_page_config(
    page_title="PayPorter Kod Asistanı",
    layout="wide",
    initial_sidebar_state="expanded"
)
# ---------- STYLE ----------
st.markdown("""
<style>

    /* Main page */
    .stApp {
        background-color: #f7f8fa;
        color: #1f2933;
    }

    .block-container {
        max-width: 1100px;
        padding-top: 4rem;
        padding-bottom: 4rem;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #202d37;
        border-right: 1px solid #34434f;
    }

    [data-testid="stSidebar"] * {
        color: #f5f5f5;
    }

    /* Headings */
    h1, h2, h3 {
        color: #202d37 !important;
        font-family: Arial, sans-serif;
    }

    h1 {
        font-size: 38px !important;
        font-weight: 650 !important;
        margin-bottom: 8px !important;
    }

    h2 {
        font-size: 25px !important;
        margin-top: 30px !important;
    }

    /* Subtitle */
    .subtitle {
        color: #66727c;
        font-size: 16px;
        margin-bottom: 45px;
    }

    /* PayPorter brand */
    .brand {
        font-size: 28px;
        font-weight: 700;
        color: #f58220;
        margin-bottom: 4px;
    }

    .brand-subtitle {
        font-size: 14px;
        color: #cbd3d9;
        margin-bottom: 28px;
    }

    /* Status */
    .status-box {
        margin-top: 35px;
        padding: 13px 14px;
        border: 1px solid #465660;
        border-radius: 6px;
        font-size: 14px;
        color: #dbe3e8;
    }

    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        background: #54a67a;
        border-radius: 50%;
        margin-right: 8px;
    }

    /* Text area */
    .stTextArea textarea {
        background-color: #ffffff !important;
        color: #202d37 !important;
        border: 1px solid #c7cdd2 !important;
        border-radius: 5px !important;
        min-height: 140px;
        font-size: 15px;
    }

    /* Text input */
    .stTextInput input {
        background-color: #ffffff !important;
        color: #202d37 !important;
        border: 1px solid #c7cdd2 !important;
        border-radius: 5px !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #202d37;
        color: white;
        border: none;
        border-radius: 5px;
        height: 44px;
        font-weight: 500;
    }

    .stButton > button:hover {
        background-color: #f58220;
        color: white;
        border: none;
    }

    /* Divider */
    hr {
        border-color: #e0e4e7;
    }

    /* Hide Streamlit decoration */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

</style>
""", unsafe_allow_html=True)


# ---------- SIDEBAR ----------

with st.sidebar:

    st.markdown(
        '<div class="brand">PayPorter</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="brand-subtitle">Internal Code Assistant</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "Chat",
            "Code Search",
            "Index Management"
        ],
        label_visibility="collapsed"
    )

    st.markdown(
        """
        <div class="status-box">
            <span class="status-dot"></span>
            Local LLM connected
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption("Private local environment")


# ---------- HEADER ----------

st.title("PayPorter Code Assistant")

st.markdown(
    '<div class="subtitle">Private assistant for internal source code analysis</div>',
    unsafe_allow_html=True
)


# ---------- CHAT ----------

if page == "Chat":

    # ---------- CONVERSATION STATE ----------
    if "conversations" not in st.session_state:
        st.session_state.conversations = {
            "Sohbet 1": []
        }

    if "active_conversation" not in st.session_state:
        st.session_state.active_conversation = "Sohbet 1"

    # ---------- CHAT SIDEBAR ----------
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Sohbetler")

    if st.sidebar.button("+ Yeni Sohbet", use_container_width=True):
        # Mevcut aktif sohbet zaten bossa yeni bir tane daha olusturma
        current_name = st.session_state.active_conversation
        current_chat = st.session_state.conversations[current_name]

        if current_chat:
            number = len(st.session_state.conversations) + 1
            new_name = f"Sohbet {number}"

            while new_name in st.session_state.conversations:
                number += 1
                new_name = f"Sohbet {number}"

            st.session_state.conversations[new_name] = []
            st.session_state.active_conversation = new_name

        st.rerun()

    for conversation_name in list(st.session_state.conversations.keys()):
        if st.sidebar.button(
            conversation_name,
            key=f"conversation_{conversation_name}",
            use_container_width=True
        ):
            st.session_state.active_conversation = conversation_name
            st.rerun()

    active_name = st.session_state.active_conversation
    chat_history = st.session_state.conversations[active_name]

    # ---------- MODEL ----------
    model_name = st.selectbox(
        "Model",
        ["qwen3:4b", "deepseek-r1:7b"],
        index=0
    )

    st.caption(f"Aktif sohbet: {active_name}")

    # ---------- OLD MESSAGES ----------
    for message in chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("sources"):
                with st.expander("Sources"):
                    for source in message["sources"]:
                        st.write(
                            f'{source["file"]} | '
                            f'Lines: {source["start_line"]}-{source["end_line"]} | '
                            f'Similarity: {source["score"]:.3f}'
                        )

    # ---------- INPUT ----------
    question = st.chat_input("Kod tabanınız hakkında bir soru sorun...")

    if question:

        # İlk soru sorulduğunda sohbet başlığını otomatik oluştur
        if len(chat_history) == 0:
            old_name = active_name

            clean_title = " ".join(question.strip().split())

            if len(clean_title) > 38:
                clean_title = clean_title[:38].rstrip() + "..."

            # Aynı isimde sohbet varsa benzersiz hale getir
            new_name = clean_title
            counter = 2
            while new_name in st.session_state.conversations:
                new_name = f"{clean_title} ({counter})"
                counter += 1

            st.session_state.conversations[new_name] = st.session_state.conversations.pop(old_name)
            st.session_state.active_conversation = new_name
            active_name = new_name
            chat_history = st.session_state.conversations[new_name]

        chat_history.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Kaynak kod analiz ediliyor..."):
                try:
                    result = ask_codebase(
                        question,
                        chat_history[:-1],
                        model_name=model_name
                    )

                    answer = result["answer"]
                    sources = result.get("sources", [])

                    st.markdown(answer)

                    if sources:
                        with st.expander("Sources"):
                            for source in sources:
                                st.write(
                                    f'{source["file"]} | '
                                    f'Lines: {source["start_line"]}-{source["end_line"]} | '
                                    f'Similarity: {source["score"]:.3f}'
                                )

                    chat_history.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })

                except Exception as e:
                    st.error(f"Error: {e}")

# ---------- SEARCH ----------

elif page == "Code Search":

    st.header("Code Search")

    st.write(
        "Search the indexed source code for files, functions and services."
    )

    search_query = st.text_input(
        "Search",
        placeholder="Example: authentication service"
    )

    if st.button(
        "Search",
        use_container_width=True
    ):

        if search_query.strip():
            results = search_code(search_query, top_k=5)

            st.markdown("### Search Results")

            for score, chunk in results:
                with st.expander(chunk["file"]):
                    st.write(
                        f'Lines: {chunk["start_line"]}-{chunk["end_line"]}'
                    )
                    st.write(
                        f'Similarity: {score:.3f}'
                    )

        else:

            st.warning(
                "Enter a search term."
            )


# ---------- INDEX ----------

elif page == "Index Management":

    st.header("Index Management")

    st.write(
        "Manage the local source-code index used by the RAG system."
    )

    st.markdown("---")

    project_path = st.text_input(
        "Source directory",
        value="company_code",
        placeholder="Example: /Users/username/Desktop/my-project"
    )

    st.write("Current source directory")
    st.code(project_path)

    st.write(
        "Rebuild the index after source-code files are changed."
    )

    if st.button(
        "Rebuild Index",
        use_container_width=True
    ):
        import subprocess

        with st.spinner("Rebuilding index..."):
            result = subprocess.run(
                ["python", "build_index.py", project_path],
                capture_output=True,
                text=True
            )

        if result.returncode == 0:
            st.success("Index rebuilt successfully.")
            st.code(result.stdout)
        else:
            st.error("Index rebuild failed.")
            st.code(result.stderr)

    # ---------- FOOTER ----------

    st.markdown("---")

    st.caption(
        "PayPorter Internal Tool · Local processing"
    )
