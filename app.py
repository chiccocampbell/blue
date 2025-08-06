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
st.markdown(f'''
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
''', unsafe_allow_html=True)

if "user" not in st.session_state or st.session_state.user not in ["Chix", "Mati"]:
    username = st.selectbox("Select your name to continue:", ["Chix", "Mati"])
    st.session_state.user = username
    st.stop()
else:
    st.sidebar.success(f"Logged in as {st.session_state.user}")
    if st.sidebar.button("Logout"):
        del st.session_state.user
        st.rerun()

# ------------------- APP START ----------------------

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

df_this_month = load_data()
df_this_month = df_this_month[df_this_month["Budget Date"].dt.month == now_cet.month]

user_column = "Chix" if st.session_state.user == "Chix" else "Matilda"
total_spent = df_this_month[user_column].sum()

st.sidebar.markdown(f"## {greeting}, {st.session_state.user}! 💸")
st.sidebar.markdown(f"**Your spending this month:** {total_spent:.2f} SEK")

CURRENCY_RATES = {
    "SEK": 1.0,
    "ZAR (Rand)": 1.8,
    "EUR": 0.088
}
