# dashboard.py
import streamlit as st
from features.transactions import transactions as transaction_features
from features.budgets import budgets as budget_features
from datetime import datetime

def get_monthly_summary(transactions):
    """Calculates total income, expenses, and balance for the current month."""
    now = datetime.now()
    total_income = 0
    total_expenses = 0

    for t in transactions:
        if t['date'].month == now.month and t['date'].year == now.year:
            if t['type'] == 'income':
                total_income += t['amount']
            elif t['type'] == 'expense':
                total_expenses += t['amount']
    
    balance = total_income - total_expenses
    return total_income, total_expenses, balance

def get_budget_status(budgets, transactions):
    """Calculates spending, remaining, utilization, and status for each budget category for the current month."""
    now = datetime.now()
    monthly_spending = {category: 0 for category in budgets}

    for t in transactions:
        if t['type'] == 'expense' and t['date'].month == now.month and t['date'].year == now.year:
            if t['category'] in monthly_spending:
                monthly_spending[t['category']] += t['amount']
    
    budget_status = {}
    for category, budget_amount in budgets.items():
        spent_amount = monthly_spending.get(category, 0)
        remaining = budget_amount - spent_amount
        utilization = (spent_amount / budget_amount) * 100 if budget_amount > 0 else 0

        if utilization > 100:
            status = "Over"
            color = "red"
        elif utilization >= 70:
            status = "Warning"
            color = "yellow"
        else:
            status = "OK"
            color = "green"
        
        budget_status[category] = {
            "budget": budget_amount,
            "spent": spent_amount,
            "remaining": remaining,
            "utilization": utilization,
            "status": status,
            "color": color
        }
    return budget_status

def main():
    st.set_page_config(layout="centered", page_title="Finance Tracker Dashboard")

def main():
    st.set_page_config(layout="wide", page_title="Finance Tracker Dashboard")

    st.title("💰 Finance Tracker Dashboard")
    st.markdown("---")

    all_transactions = transaction_features._read_transactions()
    all_budgets = budget_features._read_budgets()

    # --- Balance Section ---
    st.header("Overall Balance")
    total_income, total_expenses, balance = get_monthly_summary(all_transactions)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"### Income: ${total_income / 100:.2f}")
    with col2:
        st.warning(f"### Expenses: ${total_expenses / 100:.2f}")
    with col3:
        balance_color = "green" if balance >= 0 else "red"
        st.markdown(f"### <p style='color:{balance_color};'>Balance: ${balance / 100:.2f}</p>", unsafe_allow_html=True)

    st.markdown("---")

    # --- Budget Status Section ---
    st.header("Budget Status (Current Month)")
    if all_budgets:
        budget_summary = get_budget_status(all_budgets, all_transactions)
        for category, data in budget_summary.items():
            st.subheader(f"{category} Budget")
            col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
            with col_b1:
                st.metric("Budgeted", f"${data['budget'] / 100:.2f}")
            with col_b2:
                st.metric("Spent", f"${data['spent'] / 100:.2f}")
            with col_b3:
                st.metric("Remaining", f"${data['remaining'] / 100:.2f}")
            
            progress_color = {
                "green": "#4CAF50",  # Green
                "yellow": "#FFC107", # Yellow
                "red": "#F44336"     # Red
            }.get(data['color'], "#4CAF50")

            st.progress(min(1.0, data['utilization'] / 100), text=f"**{data['utilization']:.2f}% Used**")
            st.markdown(f"<style> .st-emotion-cache-16oym6q {{ background-color: {progress_color}; }} </style>", unsafe_allow_html=True)
            st.markdown("---")
    else:
        st.info("No budgets set. Go to the 'Budgets' section to set your monthly budgets.")

    st.markdown("---")

    # --- Recent Transactions Table ---
    st.header("Recent Transactions")
    if all_transactions:
        recent_transactions = all_transactions[:10]
        
        # Prepare data for display
        display_data = []
        for t in recent_transactions:
            amount_str = f"{t['amount'] / 100:.2f}"
            color = "green" if t['type'] == 'income' else "red"
            display_data.append({
                "Date": t['date'].strftime("%Y-%m-%d"),
                "Type": f":{color}[{t['type'].capitalize()}]",
                "Category": t['category'],
                "Description": t['description'],
                "Amount": f":{color}[${amount_str}]"
            })
        
        st.dataframe(display_data, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions recorded yet.")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
