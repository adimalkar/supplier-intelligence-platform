import streamlit as st
import time
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AI Assistant", layout="wide")
st.title("AI Assistant")
st.markdown("Ask questions about supplier performance, root cause analysis, or generate reports.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "data" in message and message["data"] is not None:
            if message.get("visualization_type") == "bar_chart":
                df = pd.DataFrame(message["data"])
                fig = px.bar(df, x=df.columns[0], y=df.columns[1])
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
                st.plotly_chart(fig, use_container_width=True)
            elif message.get("visualization_type") == "table":
                st.dataframe(pd.DataFrame(message["data"]), use_container_width=True)

import asyncio
from src.agentic_ai.agent import SupplierIntelligenceAgent
from src.common.db.connection import SessionLocal

# Ensure OpenAI API Key is in environment for Agentic AI to work
import os
from src.common.config import settings

# Initialize real agent
if "agent" not in st.session_state:
    # Use SessionLocal for DB factory
    llm_config = {"provider": "openai", "model_name": "gpt-4o", "temperature": 0.0}
    # For openai you need OPENAI_API_KEY in environment
    st.session_state.agent = SupplierIntelligenceAgent(db_session_factory=SessionLocal, llm_config=llm_config)

agent = st.session_state.agent

# Accept user input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        # Simulate thinking
        with st.spinner("Analyzing..."):
            # Run the async agent query synchronously for streamlit
            try:
                response_obj = asyncio.run(agent.query(prompt))
                response = {
                    "text": response_obj.text,
                    "data": response_obj.data,
                    "visualization_type": response_obj.visualization_type,
                    "sources": response_obj.sources
                }
            except Exception as e:
                response = {
                    "text": f"Error: {e}",
                    "data": None,
                    "visualization_type": None,
                    "sources": []
                }
            
        message_placeholder.markdown(response["text"])
        
        if response.get("data") is not None:
            if response.get("visualization_type") == "bar_chart":
                df = pd.DataFrame(response["data"])
                fig = px.bar(df, x=df.columns[0], y=df.columns[1])
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
                st.plotly_chart(fig, use_container_width=True)
            elif response.get("visualization_type") == "table":
                st.dataframe(pd.DataFrame(response["data"]), use_container_width=True)
                
        if response.get("sources"):
            st.caption(f"Sources: {', '.join(response['sources'])}")
            
    # Add assistant response to chat history
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response["text"],
        "data": response.get("data"),
        "visualization_type": response.get("visualization_type"),
        "sources": response.get("sources")
    })
