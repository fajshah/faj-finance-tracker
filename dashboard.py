import sys
sys.path.insert(0, '.')
import streamlit as st
import pandas as pd
from datetime import datetime
from features.smart_assistant import smart_assistant
import matplotlib.pyplot as plt
from features.data_management import data_management

# --- Page Configuration ---
st.set_page_config(
    page_title="Faj Finance Dashboard",
    layout="wide",
)

# --- File Paths ---
TRANSACTIONS_FILE = "database/transactions.txt"
BUDGETS_FILE = "database/budgets.txt"

# --- Categories ---
EXPENSE_CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"]
INCOME_CATEGORIES = ["Salary", "Freelance", "Business", "Investment", "Gift", "Other"]

# --- Transaction Functions ---

def write_transaction(date, type, category, description, amount):
    """Writes a new transaction to the text file."""
    with open(TRANSACTIONS_FILE, "a") as f:
        f.write(f"{date},{type},{category},{description},{int(amount * 100)}\n")

def write_budgets(budgets):
    """Writes all budgets to the file, overwriting it."""
    with open(BUDGETS_FILE, "w") as f:
        for category, amount in budgets.items():
            f.write(f"{category},{int(amount * 100)}\n")

# --- Helper Functions ---

def load_transactions():
    """Loads transactions from the text file into a DataFrame, handling commas in description."""
    transactions = []
    try:
        with open(TRANSACTIONS_FILE, "r") as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(',')
                    if len(parts) >= 5:
                        date = parts[0]
                        trans_type = parts[1]
                        category = parts[2]
                        amount = parts[-1]
                        description = ",".join(parts[3:-1])
                        
                        try:
                            transactions.append([date, trans_type, category, description, int(amount)])
                        except ValueError:
                            # Handle cases where amount is not a valid integer
                            pass
    
        if not transactions:
            return pd.DataFrame(columns=['date', 'type', 'category', 'description', 'amount'])

        df = pd.DataFrame(transactions, columns=['date', 'type', 'category', 'description', 'amount'])
        df['date'] = pd.to_datetime(df['date']).dt.date
        df['amount'] = df['amount'] / 100  # Convert cents to dollars
        return df
        
    except FileNotFoundError:
        return pd.DataFrame(columns=['date', 'type', 'category', 'description', 'amount'])


def load_budgets():
    """Loads budgets from the text file into a dictionary."""
    budgets = {}
    try:
        with open(BUDGETS_FILE, "r") as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(',')
                    if len(parts) == 2:
                        category = parts[0]
                        try:
                            budgets[category] = int(parts[1]) / 100
                        except ValueError:
                            pass # Ignore malformed budget lines
    except FileNotFoundError:
        pass
    return budgets

def _calculate_savings_rate_score(total_income, total_expenses):
    """Calculates the savings rate score (max 40)."""
    if total_income == 0:
        return 0
    savings_rate = ((total_income - total_expenses) / total_income) * 100
    if savings_rate >= 20:
        return 40
    elif savings_rate >= 10:
        return 30
    elif savings_rate >= 0:
        return 20
    else:
        return 0

def _calculate_budget_adherence_score(monthly_transactions, budgets):
    """Calculates the budget adherence score (max 35)."""
    if not budgets:
        return 0
    
    total_budget_utilized = 0
    num_budgeted_categories = 0
    
    for category, budget_amount in budgets.items():
        spent = sum(
            t['amount'] for t in monthly_transactions 
            if t['type'] == 'expense' and t['category'] == category
        )
        if budget_amount > 0:
            utilization = (spent / budget_amount) * 100
            total_budget_utilized += min(utilization, 100)
            num_budgeted_categories += 1

    if num_budgeted_categories == 0:
        return 35

    avg_utilization = total_budget_utilized / num_budgeted_categories
    
    if avg_utilization <= 80:
        return 35
    elif avg_utilization <= 90:
        return 25
    elif avg_utilization <= 100:
        return 15
    else:
        return 5

def _calculate_income_expense_score(total_income, total_expenses):
    """Calculates the income vs. expense score (max 25)."""
    if total_income == 0:
        return 0
    if total_income > total_expenses:
        return 25
    elif total_income * 0.9 < total_expenses:
        return 10
    else:
        return 0

def _interpret_score(score):
    """Prints an interpretation of the financial health score."""
    if score >= 75:
        return "Excellent! Your finances are in great shape. Keep up the good work!"
    elif score >= 50:
        return "Good. There's room for improvement, but you're on the right track."
    else:
        return "Needs Attention. Your finances require careful review. Focus on budgeting and saving."

# --- Main Dashboard ---

def main():
    """The main function to run the Streamlit dashboard."""

    # --- Custom CSS for Styling ---
    st.markdown("""
        <style>
        .main {
            max-width: 1200px;
            margin: 0 auto;
        }
        .st-emotion-cache-1jicfl2 {
            width: 100%;
            padding: 2rem 1rem 1rem;
        }
        .card {
            background-color: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .metric-label {
            font-size: 1.1rem;
            color: #555;
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
        }
        .income {
            color: #28a745; /* Green */
        }
        .expense {
            color: #dc3545; /* Red */
        }
        .balance {
            color: #007bff; /* Blue */
        }
        </style>
    """, unsafe_allow_html=True)

    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ["Dashboard", "Add Income", "Add Expense", "Set Budget", "Smart Assistant", "Analytics"])

    if selection == "Dashboard":
        st.title("Faj Financial Dashboard")

        # --- Load Data ---
        transactions_df = load_transactions()
        budgets = load_budgets()

        # --- Balance Section ---
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Current Financial Overview")

        if not transactions_df.empty:
            total_income = transactions_df[transactions_df['type'] == 'income']['amount'].sum()
            total_expenses = transactions_df[transactions_df['type'] == 'expense']['amount'].sum()
            current_balance = total_income - total_expenses

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<p class="metric-label">Total Income</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="metric-value income">€{total_income:,.2f}</p>', unsafe_allow_html=True)
            with col2:
                st.markdown('<p class="metric-label">Total Expenses</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="metric-value expense">€{total_expenses:,.2f}</p>', unsafe_allow_html=True)
            with col3:
                st.markdown('<p class="metric-label">Current Balance</p>', unsafe_allow_html=True)
                balance_color_class = "income" if current_balance >= 0 else "expense"
                st.markdown(f'<p class="metric-value {balance_color_class}">€{current_balance:,.2f}</p>', unsafe_allow_html=True)
        else:
            st.info("No transaction data available.")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- Budget Status Section ---
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Monthly Budget Status")

        if budgets and not transactions_df.empty:
            now = datetime.now()
            # Ensure 'date' column is datetime
            transactions_df['date'] = pd.to_datetime(transactions_df['date'])
            
            current_month_expenses = transactions_df[
                (transactions_df['type'] == 'expense') &
                (transactions_df['date'].dt.month == now.month) &
                (transactions_df['date'].dt.year == now.year)
            ]
            
            spending_by_category = current_month_expenses.groupby('category')['amount'].sum()

            for category, budget_amount in budgets.items():
                spent_amount = spending_by_category.get(category, 0)
                percentage = (spent_amount / budget_amount) * 100 if budget_amount > 0 else 0

                st.markdown(f"**{category}**")
                col1, col2 = st.columns([3, 1])
                with col1:
                    if percentage >= 100:
                        color = "red"
                    elif percentage >= 70:
                        color = "orange"
                    else:
                        color = "green"
                    
                    st.progress(int(min(percentage, 100)))

                with col2:
                    st.markdown(f"€{spent_amount:,.2f} / €{budget_amount:,.2f}")

        elif not budgets:
            st.info("No budgets set. Please set budgets in the CLI application.")
        else:
            st.info("No expenses this month to compare with budgets.")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- Recent Transactions Table ---
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Recent Transactions")

        if not transactions_df.empty:
            # Ensure 'date' column is datetime before sorting
            transactions_df['date'] = pd.to_datetime(transactions_df['date'])
            recent_transactions = transactions_df.sort_values(by='date', ascending=False).head(10)
            
            def get_color(trans_type):
                return "red" if trans_type == "expense" else "green"

            for index, row in recent_transactions.iterrows():
                cols = st.columns([1,1,1,2,1])
                cols[0].write(row['date'].strftime('%Y-%m-%d'))
                cols[1].write(row['type'].capitalize())
                cols[2].write(row['category'])
                cols[3].write(row['description'])
                
                amount_color = get_color(row['type'])
                cols[4].markdown(f"<span style='color:{amount_color};'>€{row['amount']:,.2f}</span>", unsafe_allow_html=True)
        else:
            st.info("No transactions to display.")
        st.markdown('</div>', unsafe_allow_html=True)

    elif selection == "Add Income":
        st.title("Add New Income")
        with st.form("income_form"):
            date = st.date_input("Date", datetime.now())
            amount = st.number_input("Amount", min_value=0.01, format="%.2f")
            category = st.selectbox("Category", INCOME_CATEGORIES)
            description = st.text_input("Description")
            submitted = st.form_submit_button("Add Income")

            if submitted:
                if amount <= 0:
                    st.error("Amount must be positive.")
                elif ',' in description:
                    st.error("Description cannot contain commas.")
                else:
                    write_transaction(date, "income", category, description, amount)
                    st.success("Income added successfully!")
                    st.rerun()

    elif selection == "Add Expense":
        st.title("Add New Expense")
        with st.form("expense_form"):
            date = st.date_input("Date", datetime.now())
            amount = st.number_input("Amount", min_value=0.01, format="%.2f")
            category = st.selectbox("Category", EXPENSE_CATEGORIES)
            description = st.text_input("Description")
            submitted = st.form_submit_button("Add Expense")

            if submitted:
                if amount <= 0:
                    st.error("Amount must be positive.")
                elif ',' in description:
                    st.error("Description cannot contain commas.")
                else:
                    write_transaction(date, "expense", category, description, amount)
                    st.success("Expense added successfully!")
                    st.rerun()

    elif selection == "Set Budget":
        st.title("Set Monthly Budget")
        budgets = load_budgets()
        
        with st.form("budget_form"):
            category = st.selectbox("Category", EXPENSE_CATEGORIES)
            amount = st.number_input("Amount", min_value=0.01, format="%.2f")
            submitted = st.form_submit_button("Set Budget")

            if submitted:
                if amount <= 0:
                    st.error("Amount must be positive.")
                else:
                    budgets[category] = amount
                    write_budgets(budgets)
                    st.success(f"Budget for {category} set to €{amount:,.2f}")
                    st.rerun()

        st.subheader("Current Budgets")
        if budgets:
            st.table(pd.DataFrame(list(budgets.items()), columns=['Category', 'Amount']))
        else:
            st.info("No budgets set yet.")

    elif selection == "Smart Assistant":
        st.title("Smart Financial Assistant")
        transactions_df = load_transactions()
        budgets = load_budgets()
        
        # The get_recommendations function in the smart_assistant module expects amounts in cents
        # but our load_transactions function converts them to dollars.
        # We need to pass the amounts in cents.
        transactions_for_assistant = transactions_df.copy()
        transactions_for_assistant['amount'] = (transactions_for_assistant['amount'] * 100).astype(int)
        
        # The get_recommendations function expects a dict of transactions
        transactions_list = transactions_for_assistant.to_dict('records')
        
        recommendations = smart_assistant.get_recommendations(transactions_list, budgets)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Personalized Recommendations")
        if recommendations:
            for rec in recommendations:
                st.info(rec)
        else:
            st.success("Your finances are looking good! No specific recommendations at this time.")
        st.markdown('</div>', unsafe_allow_html=True)

    elif selection == "Analytics":
        st.title("Financial Analytics")
        transactions_df = load_transactions()
        
        tab1, tab2, tab3, tab4 = st.tabs(["Spending", "Income", "Savings", "Financial Health"])

        with tab1:
            st.subheader("Spending Analysis")
            if not transactions_df.empty:
                now = datetime.now()
                current_month_start = now.replace(day=1)
                
                # Ensure 'date' column is datetime
                transactions_df['date'] = pd.to_datetime(transactions_df['date'])

                expenses_df = transactions_df[
                    (transactions_df['type'] == 'expense') &
                    (transactions_df['date'].dt.to_pydatetime() >= current_month_start)
                ]

                if not expenses_df.empty:
                    spending_by_category = expenses_df.groupby('category')['amount'].sum()
                    
                    # Pie chart
                    fig, ax = plt.subplots()
                    ax.pie(spending_by_category, labels=spending_by_category.index, autopct='%1.1f%%', startangle=90)
                    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                    st.pyplot(fig)

                    # Top 3 categories
                    top_categories = spending_by_category.nlargest(3)
                    st.subheader("Top 3 Spending Categories")
                    st.table(top_categories)

                    # Average daily expense
                    days_in_month = (now - current_month_start).days + 1
                    avg_daily_expense = expenses_df['amount'].sum() / days_in_month
                    st.metric(label="Average Daily Expense", value=f"€{avg_daily_expense:,.2f}")

                else:
                    st.info("No spending data for the current month.")
            else:
                st.info("No transaction data available.")
        
        with tab2:
            st.subheader("Income Analysis")
            if not transactions_df.empty:
                now = datetime.now()
                current_month_start = now.replace(day=1)
                
                # Ensure 'date' column is datetime
                transactions_df['date'] = pd.to_datetime(transactions_df['date'])

                income_df = transactions_df[
                    (transactions_df['type'] == 'income') &
                    (transactions_df['date'].dt.to_pydatetime() >= current_month_start)
                ]

                if not income_df.empty:
                    income_by_source = income_df.groupby('category')['amount'].sum()
                    
                    st.subheader("Income by Source")
                    st.table(income_by_source)

                    total_income = income_df['amount'].sum()
                    st.metric(label="Total Income this Month", value=f"€{total_income:,.2f}")
                else:
                    st.info("No income data for the current month.")
            else:
                st.info("No transaction data available.")

        with tab3:
            st.subheader("Savings Analysis")
            if not transactions_df.empty:
                now = datetime.now()
                current_month_start = now.replace(day=1)
                
                # Ensure 'date' column is datetime
                transactions_df['date'] = pd.to_datetime(transactions_df['date'])

                monthly_transactions = transactions_df[
                    transactions_df['date'].dt.to_pydatetime() >= current_month_start
                ]
                
                total_income = monthly_transactions[monthly_transactions['type'] == 'income']['amount'].sum()
                total_expenses = monthly_transactions[monthly_transactions['type'] == 'expense']['amount'].sum()

                if total_income > 0:
                    savings = total_income - total_expenses
                    savings_rate = (savings / total_income) * 100
                    
                    st.metric(label="Total Income this Month", value=f"€{total_income:,.2f}")
                    st.metric(label="Total Expenses this Month", value=f"€{total_expenses:,.2f}")
                    st.metric(label="Savings this Month", value=f"€{savings:,.2f}")
                    st.metric(label="Savings Rate", value=f"{savings_rate:.2f}%")
                else:
                    st.info("No income data for the current month to calculate savings.")
            else:
                st.info("No transaction data available.")

        with tab4:
            st.subheader("Financial Health Score")
            if not transactions_df.empty:
                now = datetime.now()
                current_month_start = now.replace(day=1)
                
                # Ensure 'date' column is datetime
                transactions_df['date'] = pd.to_datetime(transactions_df['date'])

                monthly_transactions_df = transactions_df[
                    transactions_df['date'].dt.to_pydatetime() >= current_month_start
                ]
                
                # The _calculate_budget_adherence_score expects a list of dicts with amounts in cents
                monthly_transactions_list = monthly_transactions_df.copy()
                monthly_transactions_list['amount'] = (monthly_transactions_list['amount'] * 100).astype(int)
                monthly_transactions_list = monthly_transactions_list.to_dict('records')

                total_income = monthly_transactions_df[monthly_transactions_df['type'] == 'income']['amount'].sum()
                total_expenses = monthly_transactions_df[monthly_transactions_df['type'] == 'expense']['amount'].sum()
                
                budgets = load_budgets()

                savings_rate_score = _calculate_savings_rate_score(total_income, total_expenses)
                budget_adherence_score = _calculate_budget_adherence_score(monthly_transactions_list, budgets)
                income_expense_score = _calculate_income_expense_score(total_income, total_expenses)

                final_score = savings_rate_score + budget_adherence_score + income_expense_score

                st.metric(label="Financial Health Score", value=f"{final_score:.0f} / 100")
                st.progress(int(final_score))
                
                interpretation = _interpret_score(final_score)
                st.write(interpretation)

                st.subheader("Score Breakdown")
                st.markdown(f"- **Savings Rate Score:** {savings_rate_score:.0f} / 40")
                st.markdown(f"- **Budget Adherence Score:** {budget_adherence_score:.0f} / 35")
                st.markdown(f"- **Income vs. Expense Score:** {income_expense_score:.0f} / 25")
            else:
                st.info("No transaction data available.")
    
    elif selection == "Data Management":
        st.title("Data Management")

        st.subheader("Export Data")
        if st.button("Export to CSV"):
            data_management.export_data_to_csv()
            st.success("Data exported to CSV successfully!")
            with open("transactions_export.csv", "r") as f:
                st.download_button("Download Transactions CSV", f, "transactions_export.csv")
            with open("budgets_export.csv", "r") as f:
                st.download_button("Download Budgets CSV", f, "budgets_export.csv")

        if st.button("Export to JSON"):
            data_management.export_data_to_json()
            st.success("Data exported to JSON successfully!")
            with open("all_data_export.json", "r") as f:
                st.download_button("Download JSON Export", f, "all_data_export.json")

        st.subheader("Backup")
        if st.button("Create Backup"):
            data_management.create_backup()
            st.success("Backup created successfully!")



if __name__ == "__main__":
    main()