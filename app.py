# Expense Tracker - Web Interface Version with Filters, Charts, CSV Export & Recurring Expenses

import pandas as pd
from datetime import datetime
import streamlit as st
import altair as alt

# Load or initialize data
@st.cache_data
def load_data():
    expenses = [
        ["Mattress", 0, 0, 0, "very high", "2025-07-25", False],
        ["Washing Machine", 5743, 5743, 0, "very high", "2025-07-25", False],
        ["Humidifier", 4500, 2250, 2250, "very high", "2025-08-25", False],
        ["Couch", 0, 0, 0, "very high", "2025-07-25", False],
        ["bedroom lights", 200, 100, 100, "medium", "2025-08-25", False],
        ["laundry basket", 100, 50, 50, "medium", "2025-08-25", False],
        ["Le Creuset stew pot", 3000, 1500, 1500, "medium", "2025-11-25", False],
        ["Juicer", 500, 250, 250, "low", "2025-10-25", False],
        ["Pillows", 2000, 1000, 1000, "low", "2025-02-25", False],
        ["Duvet Inner", 2900, 1450, 1450, "high", "2025-08-25", False],
        ["Bed cover", 1563, 781.5, 781.5, "high", "2025-07-25", False],
        ["First Rent Invoice (8 days)", 6200, 3100, 3100, "high", "2025-08-25", False],
        ["Petrol for moving", 2000, 1500, 500, "high", "2025-08-25", False],
        ["Move out cleaning (both)", 1700, 850, 850, "high", "2025-07-25", False],
        ["Hooks for art", 200, 100, 100, "high", "2025-07-25", False],
        ["Knives", 3000, 3000, 0, "high", "2025-07-25", False],
        ["Frying pan", 1300, 650, 650, "high", "2025-07-25", False],
        ["Toolbox", 0, 0, 0, "high", "2025-07-25", False],
        ["Bedside tables", 0, 0, 0, "high", "2025-08-25", False],
        ["Kitchen rug", 559, 279.5, 279.5, "high", "2025-07-25", False],
        ["Living room rug", 5000, 0, 0, "high", "2025-02-25", False]
    ]
    df = pd.DataFrame(expenses, columns=[
        "Category", "Total (SEK)", "Chix (SEK)", "Matilda (SEK)", "Priority", "Budget Date", "Recurring"
    ])
    df["Budget Date"] = pd.to_datetime(df["Budget Date"])
    df["Month"] = df["Budget Date"].dt.to_period("M").astype(str)
    return df

# Load data
if "df" not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

# Web UI
st.title("Chix & Mati Expense Tracker")

# Add new expense
with st.form("Add Expense"):
    st.subheader("Add a New Expense")
    category = st.text_input("Category")
    total = st.number_input("Total (SEK)", min_value=0.0, step=1.0)
    chix = st.number_input("Chix's Share (SEK)", min_value=0.0, step=1.0)
    matilda = st.number_input("Matilda's Share (SEK)", min_value=0.0, step=1.0)
    priority = st.selectbox("Priority", ["very high", "high", "medium", "low"])
    budget_date = st.date_input("Budget Date", datetime.today())
    recurring = st.checkbox("Recurring Expense")
    submitted = st.form_submit_button("Add Expense")

    if submitted:
        new_row = pd.DataFrame([[category, total, chix, matilda, priority, pd.to_datetime(budget_date), recurring, pd.to_datetime(budget_date).strftime("%Y-%m")]],
                               columns=list(df.columns))
        st.session_state.df = pd.concat([df, new_row], ignore_index=True)
        st.success("Expense added!")

# Filters
st.sidebar.header("Filters")
months = st.sidebar.multiselect("Select Month(s)", options=df["Month"].unique(), default=df["Month"].unique())
priorities = st.sidebar.multiselect("Select Priority", options=df["Priority"].unique(), default=df["Priority"].unique())
categories = st.sidebar.multiselect("Select Category", options=df["Category"].unique(), default=df["Category"].unique())

filtered_df = df[df["Month"].isin(months) & df["Priority"].isin(priorities) & df["Category"].isin(categories)]

# Show data
st.subheader("Filtered Expenses")
st.dataframe(filtered_df)

# Export
st.download_button(
    label="Download Filtered Data as CSV",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="chix_mati_expenses_filtered.csv",
    mime="text/csv"
)

# Summary
st.subheader("Summary")
total_by_person = filtered_df[["Chix (SEK)", "Matilda (SEK)"]].sum()
total_by_category = filtered_df.groupby("Priority")["Total (SEK)"].sum()
net_balance = total_by_person["Chix (SEK)"] - total_by_person["Matilda (SEK)"]

st.write("### Total Spending by Person")
st.write(total_by_person)

st.write("### Total Spending by Priority Category")
st.write(total_by_category)

st.write("### Net Balance")
st.write(f"Chix - Matilda = {net_balance} SEK")

# Visualization: Monthly Spending by Person
st.subheader("Monthly Spending by Person")
monthly = filtered_df.groupby(["Month"])[["Chix (SEK)", "Matilda (SEK)"]].sum().reset_index()
monthly_melted = monthly.melt(id_vars="Month", var_name="Person", value_name="Amount")
chart = alt.Chart(monthly_melted).mark_bar().encode(
    x="Month:N",
    y="Amount:Q",
    color="Person:N",
    tooltip=["Month", "Person", "Amount"]
).properties(height=400)

st.altair_chart(chart, use_container_width=True)
