import os
from decimal import Decimal, InvalidOperation

import pandas as pd
import streamlit as st

from main import BankSystem, Account, Audit, initialize_tables

st.set_page_config(
    page_title="VaultBank | Banking Portal",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------- Styling ----------------------------
st.markdown(
    """
    <style>
    .stApp { background: #f4f7fb; }
    [data-testid="stSidebar"] { background: #101d35; }
    [data-testid="stSidebar"] * { color: #f4f7fb; }
    [data-testid="stSidebar"] button { border-color: #31415d; }
    .hero {
        padding: 1.6rem 1.8rem; border-radius: 20px;
        background: linear-gradient(120deg, #142744, #244d79);
        color: white; margin-bottom: 1.2rem;
    }
    .hero h1 { color: white; margin: 0; font-size: 2rem; }
    .hero p { color: #dce8f7; margin: .45rem 0 0 0; }
    .metric-card {
        background: white; border: 1px solid #e3eaf3; border-radius: 16px;
        padding: 1rem 1.1rem; min-height: 105px;
        box-shadow: 0 3px 12px rgba(21, 45, 78, .04);
    }
    .metric-label { color: #66758b; font-size: .88rem; }
    .metric-value { color: #142744; font-size: 1.65rem; font-weight: 750; margin-top: .3rem; }
    .section-note { color: #61718a; font-size: .93rem; }
    div.stButton > button { border-radius: 10px; font-weight: 600; }
    div[data-testid="stForm"] { background: white; padding: 1.1rem; border: 1px solid #e3eaf3; border-radius: 14px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------- Application setup -------------------------
@st.cache_resource
def get_bank():
    return BankSystem()


def money(value):
    return f"₹{float(value or 0):,.2f}"


def get_current_account():
    if not st.session_state.get("logged_in"):
        return None
    return Account.load_from_db(
        st.session_state.get("account_number", ""),
        st.session_state.get("pin", ""),
    )


def refresh_account():
    account = get_current_account()
    if account:
        st.session_state["holder_name"] = account.get_name()
        st.session_state["balance"] = account.get_balance()
    else:
        st.session_state["logged_in"] = False
        st.session_state.pop("account_number", None)
        st.session_state.pop("pin", None)
    return account


def show_hero(title, subtitle):
    st.markdown(
        f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def show_metric(label, value):
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div></div>',
        unsafe_allow_html=True,
    )


def audit_frame(logs, admin=False):
    if not logs:
        st.info("No audit records are available yet.")
        return
    if admin:
        rows = [
            {
                "Log ID": item.get("id"),
                "Account Number": item.get("account_number"),
                "Account Holder": item.get("holder_name"),
                "Action": item.get("action"),
                "Amount": float(item.get("amount", 0)),
                "Timestamp": item.get("timestamp"),
            }
            for item in logs
        ]
    else:
        rows = [
            {
                "Log ID": item.get("id"),
                "Account Holder": item.get("holder_name"),
                "Action": item.get("action"),
                "Amount": float(item.get("amount", 0)),
                "Timestamp": item.get("timestamp"),
            }
            for item in logs
        ]
    df = pd.DataFrame(rows)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={"Amount": st.column_config.NumberColumn("Amount (₹)", format="₹ %.2f")},
    )
    st.download_button(
        "Download audit logs as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="bank_audit_logs.csv",
        mime="text/csv",
    )


try:
    bank = get_bank()
except Exception as exc:
    st.error("The banking application could not initialize.")
    st.code(str(exc))
    st.info("Check that PostgreSQL is running and Database.py contains the correct connection details.")
    st.stop()

# ------------------------------- Sidebar -------------------------------
with st.sidebar:
    st.markdown("# 🏦 VaultBank")
    st.caption("BANKING MANAGEMENT SYSTEM")
    st.divider()

    if st.session_state.get("logged_in"):
        st.success(f"Signed in as {st.session_state.get('holder_name', 'Customer')}")
        pages = ["Dashboard", "Deposit Money", "Withdraw Money", "Transaction History", "Account Settings"]
        page = st.radio("CUSTOMER MENU", pages, label_visibility="visible")
        st.divider()
        if st.button("Log out", use_container_width=True):
            for key in ("logged_in", "account_number", "pin", "holder_name", "balance"):
                st.session_state.pop(key, None)
            st.rerun()
    else:
        page = st.radio("MAIN MENU", ["Welcome", "Create Account", "Customer Login", "Admin Portal"])

    st.divider()
    st.caption("Demo project · PostgreSQL powered")

# ------------------------------- Welcome -------------------------------
if page == "Welcome":
    show_hero("Banking, made simple.", "A clean digital banking portal for managing your account and transactions.")
    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("Welcome to VaultBank")
        st.write("Create an account or log in to manage your balance, make deposits and withdrawals, and review your transaction history.")
        st.markdown("- Secure account-number and PIN login flow\n- Deposit and withdrawal validation\n- Transaction audit history\n- Account profile and PIN management")
        if st.button("Get started — create an account", type="primary"):
            st.session_state["welcome_action"] = "Create Account"
            st.rerun()
        if st.session_state.pop("welcome_action", None) == "Create Account":
            st.info("Choose **Create Account** from the sidebar to continue.")
    with right:
        st.markdown("### Banking overview")
        c1, c2 = st.columns(2)
        with c1:
            show_metric("ACCOUNT ACCESS", "24/7")
        with c2:
            show_metric("TRANSACTION LOGS", "Tracked")
        st.caption("This is a student project, not a production banking service.")

# ---------------------------- Create account ----------------------------
elif page == "Create Account":
    show_hero("Create your account", "Open your VaultBank demo account in a few steps.")
    with st.form("create_account_form", clear_on_submit=False):
        name = st.text_input("Full name", max_chars=100, placeholder="Enter your full name")
        pin = st.text_input("Create a 4-digit PIN", type="password", max_chars=4)
        confirm_pin = st.text_input("Confirm PIN", type="password", max_chars=4)
        submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)
    if submitted:
        name = name.strip()
        if not name:
            st.error("Please enter your name.")
        elif len(pin) != 4 or not pin.isdigit():
            st.error("Your PIN must contain exactly 4 digits.")
        elif pin != confirm_pin:
            st.error("The PINs do not match.")
        else:
            with st.spinner("Creating your account..."):
                account = bank.create_account(name, pin)
            if account:
                st.success("Your account has been created successfully.")
                st.warning("Save your account number now. You will need it to log in.")
                st.code(account.get_account_number())
                st.session_state["new_account_number"] = account.get_account_number()
            else:
                st.error("Account creation failed. Check your database connection and try again.")
    if st.session_state.get("new_account_number"):
        st.caption("Newly created account number")
        st.code(st.session_state["new_account_number"])

# ------------------------------- Login --------------------------------
elif page == "Customer Login":
    show_hero("Customer login", "Sign in with your account number and 4-digit PIN.")
    with st.form("login_form"):
        account_number = st.text_input("Account number", max_chars=50).strip().upper()
        pin = st.text_input("4-digit PIN", type="password", max_chars=4)
        submitted = st.form_submit_button("Log in", type="primary", use_container_width=True)
    if submitted:
        if not account_number or len(pin) != 4 or not pin.isdigit():
            st.error("Enter a valid account number and 4-digit PIN.")
        else:
            account = bank.read_account(account_number, pin)
            if account:
                st.session_state["logged_in"] = True
                st.session_state["account_number"] = account.get_account_number()
                st.session_state["pin"] = pin
                st.session_state["holder_name"] = account.get_name()
                st.session_state["balance"] = account.get_balance()
                st.success(f"Welcome back, {account.get_name()}!")
                st.rerun()
            else:
                st.error("Incorrect account number or PIN.")

# ----------------------------- Dashboard ------------------------------
elif page == "Dashboard":
    account = refresh_account()
    if not account:
        st.warning("Your account could not be loaded. Please log in again.")
        st.stop()
    show_hero(f"Welcome back, {account.get_name()} 👋", "Here is a summary of your bank account.")
    col1, col2, col3 = st.columns(3)
    with col1:
        show_metric("AVAILABLE BALANCE", money(account.get_balance()))
    with col2:
        show_metric("ACCOUNT NUMBER", account.get_account_number())
    with col3:
        show_metric("ACCOUNT STATUS", "Active")
    st.subheader("Quick actions")
    q1, q2, q3 = st.columns(3)
    with q1:
        if st.button("＋ Deposit money", use_container_width=True):
            st.session_state["quick_page"] = "Deposit Money"
            st.rerun()
    with q2:
        if st.button("− Withdraw money", use_container_width=True):
            st.session_state["quick_page"] = "Withdraw Money"
            st.rerun()
    with q3:
        if st.button("View transactions", use_container_width=True):
            st.session_state["quick_page"] = "Transaction History"
            st.rerun()
    quick_page = st.session_state.pop("quick_page", None)
    if quick_page:
        st.info(f"Select **{quick_page}** in the customer menu on the sidebar.")
    st.subheader("Recent activity")
    audit_frame(bank.get_audit_logs(account.get_account_number()))

# ------------------------------- Deposit ------------------------------
elif page == "Deposit Money":
    account = refresh_account()
    if not account:
        st.warning("Please log in again.")
        st.stop()
    show_hero("Deposit money", "Add funds to your account.")
    show_metric("CURRENT BALANCE", money(account.get_balance()))
    with st.form("deposit_form"):
        amount_text = st.text_input("Deposit amount (₹)", placeholder="e.g. 500.00")
        submitted = st.form_submit_button("Confirm deposit", type="primary", use_container_width=True)
    if submitted:
        try:
            amount = Decimal(amount_text.strip())
            if not amount.is_finite() or amount <= 0:
                st.error("Enter an amount greater than zero.")
            elif amount > Decimal("9999999999999.99"):
                st.error("The amount is too large.")
            elif bank.deposit(account.get_account_number(), account.get_pin(), float(amount)):
                st.success(f"Deposit of {money(amount)} completed.")
                st.rerun()
            else:
                st.error("The deposit could not be completed. Please try again.")
        except (InvalidOperation, ValueError):
            st.error("Enter a valid numeric amount, such as 500.00.")

# ------------------------------ Withdrawal ----------------------------
elif page == "Withdraw Money":
    account = refresh_account()
    if not account:
        st.warning("Please log in again.")
        st.stop()
    show_hero("Withdraw money", "Withdraw funds from your available balance.")
    show_metric("AVAILABLE BALANCE", money(account.get_balance()))
    with st.form("withdraw_form"):
        amount_text = st.text_input("Withdrawal amount (₹)", placeholder="e.g. 250.00")
        submitted = st.form_submit_button("Confirm withdrawal", type="primary", use_container_width=True)
    if submitted:
        try:
            amount = Decimal(amount_text.strip())
            if not amount.is_finite() or amount <= 0:
                st.error("Enter an amount greater than zero.")
            elif amount > Decimal("9999999999999.99"):
                st.error("The amount is too large.")
            elif amount > Decimal(str(account.get_balance())):
                st.error("Insufficient balance for this withdrawal.")
            elif bank.withdraw(account.get_account_number(), account.get_pin(), float(amount)):
                st.success(f"Withdrawal of {money(amount)} completed.")
                st.rerun()
            else:
                st.error("The withdrawal could not be completed. Please try again.")
        except (InvalidOperation, ValueError):
            st.error("Enter a valid numeric amount, such as 250.00.")

# --------------------------- Transaction history -----------------------
elif page == "Transaction History":
    account = refresh_account()
    if not account:
        st.warning("Please log in again.")
        st.stop()
    show_hero("Transaction history", "Review account activity recorded in the audit log.")
    logs = bank.get_audit_logs(account.get_account_number())
    audit_frame(logs)

# ---------------------------- Account settings -------------------------
elif page == "Account Settings":
    account = refresh_account()
    if not account:
        st.warning("Please log in again.")
        st.stop()
    show_hero("Account settings", "Manage your profile and account security.")
    left, right = st.columns(2)
    with left:
        st.subheader("Update name")
        with st.form("update_name_form"):
            new_name = st.text_input("New full name", value=account.get_name(), max_chars=100)
            update_name = st.form_submit_button("Save name", type="primary")
        if update_name:
            new_name = new_name.strip()
            if not new_name:
                st.error("Name cannot be empty.")
            else:
                account.set_name(new_name)
                if bank.update_account(account):
                    st.session_state["holder_name"] = new_name
                    Audit.log_action(account.get_account_number(), new_name, "Account name updated", 0.0)
                    st.success("Name updated successfully.")
                    st.rerun()
                else:
                    st.error("Could not update your name.")
    with right:
        st.subheader("Change PIN")
        with st.form("change_pin_form"):
            current_pin = st.text_input("Current PIN", type="password", max_chars=4)
            new_pin = st.text_input("New 4-digit PIN", type="password", max_chars=4)
            confirm_new_pin = st.text_input("Confirm new PIN", type="password", max_chars=4)
            update_pin = st.form_submit_button("Update PIN", type="primary")
        if update_pin:
            if current_pin != account.get_pin():
                st.error("Current PIN is incorrect.")
            elif len(new_pin) != 4 or not new_pin.isdigit():
                st.error("New PIN must contain exactly 4 digits.")
            elif new_pin != confirm_new_pin:
                st.error("New PINs do not match.")
            elif new_pin == current_pin:
                st.error("Choose a different PIN.")
            else:
                account.set_pin(new_pin)
                if bank.update_account(account):
                    st.session_state["pin"] = new_pin
                    Audit.log_action(account.get_account_number(), account.get_name(), "Account PIN updated", 0.0)
                    st.success("PIN updated successfully.")
                    st.rerun()
                else:
                    st.error("Could not update your PIN.")
    st.divider()
    st.subheader("Close account")
    st.warning("Account deletion is permanent. Your current database schema also links audit logs to accounts, so deletion may fail while audit records exist.")
    with st.form("delete_account_form"):
        confirm_account = st.text_input("Type your account number to confirm")
        confirm_delete_pin = st.text_input("Enter your PIN", type="password", max_chars=4)
        delete_confirmed = st.checkbox("I understand this action cannot be undone.")
        delete_submit = st.form_submit_button("Delete my account")
    if delete_submit:
        if not delete_confirmed:
            st.error("Please confirm that you understand the consequences.")
        elif confirm_account.strip().upper() != account.get_account_number() or confirm_delete_pin != account.get_pin():
            st.error("Account number or PIN does not match.")
        else:
            if bank.delete_account(account.get_account_number(), account.get_pin()):
                for key in ("logged_in", "account_number", "pin", "holder_name", "balance"):
                    st.session_state.pop(key, None)
                st.success("Account deleted.")
                st.rerun()
            else:
                st.error("Account deletion failed. Existing audit records may be preventing deletion because of the database foreign-key constraint.")

# ------------------------------- Admin --------------------------------
elif page == "Admin Portal":
    show_hero("Administrator portal", "Review and manage system audit records.")
    admin_password = os.getenv("BANK_ADMIN_PASSWORD", "")
    if not admin_password:
        st.warning("Admin access is disabled until you configure the BANK_ADMIN_PASSWORD environment variable.")
        st.code('export BANK_ADMIN_PASSWORD="choose-a-strong-password"')
        st.caption("On Windows PowerShell, use: $env:BANK_ADMIN_PASSWORD = \"choose-a-strong-password\"")
    else:
        if not st.session_state.get("admin_authenticated"):
            with st.form("admin_login_form"):
                entered_password = st.text_input("Administrator password", type="password")
                admin_submit = st.form_submit_button("Unlock admin portal", type="primary", use_container_width=True)
            if admin_submit:
                if entered_password == admin_password:
                    st.session_state["admin_authenticated"] = True
                    st.rerun()
                else:
                    st.error("Incorrect administrator password.")
        else:
            top1, top2 = st.columns([3, 1])
            with top1:
                st.subheader("All audit logs")
            with top2:
                if st.button("Lock admin portal"):
                    st.session_state["admin_authenticated"] = False
                    st.rerun()
            logs = bank.get_all_audit_logs()
            show_metric("TOTAL AUDIT RECORDS", f"{len(logs):,}")
            audit_frame(logs, admin=True)
            st.divider()
            st.subheader("Clear audit logs")
            st.warning("This permanently deletes all audit-log records. It does not delete customer accounts.")
            with st.form("clear_logs_form"):
                confirm_clear = st.checkbox("I confirm that all audit logs should be permanently deleted.")
                clear_submit = st.form_submit_button("Clear all audit logs")
            if clear_submit:
                if not confirm_clear:
                    st.error("Tick the confirmation box first.")
                elif bank.clear_audit_logs():
                    st.success("Audit logs cleared.")
                    st.rerun()
                else:
                    st.error("Could not clear the audit logs.")

st.markdown("---")
st.caption("VaultBank · Educational project · Do not use for real financial transactions.")
