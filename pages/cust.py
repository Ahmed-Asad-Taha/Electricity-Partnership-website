import streamlit as st
import pandas as pd
import os
from datetime import datetime

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("You need to login first.")
    st.stop()


if st.session_state.user_type != "cust" and st.session_state.user_type != "master":
    st.error("You don't have access to this page.")
    st.stop()


st.set_page_config(page_title="Electricity Partnership - Customer View")

# Navigation
if st.button("← Back to Main Page", key="back_button"):

    if 'page' in st.query_params:
        del st.query_params.page
    st.rerun()

st.title("Electricity Partnership - Customer Portal")


DATA_DIR = "partner_data"


if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)



def get_saved_dataframes():
    if not os.path.exists(DATA_DIR):
        return []
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    return [f.replace('.csv', '') for f in files]



def load_dataframe(df_name):
    filename = os.path.join(DATA_DIR, f"{df_name}.csv")
    if os.path.exists(filename):
        df = pd.read_csv(filename)

        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        return df
    return pd.DataFrame()






available_partners = get_saved_dataframes()

if not available_partners:
    st.warning("No customer data available. Please add data in the admin portal.")
    st.stop()


st.subheader("Select Your Account")
selected_customer = st.selectbox(
    "Choose your account name:",
    options=available_partners,
    key="customer_select"
)


customer_data = load_dataframe(selected_customer)

if customer_data.empty:
    st.info("No data available for this customer yet.")
else:

    st.subheader(f"Account: {selected_customer}")


    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Consumption", f"{customer_data['withdrawl'].sum():.2f} kWh")
    with col2:
        st.metric("Total Amount", f"${customer_data['withdrawl_by_cash'].sum():.2f}")
    with col3:
        st.metric("Total Paid", f"${customer_data['paid'].sum():.2f}")
    with col4:
        balance = customer_data['left'].sum()
        color = "green" if balance >= 0 else "red"
        st.metric("Current Balance", f"${balance:.2f}", delta_color="off")
