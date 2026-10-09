import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

DB_PATH = "/lake/warehouse/air_quality.duckdb"
WHO_PM25 = 15

st.set_page_config(page_title="Mediterranean Air Quality", layout="wide")


@st.cache_data(ttl=600)
def load_daily() -> pd.DataFrame:
    con = duckdb.connect(DB_PATH, read_only=True)
    try:
        df = con.execute("select * from main.mart_air_quality_daily").df()
    finally:
        con.close()
    df["day"] = pd.to_datetime(df["day"])
    df["exceeds_who_pm25_modeled"] = df["exceeds_who_pm25_modeled"].fillna(False).astype(bool)
    return df


df = load_daily()
cities = sorted(df["city"].unique())

st.title("Qualité de l'air en Méditerranée")
st.caption(
    "Pollution modélisée (Open-Meteo / CAMS), météo (Open-Meteo) et mesures réelles "
    "des stations (OpenAQ). Tunis et Rome n'ont pas de mesures réelles exploitables."
)

# --- Filtres ---
st.sidebar.header("Filtres")
sel = st.sidebar.multiselect("Villes", cities, default=cities)
dmin, dmax = df["day"].min().date(), df["day"].max().date()
period = st.sidebar.date_input("Période", (dmin, dmax), min_value=dmin, max_value=dmax)
if len(period) != 2:
    st.info("Choisis une date de début et une date de fin.")
    st.stop()

f = df[
    df["city"].isin(sel)
    & (df["day"] >= pd.Timestamp(period[0]))
    & (df["day"] <= pd.Timestamp(period[1]))
]
if f.empty:
    st.warning("Aucune donnée pour ces filtres.")
    st.stop()
f = f.sort_values(["city", "day"])

# --- 1. Évolution de la pollution ---
st.subheader("1. Évolution quotidienne des PM2.5")
fig = px.line(
    f, x="day", y="pm25_modeled_avg", color="city",
    labels={"day": "Jour", "pm25_modeled_avg": "PM2.5 moyen (µg/m³)", "city": "Ville"},
)
fig.add_hline(y=WHO_PM25, line_dash="dash", annotation_text="Seuil OMS 24 h : 15 µg/m³")
st.plotly_chart(fig, use_container_width=True)

# --- 2. Dépassements du seuil OMS ---
st.subheader("2. Part des jours au-dessus du seuil OMS (PM2.5, données modélisées)")
exc = (
    f.groupby("city")
    .agg(jours=("day", "count"), jours_depassement=("exceeds_who_pm25_modeled", "sum"))
    .reset_index()
)
exc["pourcentage"] = (100 * exc["jours_depassement"] / exc["jours"]).round(1)
fig = px.bar(
    exc.sort_values("pourcentage", ascending=False),
    x="city", y="pourcentage", text="pourcentage",
    labels={"city": "Ville", "pourcentage": "% de jours au-dessus du seuil"},
)
st.plotly_chart(fig, use_container_width=True)

# --- 3. Vent et pollution ---
st.subheader("3. Vent et pollution")
fig = px.scatter(
    f, x="wind_speed_avg_kmh", y="pm25_modeled_avg", color="city", opacity=0.5,
    labels={
        "wind_speed_avg_kmh": "Vitesse moyenne du vent (km/h)",
        "pm25_modeled_avg": "PM2.5 moyen (µg/m³)",
        "city": "Ville",
    },
)
st.plotly_chart(fig, use_container_width=True)
corr_wind = (
    f.groupby("city")[["wind_speed_avg_kmh", "pm25_modeled_avg"]]
    .apply(lambda g: g["wind_speed_avg_kmh"].corr(g["pm25_modeled_avg"]))
    .round(2)
    .rename("Corrélation vent / PM2.5")
    .reset_index()
)
st.dataframe(corr_wind, hide_index=True)
st.caption("Une corrélation négative indique que plus le vent est fort, plus la pollution baisse.")

# --- 4. Mesures réelles contre modèle ---
st.subheader("4. Mesures réelles (OpenAQ) contre modèle (Open-Meteo)")
comp = f.dropna(subset=["pm25_measured_avg", "pm25_modeled_avg"])
if comp.empty:
    st.info("Aucune ville sélectionnée n'a de mesures réelles sur cette période.")
else:
    fig = px.scatter(
        comp, x="pm25_measured_avg", y="pm25_modeled_avg", color="city", opacity=0.5,
        labels={
            "pm25_measured_avg": "PM2.5 mesuré (µg/m³)",
            "pm25_modeled_avg": "PM2.5 modélisé (µg/m³)",
            "city": "Ville",
        },
    )
    top = float(max(comp["pm25_measured_avg"].max(), comp["pm25_modeled_avg"].max()))
    fig.add_shape(type="line", x0=0, y0=0, x1=top, y1=top, line=dict(dash="dash"))
    st.plotly_chart(fig, use_container_width=True)

    stats = (
        comp.groupby("city")
        .apply(lambda g: pd.Series({
            "Jours comparés": len(g),
            "Corrélation": round(g["pm25_measured_avg"].corr(g["pm25_modeled_avg"]), 2),
            "Écart moyen modèle - mesure (µg/m³)": round(
                (g["pm25_modeled_avg"] - g["pm25_measured_avg"]).mean(), 1
            ),
        }))
        .reset_index()
    )
    st.dataframe(stats, hide_index=True)
    st.caption(
        "La ligne pointillée représente un accord parfait. Seuls les jours avec au moins "
        "18 heures de mesures sont comparés."
    )