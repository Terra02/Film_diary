import streamlit as st
import pandas as pd
import httpx
import asyncio
import os

st.set_page_config(
    page_title="Главная панель",
    layout="wide"
)

st.title("Главная панель управления")

def _get_dashboard_password() -> str:
    env_password = os.getenv("MAIN_DASHBOARD_PASSWORD", "")
    if env_password:
        return env_password
    try:
        if "main_dashboard_password" in st.secrets:
            return str(st.secrets["main_dashboard_password"])
    except FileNotFoundError:
        return ""
    return ""

def require_password() -> None:
    expected_password = _get_dashboard_password()
    if not expected_password:
        st.warning(
            "Пароль для доступа не настроен."
        )
        st.stop()

    if not st.session_state.get("main_dashboard_auth"):
        password = st.text_input("Пароль", type="password")
        if password:
            if password == expected_password:
                st.session_state["main_dashboard_auth"] = True
            else:
                st.error("Неверный пароль")
                st.stop()
        else:
            st.info("Введите пароль для доступа к панели.")
            st.stop()

async def get_quick_stats():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://api:8000/api/v1/analytics/system/overview")
            if response.status_code == 200:
                return response.json()
    except Exception:
        return None
    return None

async def get_registered_users(limit: int = 1000):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://api:8000/api/v1/users",
                params={"skip": 0, "limit": limit},
            )
            if response.status_code == 200:
                return response.json()
    except Exception:
        return []
    return []

async def main():
    require_password()
    stats = await get_quick_stats()
    users = await get_registered_users()
    
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Пользователи", stats.get('total_users', 0))
        with col2:
            st.metric("🎬 Контент", stats.get('total_content', 0))
        with col3:
            st.metric("📊 Просмотры", stats.get('total_views', 0))
    else:
        st.error("Не удалось загрузить данные")

if __name__ == "__main__":
    asyncio.run(main())