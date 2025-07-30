# Chix & Mati Expense Tracker - Enhanced with Currency Conversion, Highlighting, Deletion, Undo, Bulk Delete

import pandas as pd
from datetime import datetime
import streamlit as st
import altair as alt

# Currency conversion rates (example, can be updated)
CURRENCY_RATES = {
    "SEK": 1.0,
    "ZAR (Rand)": 1.8,
    "EUR": 0.088
}

# Load or initialize data
@st.cache_data
def load_data():
    expenses = [
        ["Mattress", 0, 0, 0, "very high", "2025-07-25", False],
        ["Washing Machine", 5743, 5743, 0, "very high", "2025-07-25", False],
        ["Humidifier", 4500, 2250, 2250, "very high", "2025-08-25", False],
        ["Couch", 0, 0, 0, "very high", "2025-07-25", False],
        ["bedroom lights", 200, 100, 100, "medium", "2025-08-25", False]
    ]
    df = pd.DataFrame(expenses, columns=[
        "Category", "Total", "Chix", "Matilda", "Priority", "Budget Date", "Recurring"
    ])
    df["Budget Date"] = pd.to_datetime(df["Budget Date"])
    df["Month"] = df["Budget Date"].dt.strftime("%B")
    return df

# Load data
if "df" not in st.session_state:
    st.session_state.df = load_data()

if "last_deleted" not in st.session_state:
    st.session_state.last_deleted = None

# Web UI
st.title("Chix & Mati Expense Tracker")

# Currency selection
currency = st.selectbox("Select Currency", list(CURRENCY_RATES.keys()), index=0)
rate = CURRENCY_RATES[currency]

# Add new expense
with st.form("Add Expense"):
    st.subheader("Add a New Expense")
    category = st.text_input("Category")
    total = st.number_input(f"Total ({currency})", min_value=0.0, step=1.0)
    split_type = st.selectbox("Split Type", ["Equal", "By Amount", "By Percentage"])

    if split_type == "Equal":
        chix = matilda = total / 2
    elif split_type == "By Percentage":
        chix_pct = st.slider("Chix's %", 0, 100, 50)
        chix = total * chix_pct / 100
        matilda = total - chix
    else:
        chix = st.number_input("Chix's Share", min_value=0.0, step=1.0)
        matilda = total - chix

    priority = st.selectbox("Priority", ["very high", "high", "medium", "low"])
    default_date = datetime.today() if priority != "very high" else datetime.today().replace(day=1)
    budget_date = st.date_input("Budget Date", default_date)
    recurring = st.checkbox("Recurring Expense")
    submitted = st.form_submit_button("Add Expense")

    if submitted:
        new_row = pd.DataFrame([[category, total, chix, matilda, priority, pd.to_datetime(budget_date), recurring, pd.to_datetime(budget_date).strftime("%B")]],
                               columns=list(st.session_state.df.columns))
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
        st.success("Expense added!")

# Filters
st.sidebar.header("Filters")
months = st.sidebar.multiselect("Select Month(s)", options=st.session_state.df["Month"].unique(), default=st.session_state.df["Month"].unique())
priorities = st.sidebar.multiselect("Select Priority", options=st.session_state.df["Priority"].unique(), default=st.session_state.df["Priority"].unique())
only_recurring = st.sidebar.checkbox("Show only recurring expenses")

filtered_df = st.session_state.df[st.session_state.df["Month"].isin(months) & st.session_state.df["Priority"].isin(priorities)]
if only_recurring:
    filtered_df = filtered_df[filtered_df["Recurring"] == True]

# Deletion UI
st.subheader("Manage Expenses")
with st.expander("Delete Expenses"):
    indices_to_delete = st.multiselect(
        "Select expenses to delete", options=st.session_state.df.index,
        format_func=lambda i: f"{st.session_state.df.at[i, 'Category']} ({st.session_state.df.at[i, 'Budget Date'].strftime('%Y-%m-%d')})"
    )
    if st.button("Confirm Deletion"):
        st.session_state.last_deleted = st.session_state.df.loc[indices_to_delete].copy()
        st.session_state.df.drop(index=indices_to_delete, inplace=True)
        st.session_state.df.reset_index(drop=True, inplace=True)
        st.success("Selected expenses deleted.")
        st.experimental_rerun()
    if st.session_state.last_deleted is not None:
        if st.button("Undo Last Deletion"):
            st.session_state.df = pd.concat([st.session_state.df, st.session_state.last_deleted], ignore_index=True)
            st.session_state.last_deleted = None
            st.success("Last deleted expenses restored.")
            st.experimental_rerun()

# Convert currency
filtered_df_converted = filtered_df.copy()
filtered_df_converted[["Total", "Chix", "Matilda"]] = filtered_df_converted[["Total", "Chix", "Matilda"]] * rate

# Highlight high expenses
def highlight_high(val):
    return 'background-color: #ffcccc' if val > 3000 * rate else ''

# Show data
st.subheader("Filtered Expenses")
st.dataframe(filtered_df_converted.style.applymap(highlight_high, subset=["Total"]))

# Export
st.download_button(
    label="Download Filtered Data as CSV",
    data=filtered_df_converted.to_csv(index=False).encode("utf-8"),
    file_name="chix_mati_expenses_filtered.csv",
    mime="text/csv"
)

# Summary
st.subheader("Summary")
total_by_person = filtered_df_converted[["Chix", "Matilda"]].sum()
total_by_category = filtered_df_converted.groupby("Priority")["Total"].sum()
net_balance = total_by_person["Chix"] - total_by_person["Matilda"]

st.write("### Total Spending by Person")
st.write(total_by_person)

st.write("### Total Spending by Priority Category")
st.write(total_by_category)

st.write("### Net Balance")
st.write(f"Chix - Matilda = {net_balance:.2f} {currency}")

# Visualization: Monthly Spending by Person
st.subheader("Monthly Spending by Person")
monthly = filtered_df_converted.groupby(["Month"])[["Chix", "Matilda"]].sum().reset_index()
monthly_melted = monthly.melt(id_vars="Month", var_name="Person", value_name="Amount")
chart = alt.Chart(monthly_melted).mark_bar().encode(
    x="Month:N",
    y="Amount:Q",
    color="Person:N",
    tooltip=["Month", "Person", "Amount"]
).properties(height=400)

st.altair_chart(chart, use_container_width=True)
