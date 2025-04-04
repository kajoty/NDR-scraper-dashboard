import streamlit as st
import pandas as pd
import psycopg2
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="📻 NDR Playlist Dashboard", layout="wide")

# PostgreSQL-Konfiguration aus Umgebungsvariablen
config = {
    "host": os.getenv("PG_HOST"),
    "port": os.getenv("PG_PORT"),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
    "dbname": os.getenv("PG_DB")
}

# Daten laden
@st.cache_data(ttl=300)
def get_data():
    try:
        conn = psycopg2.connect(**config)
        query = """
            SELECT station, artist, title, played_date, played_time, played_at
            FROM ndr_playlist
            ORDER BY played_at DESC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Fehler beim Laden der Daten: {e}")
        return pd.DataFrame()

df = get_data()

if df.empty:
    st.warning("Keine Daten gefunden.")
    st.stop()

# Vorbereitung: Zeitfelder
df["played_date"] = pd.to_datetime(df["played_date"], errors="coerce")
df["played_at"] = pd.to_datetime(df["played_at"], errors="coerce")
df["month"] = df["played_at"].dt.month
df["weekday"] = df["played_at"].dt.day_name()
df["hour"] = df["played_at"].dt.hour

# Jahreszeit berechnen
def get_season(month):
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Frühling"
    elif month in [6, 7, 8]:
        return "Sommer"
    else:
        return "Herbst"

df["season"] = df["month"].apply(get_season)

# Wochentag/Wochenende
df["weektype"] = df["played_at"].dt.weekday.apply(lambda x: "Wochenende" if x >= 5 else "Wochentag")

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 Übersicht & Filter", "📈 Saisonale Analyse", "🔎 Song-Suche"])

# ========== TAB 1 ========== #
with tab1:
    st.title("🎶 NDR Playlist – Übersicht & Filter")

    st.sidebar.header("🔎 Filter")

    # Sender
    station_options = sorted(df["station"].dropna().unique())
    selected_station = st.sidebar.selectbox("🎙️ Sender", ["Alle"] + station_options)

    # Datumsbereich
    min_date = df["played_date"].min().date()
    max_date = df["played_date"].max().date()

    start_date, end_date = st.sidebar.date_input(
        "📅 Zeitraum", value=(max_date - timedelta(days=1), max_date),
        min_value=min_date, max_value=max_date
    )

    filtered = df[
        (df["played_date"].dt.date >= start_date) &
        (df["played_date"].dt.date <= end_date)
    ]

    if selected_station != "Alle":
        filtered = filtered[filtered["station"] == selected_station]

    st.write(f"🎧 {len(filtered)} Einträge gefunden für `{selected_station}` von `{start_date}` bis `{end_date}`")

    st.dataframe(filtered, use_container_width=True)

    st.subheader("📊 Songs nach Uhrzeit")

    chart_df = filtered[filtered["played_time"].notna()].copy()
    chart_df["played_time"] = chart_df["played_time"].astype(str)
    chart_df["played_time_clean"] = chart_df["played_time"].str.slice(0, 5)
    chart_df = chart_df[chart_df["played_time_clean"].str.match(r"^\d{2}:\d{2}$")]

    if not chart_df.empty:
        df_chart = (
            chart_df.groupby("played_time_clean")
            .size()
            .reset_index(name="Anzahl")
            .sort_values("played_time_clean")
        )
        st.bar_chart(df_chart.set_index("played_time_clean"))
    else:
        st.info("Keine gültigen Uhrzeiten vorhanden.")

    st.subheader("🎤 Top 10 Künstler")
    st.bar_chart(filtered["artist"].dropna().value_counts().head(10))

    st.subheader("🎶 Top 10 Titel")
    st.bar_chart(filtered["title"].dropna().value_counts().head(10))

    st.subheader("📡 Verteilung nach Sender")
    st.bar_chart(filtered["station"].value_counts())

# ========== TAB 2 ========== #
with tab2:
    st.title("📈 Saisonale Auswertung")

    col1, col2 = st.columns(2)

    with col1:
        selected_month = st.selectbox("📆 Monat wählen", range(1, 13))
    with col2:
        selected_season = st.selectbox("🌤️ Jahreszeit wählen", ["Frühling", "Sommer", "Herbst", "Winter"])

    st.subheader("📅 Top 10 Songs im Monat")
    monthly = df[df["month"] == selected_month]
    st.bar_chart(monthly["title"].value_counts().head(10))

    st.subheader("🌞 Top 10 Künstler in der Jahreszeit")
    seasonal = df[df["season"] == selected_season]
    st.bar_chart(seasonal["artist"].value_counts().head(10))

    st.subheader("🗓️ Wochentag vs. Wochenende – Top Titel")
    for typ in ["Wochentag", "Wochenende"]:
        st.markdown(f"**{typ}**")
        part = df[df["weektype"] == typ]
        st.bar_chart(part["title"].value_counts().head(5))

    st.subheader("⏰ Tageszeit-Analyse")
    hourly = df.groupby("hour").size().reset_index(name="Anzahl")
    st.line_chart(hourly.set_index("hour"))

# ========== TAB 3 ========== #
with tab3:
    st.title("🔎 Song-Suche")

    st.sidebar.header("🎵 Song auswählen")
    unique_titles = df["title"].dropna().unique()
    selected_title = st.sidebar.selectbox("🎶 Titel wählen", sorted(unique_titles))

    start_date, end_date = st.sidebar.date_input(
        "📅 Zeitraum", value=(df["played_date"].min().date(), df["played_date"].max().date())
    )

    filtered_song = df[
        (df["title"] == selected_title) &
        (df["played_date"].dt.date >= start_date) &
        (df["played_date"].dt.date <= end_date)
    ]

    st.write(f"🔍 {len(filtered_song)} Einsätze von **{selected_title}** zwischen {start_date} und {end_date}")

    if filtered_song.empty:
        st.info("Keine Einsätze für diesen Titel im gewählten Zeitraum gefunden.")
        st.stop()

    # 📅 Verlauf pro Tag
    st.subheader("📅 Einsätze pro Tag")
    timeline = (
        filtered_song.groupby(filtered_song["played_date"].dt.date)
        .size()
        .reset_index(name="Anzahl")
        .rename(columns={"played_date": "Datum"})
    )
    st.line_chart(timeline.set_index("Datum"))

    # ⏰ Uhrzeitenverlauf
    st.subheader("⏰ Verteilung nach Uhrzeit")
    if "hour" not in filtered_song.columns:
        filtered_song["hour"] = filtered_song["played_at"].dt.hour
    hour_data = (
        filtered_song.groupby("hour").size().reset_index(name="Anzahl")
    )
    st.bar_chart(hour_data.set_index("hour"))

    # 📡 Sender-Verlauf
    st.subheader("📡 Sender-Analyse")
    sender_timeline = (
        filtered_song.groupby(["played_date", "station"])
        .size()
        .reset_index(name="Anzahl")
    )
    if not sender_timeline.empty:
        pivot = sender_timeline.pivot(index="played_date", columns="station", values="Anzahl").fillna(0)
        st.line_chart(pivot)
    else:
        st.info("Keine Senderdaten verfügbar für diesen Titel.")
