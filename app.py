# Chix & Mati Expense Tracker - Full Features with Login, Edit, Import, Themes, QR Access

import pandas as pd
from datetime import datetime
import streamlit as st
import altair as alt
import uuid
from difflib import SequenceMatcher
import qrcode
from io import BytesIO
from PIL import Image
import hashlib

# ------------------- SIMPLE LOGIN CONFIG -------------------

st.title("Chix & Mati Expense Tracker")

# Theme toggle
mode = st.sidebar.radio("Choose Theme Mode", ["Light", "Dark"], index=0)
st.markdown(f"""
    <style>
    .main, body {{
        background-color: {'#ffffff' if mode == 'Light' else '#1e1e1e'};
        color: {'#000000' if mode == 'Light' else '#ffffff'};
    }}
    .stButton>button {{
        background-color: {'#4CAF50' if mode == 'Light' else '#444444'};
        color: white;
        border-radius: 5px;
        padding: 8px 16px;
    }}
    label, .css-1cpxqw2, .css-1kyxreq, .css-1aumxhk {{
        color: {'#000000' if mode == 'Light' else '#ffffff'} !important;
    }}
    </style>
""", unsafe_allow_html=True)

if "user" not in st.session_state:
    username = st.selectbox("Select your name to continue:", ["Chix", "Mati"])
    if username:
        st.session_state.user = username
        st.experimental_rerun()
    st.stop()
else:
    avatar = "https://i.imgur.com/jRjzdhE.png" if st.session_state.user == "Chix" else "https://i.imgur.com/Z7AzH2c.png"
st.sidebar.image(avatar, width=60)
st.sidebar.success(f"Logged in as {st.session_state.user}")
    if st.sidebar.button("Logout"):
        del st.session_state.user
        st.experimental_rerun()

# ------------------- APP START ----------------------

# Personalized greeting
from pytz import timezone
now_cet = datetime.now(timezone("CET"))
current_hour = now_cet.hour
if current_hour < 12:
    greeting = "Good morning"
elif current_hour < 18:
    greeting = "Good afternoon"
else:
    greeting = "Good evening"

if "df" in st.session_state:
    df_this_month = st.session_state.df.copy()
else:
    df_this_month = load_data()

df_this_month = df_this_month[df_this_month["Budget Date"].dt.month == now_cet.month]
total_spent = df_this_month[st.session_state.user].sum()
st.sidebar.markdown(f"## {greeting}, {st.session_state.user}! 💸")
st.sidebar.markdown(f"**Your spending this month:** {total_spent:.2f} SEK")

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

# Theme toggle
mode = st.sidebar.radio("Choose Theme Mode", ["Light", "Dark"])
st.markdown(f"""
    <style>
    body {{
        background-color: {'#f0f0f0' if mode == 'Light' else '#1e1e1e'};
        color: {'#000000' if mode == 'Light' else '#ffffff'};
    }}
    .stButton>button {{
        background-color: {'#4CAF50' if mode == 'Light' else '#444444'};
        color: white;
        border: none;
        border-radius: 5px;
        padding: 8px 16px;
        font-weight: bold;
    }}
    .stSelectbox label, .stTextInput label {{
        color: {'#000000' if mode == 'Light' else '#ffffff'} !important;
    }}
    </style>
""", unsafe_allow_html=True)

st.title("Chix & Mati Expense Tracker")

# Currency
currency = st.selectbox("Select Currency", list(CURRENCY_RATES.keys()), index=0)
rate = CURRENCY_RATES[currency]

# QR code generator for current app URL (placeholder)
st.sidebar.markdown("### 📱 Access on Mobile")
try:
    url = st.secrets["app_url"] if "app_url" in st.secrets else "https://share.streamlit.io/your_app"
except:
    url = "https://share.streamlit.io/your_app"
qr_img = qrcode.make(url)
buf = BytesIO()
qr_img.save(buf)
st.sidebar.image(Image.open(buf), caption="Scan to open app")

# CSV Import
st.sidebar.markdown("### 📥 Import CSV")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type="csv")
if uploaded_file:
    imported_df = pd.read_csv(uploaded_file)
    if set(imported_df.columns).issuperset(set(st.session_state.df.columns)):
        imported_df["Budget Date"] = pd.to_datetime(imported_df["Budget Date"])
        imported_df["Month"] = imported_df["Budget Date"].dt.strftime("%B")
        imported_df["Deleted"] = False
        st.session_state.last_state = st.session_state.df.copy()
        st.session_state.df = pd.concat([st.session_state.df, imported_df], ignore_index=True)
        st.success("CSV data imported successfully.")

        # Show preview
        with st.expander("📄 Preview Imported Data"):
            st.dataframe(imported_df)
    else:
        st.error("CSV format does not match the expected structure.")

# Add/Edit Form
with st.form("Add Expense"):
    st.subheader("➕ Add a New Expense")
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
    budget_date = st.date_input("Budget Date", datetime.today())
    recurring = st.checkbox("Recurring")
    created_by = st.selectbox("Created By", ["Chix", "Mati"])
    submitted = st.form_submit_button("Add Expense")

    if submitted:
        new_row = pd.DataFrame([[str(uuid.uuid4()), item, category, total, chix, matilda, priority, pd.to_datetime(budget_date), recurring, created_by, pd.to_datetime(budget_date).strftime("%B"), False]],
                               columns=list(st.session_state.df.columns))
        st.session_state.last_state = st.session_state.df.copy()
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
        st.success("Expense added!")

# Filters
st.sidebar.markdown("### 🔍 Filter Options")
months = st.sidebar.multiselect("Month", options=st.session_state.df["Month"].unique(), default=st.session_state.df["Month"].unique())
priorities = st.sidebar.multiselect("Priority", options=st.session_state.df["Priority"].unique(), default=st.session_state.df["Priority"].unique())
only_recurring = st.sidebar.checkbox("Only show recurring")
show_deleted = st.sidebar.checkbox("Show archived/deleted")

filtered_df = st.session_state.df.copy()
filtered_df = filtered_df[filtered_df["Month"].isin(months) & filtered_df["Priority"].isin(priorities)]
if only_recurring:
    filtered_df = filtered_df[filtered_df["Recurring"] == True]
if not show_deleted:
    filtered_df = filtered_df[filtered_df["Deleted"] == False]

# Deletion and Undo
st.subheader("🗑️ Manage Records")
archive_ids = st.multiselect("Select records to archive/delete", filtered_df["ID"].tolist())
if st.button("Confirm Archive/Delete"):
    st.session_state.last_state = st.session_state.df.copy()
    st.session_state.df.loc[st.session_state.df["ID"].isin(archive_ids), "Deleted"] = True
    st.success("Selected records archived.")

if st.session_state.last_state is not None:
    if st.button("Undo Last Action"):
        st.session_state.df = st.session_state.last_state.copy()
        st.session_state.last_state = None
        st.success("Undo successful")

# Export Filtered CSV
st.download_button(
    label="📤 Download Filtered CSV",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_expenses.csv",
    mime="text/csv"
)

# Summary
st.subheader("📊 Summary")
converted_df = filtered_df.copy()
converted_df[["Total", "Chix", "Matilda"]] *= rate

summary_person = converted_df[["Chix", "Matilda"]].sum()
summary_category = converted_df.groupby("Category")["Total"].sum()
net_balance = summary_person["Chix"] - summary_person["Matilda"]

st.write("### Total by Person")
st.write(summary_person)

st.write("### Total by Category")
st.write(summary_category)

st.markdown(f"**Net Balance (Chix - Mati): {net_balance:.2f} {currency}**")

# Chart
st.subheader("📈 Monthly Spending by Person")
monthly_summary = converted_df.groupby("Month")[["Chix", "Matilda"]].sum().reset_index()
monthly_melted = monthly_summary.melt(id_vars="Month", var_name="Person", value_name="Amount")
chart = alt.Chart(monthly_melted).mark_bar().encode(
    x="Month:N",
    y="Amount:Q",
    color="Person:N",
    tooltip=["Month", "Person", "Amount"]
)
st.altair_chart(chart, use_container_width=True)
