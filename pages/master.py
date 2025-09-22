
import pandas as pd
import streamlit as st
import os
from datetime import datetime


if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("You need to login first.")
    st.stop()


if st.session_state.user_type != "master":
    st.error("You don't have access to this page.")
    st.stop()


st.set_page_config(page_title='Electricity Partnership Admin', layout='wide')


if st.button("← Back to Main Page", key="back_button"):

    if 'page' in st.query_params:
        del st.query_params.page
    st.rerun()


DATA_DIR = "partner_data"
COLS = ['date', 'last_read', 'new_read', 'withdrawl', 'withdrawl_price',
        'withdrawl_by_cash', 'paid', 'left']


if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)



def save_dataframe(df_name, dataframe):
    filename = os.path.join(DATA_DIR, f"{df_name}.csv")
    dataframe.to_csv(filename, index=False)


def load_dataframe(df_name):
    filename = os.path.join(DATA_DIR, f"{df_name}.csv")
    if os.path.exists(filename):
        return pd.read_csv(filename)
    return pd.DataFrame(columns=COLS)



def get_saved_dataframes():
    if not os.path.exists(DATA_DIR):
        return []
    files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
    return [f.replace('.csv', '') for f in files]



if 'named_dataframes' not in st.session_state:
    st.session_state.named_dataframes = {}


    for df_name in get_saved_dataframes():
        st.session_state.named_dataframes[df_name] = load_dataframe(df_name)

if 'current_df' not in st.session_state:
    st.session_state.current_df = None


st.title("Electricity Partnership Management")
st.write("Manage multiple partner electricity data with persistent storage")


col1, col2 = st.columns([1, 2])

with col1:
    st.header("Partners")

    if st.session_state.named_dataframes:
        st.subheader("Existing Partners")
        for df_name in st.session_state.named_dataframes.keys():
            if st.button(f"📊 {df_name}", key=f"btn_{df_name}"):
                st.session_state.current_df = df_name


    with st.expander("Add New Partner", expanded=False):
        with st.form('new_partner_form'):
            new_df_name = st.text_input("Partner Name (must be unique)", key="new_df_name")
            submitted = st.form_submit_button("Create Partner")

            if submitted:
                if new_df_name in st.session_state.named_dataframes:
                    st.error("A partner with this name already exists!")
                elif new_df_name.strip() == "":
                    st.error("Partner name cannot be empty!")
                else:
                    new_df = pd.DataFrame(columns=COLS)
                    st.session_state.named_dataframes[new_df_name] = new_df
                    st.session_state.current_df = new_df_name
                    save_dataframe(new_df_name, new_df)
                    st.success(f"Partner '{new_df_name}' created successfully!")
                    st.rerun()

with col2:
    if st.session_state.current_df:
        st.header(f"Data for: {st.session_state.current_df}")

        current_data = st.session_state.named_dataframes[st.session_state.current_df]
        if not current_data.empty:
            st.dataframe(current_data, use_container_width=True)

            st.subheader("Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Withdrawal", f"{current_data['withdrawl'].sum():.2f} kWh")
            with col2:
                st.metric("Total Amount", f"${current_data['withdrawl_by_cash'].sum():.2f}")
            with col3:
                st.metric("Balance", f"${current_data['left'].sum():.2f}")
        else:
            st.info("No data entries yet for this partner.")


        with st.expander("Add New Entry", expanded=True):
            with st.form('new_entry_form'):
                date = st.date_input("Date", datetime.now())
                last_read = st.number_input("Last Read (kWh)", min_value=0.0, format="%.2f")
                new_read = st.number_input("New Read (kWh)", min_value=0.0, format="%.2f")
                withdrawl_price = st.number_input("Withdrawal Price ($ per kWh)", min_value=0.0, format="%.4f")
                paid = st.number_input("Amount Paid ($)", min_value=0.0, format="%.2f")

                submitted = st.form_submit_button("Add Entry")

                if submitted:
                    if new_read <= last_read:
                        st.error("New read must be greater than last read!")
                    else:
                        withdrawl = new_read - last_read
                        withdrawl_by_cash = withdrawl * withdrawl_price
                        left = paid - withdrawl_by_cash

                        # Create new row
                        new_row = {
                            'date': date.strftime("%Y-%m-%d"),
                            'last_read': last_read,
                            'new_read': new_read,
                            'withdrawl': withdrawl,
                            'withdrawl_price': withdrawl_price,
                            'withdrawl_by_cash': withdrawl_by_cash,
                            'paid': paid,
                            'left': left
                        }


                        updated_df = pd.concat([current_data, pd.DataFrame([new_row])], ignore_index=True)
                        st.session_state.named_dataframes[st.session_state.current_df] = updated_df
                        save_dataframe(st.session_state.current_df, updated_df)
                        st.success("Entry added successfully!")
                        st.rerun()

        if st.button("Delete This Partner", type="secondary"):
            if st.session_state.current_df:

                del st.session_state.named_dataframes[st.session_state.current_df]

                filename = os.path.join(DATA_DIR, f"{st.session_state.current_df}.csv")
                if os.path.exists(filename):
                    os.remove(filename)

                st.session_state.current_df = None
                st.success("Partner deleted successfully!")
                st.rerun()

    else:
        st.info("Select a partner from the list or create a new one to view and edit data.")

st.divider()
with st.expander("How to use this system"):
    st.markdown("""
    ### Electricity Partnership Management System Guide

    1. **Create a New Partner**: 
       - Click "Add New Partner" in the left sidebar
       - Enter a unique name for the partner
       - Click "Create Partner"

    2. **Add Data Entries**:
       - Select a partner from the list on the left
       - Fill in the form with the electricity usage data
       - The system will automatically calculate withdrawal amount and balance

    3. **View Data**:
       - All entries are displayed in a table format
       - Summary statistics show total withdrawal, amount, and balance

    4. **Data Persistence**:
       - All data is automatically saved to CSV files
       - Data remains available between sessions

    5. **Delete a Partner**:
       - Select the partner you want to delete
       - Click the "Delete This Partner" button
       - This will remove all data for that partner
    """)


