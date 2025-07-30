# app.py

import pandas as pd
from datetime import datetime
import streamlit as st

@st.cache_data
def load_data():
    expenses = [
        ["Mattress", 0, 0, 0, "very high", "2025-07-25"],
        ["Washing Machine", 5743, 5743, 0, "very high", "2025-07-25"],
        ["Humidifier", 4500, 2250, 2250, "very high", "2025-08-25"],
        ["Couch", 0, 0, 0, "very high", "2025-07-25"],
        ["bedroom lights", 200, 100, 100, "medium", "2025-08-25"],
        ["laundry basket", 100, 50, 50, "medium", "2025-08-25"],
        ["Le Creuset stew pot", 3000, 1500, 1500, "medium", "2025-11-25"],
        ["Juicer", 500, 250, 250, "low", "2025-10-25"],
        ["Pillows", 2000, 1000, 1000, "low", "2025-02-25"],
        ["Duvet Inner", 2900, 1450, 1450, "high", "2025-08-25"],
        ["Bed cover", 1563, 781.5, 781.5, "high", "2025-07-25"],
        ["First Rent Invoice (8 days)", 6200, 3100, 3100, "high", "2025-08-25"],
        ["Petrol for moving", 2000, 1500, 500, "high", "2025-08-25"],
        ["Move out cleaning (both)", 1700, 850, 850, "high", "2025-07-25"],
        ["Hooks for art", 200, 100, 100, "high", "2025-07-25"],
        ["Knives", 3000, 3000, 0, "high", "2025-07-25"],
        ["Frying pan", 1300, 650, 650, "high", "2025-07-25"],
        ["Toolbox", 0, 0, 0, "high", "2025-07-25"],
        ["Bedside tables", 0, 0, 0, "high", "2025-08-25"],
        ["Kitchen rug", 559, 279.5, 279.5, "high", "2025-07-25"],
        ["Living room rug", 5000, 0, 0, "high", "2025-02-25"]
    ]
    df = pd.DataFrame(expenses, columns=[
        "Category", "Total (SEK)", "Chicco (SEK)", "Matilda (SEK)", "Priority", "Budget Date"
    ])
    df["Budget Date"] = pd.to_datetime(df["Budget Date"])
    return df

if "df" not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

st.title("Chicco & Mati Expense Tracker")

with st.form("Add Expense"):
    st.subheader("Add a New Expense")
    category = st.text_input("Category")
    total = st.number_input("Total (SEK)", min_value=0.0, step=1.0)
    chicco = st.number_input("Chicco's Share (SEK)", min_value=0.0, step=1.0)
    matilda = st.number_input("Matilda's Share (SEK)", min_value=0.0, step=1.0)
    priority = st.selectbox("Priority", ["very high", "high", "medium", "low"])
    budget_date = st.date_input("Budget Date", datetime.today())
    submitted = st.form_submit_button("Add Expense")

    if submitted:
        new_row = pd.DataFrame([[category, total, chicco, matilda, priority, pd.to_datetime(budget_date)]],
                               columns=df.columns)
        st.session_state.df = pd.concat([df, new_row], ignore_index=True)
        st.success("Expense added!")

st.subheader("All Expenses")
st.dataframe(st.session_state.df)

st.subheader("Summary")
total_by_person = st.session_state.df[["Chicco (SEK)", "Matilda (SEK)"]].sum()
total_by_category = st.session_state.df.groupby("Priority")["Total (SEK)"].sum()
net_balance = total_by_person["Chicco (SEK)"] - total_by_person["Matilda (SEK)"]

st.write("### Total Spending by Person")
st.write(total_by_person)

st.write("### Total Spending by Priority Category")
st.write(total_by_category)

st.write("### Net Balance")
st.write(f"Chicco - Matilda = {net_balance} SEK")
