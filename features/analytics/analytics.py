from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from datetime import datetime, timedelta

# Import the helper function from the transactions module
from features.transactions import transactions as transaction_features
from features.budgets import budgets as budget_features
from features.smart_assistant import smart_assistant

# Initialize Rich Console
console = Console()

# --- Core Functions ---

def analyze_spending():
    """Analyzes spending patterns for the current month."""
    console.print("\n[bold cyan]-- Spending Analysis --[/bold cyan]")

    all_transactions = transaction_features._read_transactions()
    now = datetime.now()
    current_month_start = now.replace(day=1)

    # Filter for expenses in the current month
    expenses = [
        t for t in all_transactions 
        if t['type'] == 'expense' and t['date'] >= current_month_start.date()
    ]

    if not expenses:
        console.print("[yellow]No expenses found for the current month.[/yellow]")
        return

    # --- Calculations ---
    spending_by_category = {}
    for e in expenses:
        spending_by_category[e['category']] = spending_by_category.get(e['category'], 0) + e['amount']
    
    total_spent = sum(spending_by_category.values())
    
    # Top 3 categories
    top_categories = sorted(spending_by_category.items(), key=lambda item: item[1], reverse=True)[:3]
    
    # Average daily expense
    days_in_month = (now - current_month_start).days + 1
    avg_daily_expense = total_spent / days_in_month

    # --- Display ---
    _display_pie_chart(spending_by_category, total_spent)
    
    console.print("\n[bold]Top 3 Spending Categories:[/bold]")
    for category, amount in top_categories:
        console.print(f"- {category}: {amount/100:.2f}")

    console.print(f"\n[bold]Average Daily Expense:[/bold] {avg_daily_expense/100:.2f}")

def analyze_income():
    """Analyzes income patterns for the current month."""
    console.print("\n[bold cyan]-- Income Analysis --[/bold cyan]")

    all_transactions = transaction_features._read_transactions()
    now = datetime.now()
    current_month_start = now.replace(day=1)

    # Filter for income in the current month
    income_transactions = [
        t for t in all_transactions 
        if t['type'] == 'income' and t['date'] >= current_month_start.date()
    ]

    if not income_transactions:
        console.print("[yellow]No income found for the current month.[/yellow]")
        return

    # --- Calculations ---
    income_by_source = {}
    for t in income_transactions:
        income_by_source[t['category']] = income_by_source.get(t['category'], 0) + t['amount']
    
    total_income = sum(income_by_source.values())

    # --- Display ---
    console.print("\n[bold]Income by Source:[/bold]")
    for source, amount in income_by_source.items():
        console.print(f"- {source}: {amount/100:.2f}")

    console.print(f"\n[bold]Total Income this month:[/bold] [green]{total_income/100:.2f}[/green]")

def analyze_savings():
    """Analyzes savings for the current month."""
    console.print("\n[bold cyan]-- Savings Analysis --[/bold cyan]")

    all_transactions = transaction_features._read_transactions()
    now = datetime.now()
    current_month_start = now.replace(day=1)

    # Filter for income and expenses in the current month
    monthly_transactions = [
        t for t in all_transactions if t['date'] >= current_month_start.date()
    ]

    total_income = sum(t['amount'] for t in monthly_transactions if t['type'] == 'income')
    total_expenses = sum(t['amount'] for t in monthly_transactions if t['type'] == 'expense')

    if total_income == 0:
        console.print("[yellow]No income recorded for this month. Savings cannot be calculated.[/yellow]")
        return

    savings = total_income - total_expenses
    savings_rate = (savings / total_income) * 100 if total_income > 0 else 0
    
    savings_color = "green" if savings >= 0 else "red"

    # --- Display ---
    savings_text = (
        f"Total Income:   [green]{total_income/100:.2f}[/green]\n"
        f"Total Expenses: [red]{total_expenses/100:.2f}[/red]\n"
        f"---------------------------\n"
        f"Saved this month: [bold {savings_color}]{savings/100:.2f}[/bold {savings_color}]\n"
        f"Savings Rate:     [bold {savings_color}]{savings_rate:.2f}%[/bold {savings_color}]"
    )

    panel = Panel(
        savings_text,
        title="[bold]Monthly Savings Summary[/bold]",
        border_style="blue",
        expand=False
    )
    console.print(panel)

def financial_health_score():
    """Calculates and displays a financial health score."""
    console.print("\n[bold cyan]-- Financial Health Score --[/bold cyan]")

    all_transactions = transaction_features._read_transactions()
    budgets = budget_features._read_budgets()
    now = datetime.now()
    current_month_start = now.replace(day=1)

    monthly_transactions = [
        t for t in all_transactions if t['date'] >= current_month_start.date()
    ]
    
    total_income = sum(t['amount'] for t in monthly_transactions if t['type'] == 'income')
    total_expenses = sum(t['amount'] for t in monthly_transactions if t['type'] == 'expense')

    # --- Calculate individual scores ---
    savings_rate_score = _calculate_savings_rate_score(total_income, total_expenses)
    budget_adherence_score = _calculate_budget_adherence_score(monthly_transactions, budgets)
    income_expense_score = _calculate_income_expense_score(total_income, total_expenses)

    # --- Final Score ---
    final_score = savings_rate_score + budget_adherence_score + income_expense_score
    
    score_color = "green" if final_score >= 75 else "yellow" if final_score >= 50 else "red"

    # --- Display ---
    score_text = (
        f"Savings Rate Score:       {savings_rate_score:.0f} / 40\n"
        f"Budget Adherence Score:   {budget_adherence_score:.0f} / 35\n"
        f"Income vs. Expense Score: {income_expense_score:.0f} / 25\n"
        f"-----------------------------------\n"
        f"Overall Score: [bold {score_color}]{final_score:.0f} / 100[/bold {score_color}]"
    )

    panel = Panel(
        score_text,
        title="[bold]Financial Health Breakdown[/bold]",
        border_style="blue"
    )
    console.print(panel)
    _interpret_score(final_score)

def show_financial_summary_and_recommendations():
    """Shows a summary and recommendations from the Smart Financial Assistant."""
    console.print("\n[bold cyan]-- Financial Summary & Recommendations --[/bold cyan]")
    
    all_transactions = transaction_features._read_transactions()
    all_budgets = budget_features._read_budgets()

    recommendations = smart_assistant.get_recommendations(all_transactions, all_budgets)

    if not recommendations:
        console.print("[green]Your finances are looking good! No specific recommendations at this time.[/green]")
        return

    rec_panel = "\n".join([f"• [yellow]{rec}[/yellow]" for rec in recommendations])
    
    panel = Panel(
        rec_panel,
        title="[bold]Personalized Recommendations[/bold]",
        border_style="blue",
        expand=False
    )
    console.print(panel)

def generate_monthly_report():
    """Generates a comprehensive monthly financial report."""
    console.print("\n[bold magenta]-- Monthly Financial Report --[/bold magenta]")
    now = datetime.now()
    
    console.print(f"\n[bold]Report for: {now.strftime('%B %Y')}[/bold]")
    
    # --- Use existing functions to display sections of the report ---
    analyze_income()
    analyze_spending()
    analyze_savings()
    show_financial_summary_and_recommendations()
    
    console.print("\n[bold green]End of Report.[/bold green]")


# --- Helper Functions ---

def _display_pie_chart(spending_by_category, total_spent):
    """Displays an ASCII pie chart."""
    console.print("\n[bold]Spending by Category:[/bold]")
    if total_spent == 0:
        return

    sorted_categories = sorted(spending_by_category.items(), key=lambda item: item[1], reverse=True)

    for category, amount in sorted_categories:
        percentage = (amount / total_spent) * 100
        bar_length = int(percentage / 2)
        bar = '█' * bar_length
        console.print(f"{category:<15} {bar} {percentage:.1f}%")

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
        console.print("[bold green]Excellent! Your finances are in great shape. Keep up the good work![/bold green]")
    elif score >= 50:
        console.print("[bold yellow]Good. There's room for improvement, but you're on the right track.[/bold yellow]")
    else:
        console.print("[bold red]Needs Attention. Your finances require careful review. Focus on budgeting and saving.[/bold red]")
