# Chix & Mati Expense Tracker - Full Features with Edit by Unique ID and Record Lookup

import pandas as pd
from datetime import datetime
import streamlit as st
import altair as alt
import uuid
from difflib import SequenceMatcher

CURRENCY_RATES = {
    "SEK": 1.0,
    "ZAR (Rand)": 1.8,
    "EUR": 0.088
}

@st.cache_data
def load_data():
    expenses = [
        [str(uuid.uuid4()), "Mattress", "Furniture", 0, 0, 0, "very high", "2025-07-25", False, "Chix"],
        [str(uuid.uuid4()), "Washing Machine", "Furniture", 5743, 5743, 0, "very high", "2025-07-25", False, "Chix"],
        [str(uuid.uuid4()), "Humidifier", "Furniture", 4500, 2250, 2250, "very high", "2025-08-25", False, "Mati"],
        [str(uuid.uuid4()), "Couch", "Furniture", 7000, 3500, 3500, "high", "2025-07-25", True, "Mati"],
        [str(uuid.uuid4()), "Groceries - ICA", "Groceries", 1200, 600, 600, "medium", "2025-08-15", False, "Chix"],
        [str(uuid.uuid4()), "Internet Bill", "Rent", 450, 225, 225, "high", "2025-08-01", True, "Mati"],
        [str(uuid.uuid4()), "Electricity", "Rent", 890, 445, 445, "medium", "2025-08-05", False, "Chix"],
        [str(uuid.uuid4()), "Dinner Out", "Entertainment", 900, 450, 450, "low", "2025-08-20", False, "Mati"],
        [str(uuid.uuid4()), "Savings Transfer", "Savings", 3000, 1500, 1500, "very high", "2025-07-31", True, "Chix"],
        [str(uuid.uuid4()), "Laundry Basket", "Furniture", 200, 100, 100, "medium", "2025-08-10", False, "Mati"]
    ]
    df = pd.DataFrame(expenses, columns=[
        "ID", "Item", "Category", "Total", "Chix", "Matilda", "Priority", "Budget Date", "Recurring", "Created By"
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

if st.button("🔄 Refresh View"):
    st.experimental_rerun()

with st.form("Add Expense"):
    st.subheader("Add a New Expense")
    item = st.text_input("Item")
    category = st.selectbox("Category", ["Furniture", "Groceries", "Rent", "Entertainment", "Savings", "Other"])
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
    created_by = st.selectbox("Created By", ["Chix", "Mati"])
    submitted = st.form_submit_button("Add Expense")

    if submitted:
        new_row = pd.DataFrame([[str(uuid.uuid4()), item, category, total, chix, matilda, priority, pd.to_datetime(budget_date), recurring, created_by, pd.to_datetime(budget_date).strftime("%B"), False]],
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

# Edit existing records by unique ID
st.subheader("Edit Existing Expense")
with st.expander("Edit Record"):
    st.caption("Use the record table below to find the ID for editing. You can also search for a specific item below.")
    search_term = st.text_input("Search (natural language supported)")

    if search_term:
        def fuzzy_match(row):
            row_text = ' '.join([str(v).lower() for v in row.values])
            return SequenceMatcher(None, search_term.lower(), row_text).ratio() > 0.3

        search_df = filtered_df[filtered_df.apply(fuzzy_match, axis=1)]
    else:
        search_df = filtered_df

    st.dataframe(search_df[["ID", "Item", "Total", "Chix", "Matilda", "Priority", "Budget Date"]])

    selected_id = st.text_input("Enter ID of the record to edit")
    if selected_id in filtered_df["ID"].values:
        row_to_edit = filtered_df[filtered_df["ID"] == selected_id].index[0]
        with st.form("edit_form"):
            row = st.session_state.df.loc[row_to_edit]
            item = st.text_input("Item", row["Item"])
            category = st.selectbox("Category", ["Furniture", "Groceries", "Rent", "Entertainment", "Savings", "Other"], index=["Furniture", "Groceries", "Rent", "Entertainment", "Savings", "Other"].index(row["Category"]))
            total = st.number_input("Total", value=float(row["Total"]))
            chix = st.number_input("Chix Share", value=float(row["Chix"]))
            matilda = total - chix
            priority = st.selectbox("Priority", ["very high", "high", "medium", "low"], index=["very high", "high", "medium", "low"].index(row["Priority"]))
            budget_date = st.date_input("Budget Date", value=row["Budget Date"])
            recurring = st.checkbox("Recurring", value=row["Recurring"])
            created_by = st.selectbox("Created By", ["Chix", "Mati"], index=["Chix", "Mati"].index(row["Created By"]))
            submit_edit = st.form_submit_button("Save Changes")
            if submit_edit:
                st.session_state.last_state = st.session_state.df.copy()
                for col, val in zip(["Item", "Category", "Total", "Chix", "Matilda", "Priority", "Budget Date", "Recurring", "Created By"],
                                     [item, category, total, chix, matilda, priority, budget_date, recurring, created_by]):
                    st.session_state.df.at[row_to_edit, col] = val
                st.session_state.df.at[row_to_edit, "Month"] = pd.to_datetime(budget_date).strftime("%B")
                st.success("Changes saved!")
                st.experimental_rerun()

# Remaining code (deletion, export, summaries, visualization)...
