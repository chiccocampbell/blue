# Chix & Mati Expense Tracker - Full Features

import pandas as pd
from datetime import datetime
import streamlit as st
import altair as alt

CURRENCY_RATES = {
    "SEK": 1.0,
    "ZAR (Rand)": 1.8,
    "EUR": 0.088
}

@st.cache_data
def load_data():
    expenses = [
        ["Mattress", "Furniture", 0, 0, 0, "very high", "2025-07-25", False],
        ["Washing Machine", "Furniture", 5743, 5743, 0, "very high", "2025-07-25", False],
        ["Humidifier", "Furniture", 4500, 2250, 2250, "very high", "2025-08-25", False]
    ]
    df = pd.DataFrame(expenses, columns=[
        "Item", "Category", "Total", "Chix", "Matilda", "Priority", "Budget Date", "Recurring"
    ])
    df["Budget Date"] = pd.to_datetime(df["Budget Date"])
    df["Month"] = df["Budget Date"].dt.strftime("%B")
    df["Deleted"] = False
    return df

if "df" not in st.session_state:
    st.session_state.df = load_data()
if "last_state" not in st.session_state:
    st.session_state.last_state = None

st.title("Chix & Mati Expense Tracker")

currency = st.selectbox("Select Currency", list(CURRENCY_RATES.keys()), index=0)
rate = CURRENCY_RATES[currency]

with st.form("Add Expense"):
    st.subheader("Add a New Expense")
    item = st.text_input("Item")
    category = st.selectbox("Category", ["Furniture", "Groceries", "Rent", "Entertainment", "Savings", "Other"])
    total = st.number_input(f"Total ({currency})", min_value=0.0, step=1.0)
    split_type = st.selectbox("Split Type", ["Equal", "By Amount", "By Percentage"])

    chix = matilda = 0
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
        new_row = pd.DataFrame([[item, category, total, chix, matilda, priority, pd.to_datetime(budget_date), recurring, pd.to_datetime(budget_date).strftime("%B"), False]],
                               columns=list(st.session_state.df.columns))
        st.session_state.last_state = st.session_state.df.copy()
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
        st.success("Expense added!")

# Filters
st.sidebar.header("Filters")
months = st.sidebar.multiselect("Select Month(s)", options=st.session_state.df["Month"].unique(), default=st.session_state.df["Month"].unique())
priorities = st.sidebar.multiselect("Select Priority", options=st.session_state.df["Priority"].unique(), default=st.session_state.df["Priority"].unique())
only_recurring = st.sidebar.checkbox("Show only recurring expenses")
show_deleted = st.sidebar.checkbox("Show archived (deleted) expenses")

filtered_df = st.session_state.df.copy()
filtered_df = filtered_df[filtered_df["Month"].isin(months) & filtered_df["Priority"].isin(priorities)]
if only_recurring:
    filtered_df = filtered_df[filtered_df["Recurring"] == True]
if not show_deleted:
    filtered_df = filtered_df[filtered_df["Deleted"] == False]

# Deletion UI
st.subheader("Manage Expenses")
with st.expander("Archive/Delete Expenses"):
    indices_to_delete = st.multiselect(
        "Select expenses to archive", options=filtered_df.index,
        format_func=lambda i: f"{filtered_df.at[i, 'Item']} ({filtered_df.at[i, 'Budget Date'].strftime('%Y-%m-%d')})"
    )
    if st.button("Confirm Archive"):
        st.session_state.last_state = st.session_state.df.copy()
        st.session_state.df.loc[indices_to_delete, "Deleted"] = True
        st.success("Selected expenses archived.")
        st.experimental_rerun()
    if st.session_state.last_state is not None:
        if st.button("Undo Last Action"):
            st.session_state.df = st.session_state.last_state.copy()
            st.session_state.last_state = None
            st.success("Previous changes undone.")
            st.experimental_rerun()

# Currency conversion
converted = filtered_df.copy()
converted[["Total", "Chix", "Matilda"]] *= rate

# Highlighting
def highlight_high(val):
    return 'background-color: #ff9933' if val > 3000 * rate else ''

st.subheader("Filtered Expenses")
st.dataframe(converted.style.applymap(highlight_high, subset=["Total"]))

st.download_button(
    label="Download Filtered Data as CSV",
    data=converted.to_csv(index=False).encode("utf-8"),
    file_name="chix_mati_expenses_filtered.csv",
    mime="text/csv"
)

# Summary
st.subheader("Summary")
total_by_person = converted[["Chix", "Matilda"]].sum()
total_by_category = converted.groupby("Priority")["Total"].sum()
net_balance = total_by_person["Chix"] - total_by_person["Matilda"]

st.write("### Total Spending by Person")
st.write(total_by_person)

st.write("### Total Spending by Priority Category")
st.write(total_by_category)

st.write("### Net Balance")
st.markdown(f"**Chix - Matilda = {net_balance:.2f} {currency}**")
st.caption("This shows how much more or less Chix has paid compared to Matilda. Positive means Chix has paid more; negative means Matilda has paid more.")

# Visualization
st.subheader("Monthly Spending by Person")
monthly = converted.groupby(["Month"])[["Chix", "Matilda"]].sum().reset_index()
monthly_melted = monthly.melt(id_vars="Month", var_name="Person", value_name="Amount")
chart = alt.Chart(monthly_melted).mark_bar().encode(
    x="Month:N",
    y="Amount:Q",
    color="Person:N",
    tooltip=["Month", "Person", "Amount"]
).properties(height=400)

st.altair_chart(chart, use_container_width=True)
