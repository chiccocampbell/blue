# Chix & Mati Expense Tracker - Full Features with Edit, Import, Themes, QR Access

import pandas as pd
from datetime import datetime
import streamlit as st
import altair as alt
import uuid
from difflib import SequenceMatcher
import qrcode
from io import BytesIO
from PIL import Image

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

# The rest of the app code (form, editing, filtering, export, summary, visualization) continues here...
