import streamlit as st
import requests
from function_for_last_match import get_last_match
from function_for_next_match import next_match

if st.button("Get previous match"):
    try:
        st.write(get_last_match("Antwerp", "Genk"))
    except requests.exceptions.ConnectionError:
        st.error("Doesnt work on all wifi (bouuuuh)")

if st.button("Get next match"):
    st.write(next_match())