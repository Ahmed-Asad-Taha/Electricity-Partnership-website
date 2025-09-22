import streamlit as st

st.set_page_config(page_title="Electricity Partnership Website", layout="wide")
st.title("Electricity Partnership Website")


if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None


def logout():
    st.session_state.authenticated = False
    st.session_state.user_type = None
    st.rerun()


def check_pass():
    password = st.text_input("Enter your password", type="password")
    if st.button("Submit"):
        if password == 'aram2004':
            st.session_state.authenticated = True
            st.session_state.user_type = "master"
            st.rerun()
        elif password == '1':
            st.session_state.authenticated = True
            st.session_state.user_type = "cust"
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")



if not st.session_state.authenticated:
    st.header("Login")
    check_pass()
else:

    st.sidebar.button("Logout", on_click=logout)

    if st.session_state.user_type == "master":
        st.header("Admin Portal")
        st.write("Welcome to the Admin Portal")


        if st.button("Manage Partners", key="manage_partners"):
            st.query_params.page = "master"
            st.rerun()

        if st.button("View Customer Data", key="view_customer_data"):
            st.query_params.page = "cust"
            st.rerun()

    elif st.session_state.user_type == "cust":
        st.header("Customer Portal")
        st.write("Welcome to the Customer Portal")

        if st.button("View My Data", key="view_my_data"):
            st.query_params.page = "cust"
            st.rerun()











