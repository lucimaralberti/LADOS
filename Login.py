import streamlit as st
from core.auth import fazer_login

def show():
    fazer_login()
