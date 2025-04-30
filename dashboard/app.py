
import streamlit as st
import pandas as pd
import psycopg2
import os
from datetime import datetime, timedelta
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(page_title="📻 NDR Playlist Dashboard", layout="wide")

# PostgreSQL-Konfiguration
config = {
    "host": os.getenv("PG_HOST"),
    "port": os.getenv("PG_PORT"),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
    "dbname": os.getenv("PG_DB")
}

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

def plot_heatmap(dataframe, title="📊 Heatmap: Sendezeiten"):
    df_heat = dataframe.copy()
    df_heat["weekday"] = df_heat["played_at"].dt.day_name()
    df_heat["hour"] = df_heat["played_at"].dt.hour
    weekdays_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    df_heat["weekday"] = pd.Categorical(df_heat["weekday"], categories=weekdays_order, ordered=True)
    heat_data = df_heat.groupby(["weekday", "hour"]).size().unstack().fillna(0)
    fig, ax = plt.subplots(figsize=(12, 4))
    sns.heatmap(heat_data, cmap="YlGnBu", ax=ax, linewidths=.5, linecolor="white")
    ax.set_title(title)
    ax.set_xlabel("Stunde")
    ax.set_ylabel("Wochentag")
    st.pyplot(fig)

def plot_treemap(df, label_column, value_column, title):
    if df.empty:
        st.info("Keine Daten verfügbar für Treemap.")
        return
    fig = px.treemap(df, path=[label_column], values=value_column, title=title)
    st.plotly_chart(fig, use_container_width=True)

df = get_data()

if df.empty:
    st.warning("Keine Daten gefunden.")
    st.stop()

df["played_date"] = pd.to_datetime(df["played_date"], errors="coerce")
df["played_at"] = pd.to_datetime(df["played_at"], errors="coerce")
df["month"] = df["played_at"].dt.month
df["weekday"] = df["played_at"].dt.day_name()
df["hour"] = df["played_at"].dt.hour
df["season"] = df["month"].map({
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Frühling", 4: "Frühling", 5: "Frühling",
    6: "Sommer", 7: "Sommer", 8: "Sommer",
    9: "Herbst", 10: "Herbst", 11: "Herbst"
})
df["weektype"] = df["played_at"].dt.weekday.apply(lambda x: "Wochenende" if x >= 5 else "Wochentag")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Übersicht & Filter", "📈 Saisonale Analyse", "🔎 Song-Suche", "👤 Künstler-Suche", "🏆 Top 20 des Jahres"
])

# TAB 1
with tab1:
    st.header("🎶 Übersicht & Filter")
    col1, col2 = st.columns(2)
    with col1:
        station_options = sorted(df["station"].dropna().unique())
        selected_station = st.selectbox("🎙️ Sender", ["Alle"] + station_options)
    with col2:
        min_date = df["played_date"].min().date()
        max_date = df["played_date"].max().date()
        start_date, end_date = st.date_input("📅 Zeitraum", (max_date - timedelta(days=1), max_date),
                                             min_value=min_date, max_value=max_date)
    filtered = df[(df["played_date"].dt.date >= start_date) & (df["played_date"].dt.date <= end_date)]
    if selected_station != "Alle":
        filtered = filtered[filtered["station"] == selected_station]
    st.markdown(f"🎧 **{len(filtered)} Einträge gefunden** für `{selected_station}` von `{start_date}` bis `{end_date}`")
    page_size = 500
    total_pages = max(1, (len(filtered) - 1) // page_size + 1)
    page = st.number_input("📄 Seite auswählen", min_value=1, max_value=total_pages, value=1, step=1)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    st.markdown(f"📄 Zeige Einträge {start_idx + 1} bis {min(end_idx, len(filtered))} von {len(filtered):,}")
    st.dataframe(filtered.iloc[start_idx:end_idx], use_container_width=True)
    st.subheader("📊 Songs nach Uhrzeit")
    chart_df = filtered[filtered["played_time"].notna()].copy()
    chart_df["played_time_clean"] = chart_df["played_time"].astype(str).str.slice(0, 5)
    chart_df = chart_df[chart_df["played_time_clean"].str.match(r"^\d{2}:\d{2}$")]
    if not chart_df.empty:
        df_chart = chart_df.groupby("played_time_clean").size().reset_index(name="Anzahl")
        st.bar_chart(df_chart.set_index("played_time_clean").sort_index())
    else:
        st.info("Keine gültigen Uhrzeiten vorhanden.")
    st.subheader("🎤 Top 10 Künstler")
    st.bar_chart(filtered["artist"].value_counts().head(10))
    st.subheader("🎶 Top 10 Titel")
    st.bar_chart(filtered["title"].value_counts().head(10))
    st.subheader("📡 Verteilung nach Sender")
    st.bar_chart(filtered["station"].value_counts())

# TAB 2
with tab2:
    st.header("📈 Saisonale Auswertung")
    col1, col2 = st.columns(2)
    with col1:
        selected_month = st.selectbox("📆 Monat", range(1, 13))
    with col2:
        selected_season = st.selectbox("🌤️ Jahreszeit", ["Frühling", "Sommer", "Herbst", "Winter"])
    st.subheader("🎶 Top 10 Songs im Monat")
    st.bar_chart(df[df["month"] == selected_month]["title"].value_counts().head(10))
    st.subheader("🎤 Top 10 Künstler in der Jahreszeit")
    st.bar_chart(df[df["season"] == selected_season]["artist"].value_counts().head(10))
    st.subheader("🗓️ Wochentag vs. Wochenende")
    for typ in ["Wochentag", "Wochenende"]:
        part = df[df["weektype"] == typ]
        st.markdown(f"**{typ}**")
        st.bar_chart(part["title"].value_counts().head(5))
    st.subheader("⏰ Tageszeiten-Verlauf")
    st.line_chart(df.groupby("hour").size().reset_index(name="Anzahl").set_index("hour"))
    st.subheader("📊 Heatmap der Sendezeiten (Saisonfilter)")
    plot_heatmap(df[df["season"] == selected_season], title=f"Sendezeiten in {selected_season}")

# TAB 3
with tab3:
    st.header("🔍 Song-Suche")
    col1, col2 = st.columns(2)
    with col1:
        title_options = sorted(df["title"].dropna().unique())
        selected_title = st.selectbox("🎶 Titel", title_options)
    with col2:
        min_date = df["played_date"].min().date()
        max_date = df["played_date"].max().date()
        start, end = st.date_input("📅 Zeitraum wählen", (min_date, max_date), min_value=min_date, max_value=max_date)
    results = df[(df["title"] == selected_title) & (df["played_date"].dt.date >= start) & (df["played_date"].dt.date <= end)]
    st.markdown(f"🔍 **{len(results)} Einsätze** von `{selected_title}` zwischen `{start}` und `{end}`")
    if results.empty:
        st.info("Keine Daten gefunden.")
        st.stop()
    st.subheader("📅 Verlauf pro Tag")
    timeline = results.groupby(results["played_date"].dt.date).size().reset_index(name="Anzahl")
    timeline = timeline.rename(columns={"played_date": "Datum"})
    st.line_chart(timeline.set_index("Datum"))
    st.subheader("⏰ Uhrzeitverlauf")
    st.bar_chart(results["hour"].value_counts().sort_index())
    st.subheader("📡 Sender-Verlauf")
    sender_df = results.groupby(["played_date", "station"]).size().reset_index(name="Anzahl")
    if not sender_df.empty:
        pivot = sender_df.pivot(index="played_date", columns="station", values="Anzahl").fillna(0)
        st.line_chart(pivot)
    else:
        st.info("Keine Senderdaten verfügbar.")
    st.subheader("📊 Heatmap der Sendezeiten dieses Songs")
    plot_heatmap(results, title=f"Sendezeiten für '{selected_title}'")

# TAB 4
with tab4:
    st.header("👤 Künstler-Suche")
    col1, col2 = st.columns(2)
    with col1:
        artist_options = sorted(df["artist"].dropna().unique())
        selected_artist = st.selectbox("🎤 Künstler wählen", artist_options)
    with col2:
        min_date = df["played_date"].min().date()
        max_date = df["played_date"].max().date()
        start, end = st.date_input("📅 Zeitraum", (min_date, max_date), min_value=min_date, max_value=max_date)
    artist_df = df[(df["artist"] == selected_artist) & (df["played_date"].dt.date >= start) & (df["played_date"].dt.date <= end)]
    st.markdown(f"🔍 **{len(artist_df)} Einsätze** von `{selected_artist}` zwischen `{start}` und `{end}`")
    if artist_df.empty:
        st.info("Keine Daten für diesen Künstler im Zeitraum.")
        st.stop()
    st.subheader("📋 Top-Titel – Tabelle")
    song_summary = artist_df.groupby("title").agg(
        Anzahl_Plays=("title", "count"),
        Erstes_Datum=("played_date", "min"),
        Letztes_Datum=("played_date", "max"),
        Meistgenutzter_Sender=("station", lambda x: x.value_counts().idxmax())
    ).sort_values("Anzahl_Plays", ascending=False).reset_index()
    st.dataframe(song_summary, use_container_width=True)
    st.subheader("📊 Top 10 Titel – Diagramm")
    top10 = song_summary.head(10)
    st.bar_chart(top10.set_index("title")["Anzahl_Plays"])
    st.subheader("🧱 Treemap: Anteile der Titel des Künstlers")
    plot_treemap(top10, "title", "Anzahl_Plays", f"Anteile der Top 10 Titel von {selected_artist}")
    st.subheader("📊 Heatmap der Sendezeiten des Künstlers")
    plot_heatmap(artist_df, title=f"Sendezeiten für Künstler '{selected_artist}'")

# TAB 5
with tab5:
    st.header("🏆 Top 20 des Jahres")
    available_years = sorted(df["played_at"].dt.year.dropna().unique(), reverse=True)
    selected_year = st.selectbox("📅 Jahr auswählen", available_years)
    year_df = df[df["played_at"].dt.year == selected_year]
    if year_df.empty:
        st.warning(f"Keine Daten für das Jahr {selected_year} gefunden.")
        st.stop()
    st.subheader("🎤 Top 20 Künstler")
    top_artists = year_df["artist"].value_counts().sort_values(ascending=False).head(20).reset_index()
    top_artists.columns = ["Künstler", "Anzahl"]
    st.bar_chart(top_artists.set_index("Künstler"))
    st.subheader("🎶 Top 20 Titel")
    top_titles = year_df["title"].value_counts().sort_values(ascending=False).head(20).reset_index()
    top_titles.columns = ["Titel", "Anzahl"]
    st.bar_chart(top_titles.set_index("Titel"))
