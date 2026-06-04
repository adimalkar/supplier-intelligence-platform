import logging
import streamlit as st
from sqlalchemy.orm import Session
from src.common.db.connection import get_engine, init_session_factory, get_session

logger = logging.getLogger(__name__)

@st.cache_resource
def init_db():
    """Initialize the database session factory."""
    init_session_factory()
    return get_engine()

def get_db_session() -> Session:
    """
    Get a database session.
    Use inside a context manager:
    with get_db_session() as session:
        ...
    """
    init_db()  # Ensure it's initialized
    return get_session()
