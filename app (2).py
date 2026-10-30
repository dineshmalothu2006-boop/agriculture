
import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# Page settings
st.set_page_config(
    page_title="AgriSense",
    page_icon="🌱",
    layout="wide"
)

# Database connection
conn = sqlite3.connect("agrisense.db", check_same_thread=False)

conn.execute("""
CREATE TABLE IF NOT EXISTS farm_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crop TEXT,
    soil TEXT,
    temperature REAL,
    rainfall REAL,
    moisture REAL,
    advice TEXT,
    created_on TEXT
)
""")
conn.commit()

# Website design
st.markdown("""
<style>
.stApp {
    background-color: #f4f8f1;
}
.hero {
    background: linear-gradient(120deg, #14532d, #22a447);
    padding: 25px;
    border-radius: 15px;
    color: white;
}
.hero h1 {
    color: white;
}
.stButton button {
    background-color: #15803d;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>🌱 AgriSense</h1>
    <h3>Farming Advisory Simulator</h3>
    <p>Explore farm conditions and get simple farming suggestions.</p>
</div>
""", unsafe_allow_html=True)

st.write("")

dashboard, simulator, history = st.tabs([
    "📊 Dashboard",
    "🌾 Farming Simulator",
    "📚 Saved Reports"
])

# Farming simulator
with simulator:
    st.header("Enter Your Farm Details")

    with st.form("farm_form"):
        crop = st.selectbox(
            "Select Crop",
            ["Rice", "Cotton", "Maize", "Chilli",
             "Groundnut", "Wheat", "Tomato"]
        )

        soil = st.selectbox(
            "Select Soil Type",
            ["Red Soil", "Black Soil", "Sandy Soil",
             "Clay Soil", "Loamy Soil"]
        )

        col1, col2 = st.columns(2)

        with col1:
            temperature = st.slider(
                "Temperature (°C)", 0, 50, 30
            )
            rainfall = st.slider(
                "Recent Rainfall (mm)", 0, 200, 20
            )

        with col2:
            moisture = st.slider(
                "Soil Moisture (%)", 0, 100, 45
            )

        generate = st.form_submit_button(
            "Generate Farming Advice"
        )

    if generate:
        advice = []

        if temperature >= 38:
            advice.append(
                "High temperature detected. Monitor crops for heat stress."
            )
        elif temperature <= 12:
            advice.append(
                "Low temperature detected. Monitor crops for cold stress."
            )
        else:
            advice.append(
                "Temperature is within the simulator's general range."
            )

        if rainfall < 10 and moisture < 30:
            advice.append(
                "Low rainfall and moisture. Check whether irrigation is needed."
            )
        elif rainfall >= 60:
            advice.append(
                "High rainfall. Check drainage and possible waterlogging."
            )
        elif moisture >= 70:
            advice.append(
                "Soil moisture is high. Avoid unnecessary irrigation."
            )
        else:
            advice.append(
                "Continue monitoring soil moisture and rainfall."
            )

        advice.append(
            f"Selected crop: {crop}. Selected soil: {soil}."
        )

        st.session_state["advice"] = advice
        st.session_state["farm_data"] = (
            crop, soil, temperature, rainfall, moisture
        )

    if "advice" in st.session_state:
        st.subheader("Your Farming Advisory")

        for item in st.session_state["advice"]:
            st.info(item)

        if st.button("Save Simulation Report"):
            crop, soil, temp, rain, moist = (
                st.session_state["farm_data"]
            )

            conn.execute("""
                INSERT INTO farm_records
                (crop, soil, temperature, rainfall,
                 moisture, advice, created_on)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                crop, soil, temp, rain, moist,
                "\n".join(st.session_state["advice"]),
                date.today().isoformat()
            ))

            conn.commit()
            st.success("Report saved successfully!")

# Dashboard
with dashboard:
    st.header("Farm Dashboard")

    records = pd.read_sql_query(
        "SELECT * FROM farm_records", conn
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Saved Reports", len(records))

    crops = (
        records["crop"].nunique()
        if not records.empty else 0
    )
    col2.metric("Crops Simulated", crops)

    avg_moisture = (
        records["moisture"].mean()
        if not records.empty else 0
    )
    col3.metric(
        "Average Soil Moisture",
        f"{avg_moisture:.1f}%"
    )

    if not records.empty:
        st.subheader("Soil Moisture Records")
        st.bar_chart(
            records.set_index("crop")["moisture"]
        )
    else:
        st.info(
            "Run a farming simulation and save the report "
            "to see dashboard statistics."
        )

# Saved reports
with history:
    st.header("Saved Farming Reports")

    records = pd.read_sql_query("""
        SELECT created_on, crop, soil, temperature,
               rainfall, moisture, advice
        FROM farm_records
        ORDER BY id DESC
    """, conn)

    if records.empty:
        st.info("No reports saved yet.")
    else:
        st.dataframe(
            records,
            use_container_width=True,
            hide_index=True
        )

        csv = records.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Reports as CSV",
            data=csv,
            file_name="agrisense_reports.csv",
            mime="text/csv"
        )

st.divider()
st.caption(
    "AgriSense | Built using Python, Streamlit, SQLite and Pandas. "
    "This is an educational simulator, not professional farming advice."
)
