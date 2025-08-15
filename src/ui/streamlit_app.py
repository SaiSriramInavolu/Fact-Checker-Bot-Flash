import streamlit as st
import re
import os
import logging
from src.fact_checker import FactChecker
from config.settings import settings
from src.database import load_all_fact_checks, DATABASE_FILE

def strip_markdown(text):
    text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^\*]+)\*', r'\1', text)
    text = re.sub(r'```[^`]*```', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    return text

def clear_history_callback():
    if os.path.exists(DATABASE_FILE):
        os.remove(DATABASE_FILE)
    st.session_state.fact_history = []
    st.session_state.selected_fact_index = None
    st.session_state.fact_checker_instance = FactChecker(model_name=settings.LLM_MODEL, search_tool_name=settings.SEARCH_TOOL)
    st.session_state.clear_flag = True
    st.success("History and database cleared!")

if 'fact_checker_instance' not in st.session_state:
    st.session_state.fact_checker_instance = FactChecker(model_name=settings.LLM_MODEL, search_tool_name=settings.SEARCH_TOOL)
fact_checker = st.session_state.fact_checker_instance

st.set_page_config(page_title="AI Fact-Checker Bot", layout="wide")

st.title("🤖 AI Fact-Checker Bot")
st.subheader("Verify claims with the power of AI and web search.")

if "fact_history" not in st.session_state:
    logging.info("Loading history from database...")
    st.session_state.fact_history = load_all_fact_checks()
    logging.info(f"Loaded {len(st.session_state.fact_history)} items into session state.")
if "selected_fact_index" not in st.session_state:
    st.session_state.selected_fact_index = None

claim_input = st.text_area("Enter the claim you want to fact-check:", height=100, key="claim_input")

if st.button("Fact-Check"):
    if claim_input:
        with st.spinner("Fact-checking in progress..."):
            try:
                result = fact_checker.process_claim(claim_input)
                st.session_state.fact_history.append(result) 
                st.success("Fact-checking complete!")
                st.session_state.selected_fact_index = len(st.session_state.fact_history) - 1
            except Exception as e:
                st.error(f"An error occurred during fact-checking: {e}")
    else:
        st.warning("Please enter a claim to fact-check.")

st.markdown("---")

st.sidebar.header("Fact-Check History")

if st.session_state.fact_history:
    history_options = []
    for i, entry in enumerate(st.session_state.fact_history):
        display_claim = strip_markdown(entry['claim'])
        truncated_claim = display_claim[:50] + "..." if len(display_claim) > 50 else display_claim
        history_options.append(f"Claim {i+1}: {truncated_claim}")
    
    current_index = st.session_state.selected_fact_index if st.session_state.selected_fact_index is not None else 0
    
    selected_option = st.sidebar.radio(
        "Select a past fact-check:",
        options=history_options,
        index=current_index,
        key="history_radio"
    )
    
    st.session_state.selected_fact_index = history_options.index(selected_option)

else:
    st.sidebar.info("No fact-checks yet.")

st.sidebar.markdown("---")
st.sidebar.button("Clear All History", on_click=clear_history_callback)

if "clear_flag" in st.session_state and st.session_state.clear_flag:
    st.session_state.clear_flag = False
    st.rerun()

if st.session_state.selected_fact_index is not None and st.session_state.fact_history:
    selected_entry = st.session_state.fact_history[st.session_state.selected_fact_index]
    
    st.header(f"Details for Claim {st.session_state.selected_fact_index + 1}")
    
    with st.chat_message("user"):
        st.write(f"**Claim:** {selected_entry['claim']}")
        if 'claim_type' in selected_entry and selected_entry['claim_type']:
            st.markdown(f"**Claim Type:** `{selected_entry['claim_type']}`")

    with st.chat_message("assistant"):
        st.write(f"**Initial Response:** {selected_entry['initial_response']}")
        
        with st.expander("View Detailed Process"):
            st.markdown("#### Assumptions and Verdicts:")
            for av in selected_entry['assumptions_verdicts']:
                st.markdown(f"- {av}")
            
            st.markdown("#### Gathered Evidence:")
            for ge in selected_entry['gathered_evidence']:
                st.markdown(f"```\n{ge}\n```")
        
        st.write(f"**Final Answer:** {selected_entry['final_answer']}")
else:
    st.info("Select a fact-check from the sidebar to view its details.")
