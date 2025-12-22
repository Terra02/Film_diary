import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import altair as alt
import httpx
import pandas as pd
import streamlit as st

DEFAULT_API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
DATA_LIMIT = 300

st.set_page_config(
    page_title="Аналитика",
    layout="wide",
)

def _build_client(api_url: str) -> httpx.Client:
    return httpx.Client(base_url=api_url, timeout=10.0)

def _time_range_to_days(label: str) -> int:
    mapping = {
        "Все время": 36500,
    }
    return mapping.get(label, 30)

@st.cache_data(show_spinner=False, ttl=120)
def fetch_user_analytics(api_url: str, user_id: int, days: int) -> Optional[Dict[str, Any]]:
    try:
        with _build_client(api_url) as client:
            response = client.get(f"/api/v1/analytics/user/{user_id}", params={"days": days})
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        st.error(f"Не удалось загрузить аналитику пользователя: {exc}")
        return None
    
@st.cache_data(show_spinner=False, ttl=120)
def fetch_user_timeline(api_url: str, user_id: int, period: str = "monthly") -> List[Dict[str, Any]]:
    try:
        with _build_client(api_url) as client:
            response = client.get(
                f"/api/v1/analytics/user/{user_id}/timeline", params={"period": period}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", []) if isinstance(data, dict) else []
    except httpx.HTTPError as exc:
        st.error(f"Не удалось загрузить временную аналитику: {exc}")
        return []


@st.cache_data(show_spinner=False, ttl=120)
def fetch_view_history(api_url: str, user_id: int, limit: int = DATA_LIMIT) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    page_size = min(limit, 100)
    try:
        with _build_client(api_url) as client:
            skip = 0
            while len(records) < limit:
                response = client.get(
                    f"/api/v1/view-history/user/{user_id}",
                    params={"skip": skip, "limit": min(page_size, limit - len(records))},
                )
                response.raise_for_status()
                chunk = response.json()
                if not chunk:
                    break
                records.extend(chunk)
                if len(chunk) < page_size:
                    break
                skip += page_size
    except httpx.HTTPError as exc:
        st.error(f"Не удалось загрузить историю просмотров: {exc}")
    return records


@st.cache_data(show_spinner=False, ttl=120)
def resolve_user_id(api_url: str, identifier: int) -> Optional[int]:
    try:
        with _build_client(api_url) as client:
            tg_response = client.get(f"/api/v1/users/telegram/{identifier}")
            if tg_response.status_code == 200:
                return tg_response.json().get("id")

            st.warning("Пользователь не найден. Проверьте Telegram ID.")
    except httpx.HTTPError as exc:
        st.error(f"Не удалось определить пользователя: {exc}")
    return None


def build_dataframe(
    history: List[Dict[str, Any]], start_date: datetime, end_date: datetime
) -> pd.DataFrame:
    rows = []
    for record in history:
        watched_at = pd.to_datetime(record.get("watched_at"))
        if not pd.isna(watched_at) and watched_at.tzinfo is not None:
            watched_at = watched_at.tz_convert(None)
        if pd.isna(watched_at) or watched_at < start_date or watched_at > end_date:
            continue

        content = record.get("content") or {}
        content_type = content.get("content_type") or record.get("content_type")
        rows.append(
            {
                "title": content.get("title")
                or record.get("content_title")
                or "Без названия",
                "content_type": content_type,
                   "duration_minutes": content.get("duration_minutes")
                or record.get("duration_minutes"),
                "user_rating": record.get("rating"),
                "watch_date": watched_at,
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df["watch_day"] = df["watch_date"].dt.date.astype(str)
    df["watch_month"] = df["watch_date"].dt.to_period("M").astype(str)
    df["duration_minutes"] = df.get("duration_minutes")
    df["content_type_display"] = (
        df["content_type"].map({"movie": "Фильм", "series": "Сериал"}).fillna("Неизвестно")
    )
    return df



def _filter_timeline(
    data: List[Dict[str, Any]], start: datetime, end: datetime
) -> pd.DataFrame:
    timeline_rows = []
    for row in data:
        period_raw = row.get("period") or row.get("month")
        if not period_raw:
            continue
        period_dt = pd.to_datetime(period_raw)
        if not pd.isna(period_dt) and period_dt.tzinfo is not None:
            period_dt = period_dt.tz_convert(None)
        if pd.isna(period_dt) or period_dt < start or period_dt > end:
            continue
        timeline_rows.append(
            {
                "watch_period": period_dt.strftime("%Y-%m"),
                "Количество": row.get("view_count", 0),
            }
        )
    return pd.DataFrame(timeline_rows)



st.title("🎬 Аналитика Просмотров")

st.markdown(
    "Здесь вы найдете все ключевые показатели и статистику по просмотренным фильмам и сериалам")

st.sidebar.header("Фильтры и настройки")
api_url = DEFAULT_API_URL
user_identifier = st.sidebar.text_input(
    "Telegram ID",
    help="Можно вводить Telegram ID — система найдёт нужного пользователя автоматически.",
)

year_options = list(range(2020, datetime.now().year + 1))
selected_year = st.sidebar.selectbox(
    "Год для помесячной статистики",
    options=year_options,
    index=len(year_options) - 1,
)

days = _time_range_to_days("Все время")
analytics_days = min(days,365)
end_date = datetime.now()
start_date = end_date - timedelta(days=days)

resolved_user_id = resolve_user_id(api_url, user_identifier)
if resolved_user_id is None:
    st.stop()

analytics = fetch_user_analytics(api_url, resolved_user_id, analytics_days)
use_analytics = days <= analytics_days
timeline = fetch_user_timeline(api_url, resolved_user_id, period="monthly")
history_records = fetch_view_history(api_url, resolved_user_id, limit=DATA_LIMIT)
df = build_dataframe(history_records, start_date, end_date)

if df.empty and not analytics:
    st.warning("Нет данных для отображения. Проверьте фильтры или наличие записей в базе.")
    st.stop()



st.header("📊 Ключевые Показатели")

total_items = (
    analytics.get("total_views") if analytics and use_analytics else len(df)
)
total_movies = (
    analytics.get("movies_views")
    if analytics and use_analytics
    else int((df["content_type"] == "movie").sum())
)
total_series_views = (
    analytics.get("series_views")
    if analytics and use_analytics
    else int((df["content_type"] == "series").sum())
)
avg_rating = (
    analytics.get("average_rating")
    if analytics and use_analytics
    else round(df["user_rating"].dropna().mean(), 2)
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Всего Просмотров", value=total_items)
    st.metric(label="Средний Рейтинг", value=avg_rating)
with col2: 
    st.metric(label="Всего Фильмов", value=total_movies)
    st.metric(label="Всего Сериалов", value=total_series_views)

st.divider()


st.header("📈 Визуализация Данных")

st.subheader("Количество Просмотров по Месяцам")
monthly_start = datetime(selected_year, 1, 1)
monthly_end = datetime(selected_year, 12, 31, 23, 59, 59)
monthly_counts = _filter_timeline(timeline, monthly_start, monthly_end)
if monthly_counts.empty and not df.empty:
    monthly_counts = (
        df[df["watch_date"].dt.year == selected_year]
        .groupby("watch_month")
        .size()
        .reset_index(name="Количество")
    )
    monthly_counts = monthly_counts.rename(columns={"watch_month": "watch_period"})

if not monthly_counts.empty:
    monthly_counts = monthly_counts.sort_values("watch_period")

if monthly_counts.empty:
    st.info("Недостаточно данных для построения графика по месяцам.")
else:
    chart_monthly = alt.Chart(monthly_counts).mark_bar(color="#6366f1").encode(
        x=alt.X("watch_period", title="Месяц просмотра", sort="ascending"),
        y=alt.Y("Количество", title="Количество просмотров"),
        tooltip=["watch_period", "Количество"],
    ).properties(height=300)

    st.altair_chart(chart_monthly.interactive(), use_container_width=True)

type_counts = df.groupby("content_type_display").size().reset_index(name="Количество")

if type_counts.empty:
    st.info("Нет данных для построения диаграммы по типам контента.")
else:
    rating_column, chart_column = st.columns([1, 2])
    with rating_column:
            st.markdown("**Средний рейтинг**")
            rating_value = avg_rating if avg_rating else 0
            rating_data = pd.DataFrame([{"label": "", "value": rating_value}])
            rating_chart = (
                alt.Chart(rating_data)
                .mark_bar(color="#6366f1")
                .encode(
                    x=alt.X(
                        "value:Q",
                        title="Оценка",
                        scale=alt.Scale(domain=[0, 10]),
                    ),
                    y=alt.YOffsetDatum("label:N", axis=None),
                    tooltip=[alt.Tooltip("value:Q", title="Средний рейтинг")],
                )
                .properties(height=80)
            )
            st.altair_chart(rating_chart, use_container_width=True)

    with chart_column:
        st.markdown("**Соотношение фильмов и сериалов**")
        chart_type = alt.Chart(type_counts).mark_arc(outerRadius=120).encode(
            theta=alt.Theta(field="Количество", type="quantitative"),
            color=alt.Color(field="content_type_display", title="Тип контента"),
            tooltip=["content_type_display", "Количество"],
        ).properties(height=350)
    st.altair_chart(chart_type, use_container_width=True)

st.markdown("----")
st.markdown(
    f"**Всего фильмов:** {total_movies} | **Всего сериалов:** {total_series_views}"
)

st.header("📖 Последние Просмотры")

if df.empty:
    st.info("Нет недавних просмотров в выбранном диапазоне.")
else:
    recent_views = df.sort_values(by="watch_date", ascending=False)[
        ["title", "content_type_display", "user_rating", "watch_date"]
    ].head(10)
    recent_views["watch_date"] = pd.to_datetime(
        recent_views["watch_date"]
    ).dt.strftime("%Y-%m-%d")
    recent_views.columns = [
        "Название",
        "Тип",
        "Рейтинг",
        "Дата Просмотра",
    ]
    st.dataframe(recent_views, use_container_width=True,height = 300)

st.divider()