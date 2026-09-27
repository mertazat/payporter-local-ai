import streamlit as st

from rag_service import ask_codebase, search_code

st.set_page_config(
    page_title="PayPorter Code Assistant",
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

    st.header("Ask your codebase")

    st.write(
        "Ask questions about the indexed source code. "
        "The assistant retrieves relevant code before generating an answer."
    )

    question = st.text_area(
        "Question",
        placeholder="Example: How does the authentication service work?"
    )

    if st.button(
        "Ask",
        use_container_width=True
    ):
        if question.strip():
            with st.spinner("Analyzing source code..."):
                try:
                    result = ask_codebase(question)

                    st.markdown("### Answer")
                    st.markdown(result["answer"])

                    sources = result.get("sources", [])

                    if sources:
                        st.markdown("### Sources")

                        for source in sources:
                            with st.expander(source["file"]):
                                st.write(
                                    f'Lines: {source["start_line"]}-{source["end_line"]}'
                                )
                                st.write(
                                    f'Similarity: {source["score"]:.3f}'
                                )

                except Exception as e:
                    st.error(f"Error: {e}")

        else:
            st.warning("Enter a question first.")

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

    st.write("Current source directory")

    st.code("company_code/")

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
                ["python", "build_index.py"],
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
