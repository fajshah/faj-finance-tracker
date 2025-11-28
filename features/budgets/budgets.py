import questionary
from rich.console import Console
from rich.table import Table
from rich.progress_bar import ProgressBar
from datetime import datetime

# Import the helper function from the transactions module
from features.transactions import transactions as transaction_features

# Initialize Rich Console
console = Console()

# --- Categories ---
BUDGET_CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"]

# --- File Path ---
BUDGETS_FILE = "database/budgets.txt"

# --- Core Functions ---

def set_budget():
    """Sets a monthly budget for a specific category."""
    console.print("\n[bold cyan]-- Set Monthly Budget --[/bold cyan]")
    try:
        category = questionary.select(
            "Select category to budget:",
            choices=BUDGET_CATEGORIES
        ).ask()

        amount_str = questionary.text("Enter monthly budget amount:").ask()
        amount = int(float(amount_str) * 100)  # Store as cents

        if amount <= 0:
            console.print("[bold red]Error: Budget amount must be positive.[/bold red]")
            return

        budgets = _read_budgets()
        budgets[category] = amount
        _write_budgets(budgets)

        console.print(f"\n[bold green]Budget for '{category}' set to {amount/100:.2f} successfully![/bold green]")

    except (ValueError, TypeError):
        console.print("[bold red]Invalid amount. Please enter a valid number.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An error occurred: {e}[/bold red]")

def view_budget():
    """Displays the budget vs. actual spending for the current month."""
    console.print("\n[bold cyan]-- Monthly Budget Status --[/bold cyan]")
    
    budgets = _read_budgets()
    if not budgets:
        console.print("[yellow]No budgets set. Please use 'Set Budget' first.[/yellow]")
        return

    all_transactions = transaction_features._read_transactions()
    now = datetime.now()
    
    # Calculate spending per category for the current month
    monthly_spending = {category: 0 for category in budgets}
    for t in all_transactions:
        if t['type'] == 'expense' and t['date'].month == now.month and t['date'].year == now.year:
            if t['category'] in monthly_spending:
                monthly_spending[t['category']] += t['amount']

    # Create and display the budget table
    table = Table(title=f"Budget for {now.strftime('%B %Y')}", header_style="bold magenta")
    table.add_column("Category", style="cyan")
    table.add_column("Budget", justify="right")
    table.add_column("Spent", justify="right")
    table.add_column("Remaining", justify="right")
    table.add_column("Utilization", justify="center", width=20)
    table.add_column("Status")

    for category, budget_amount in budgets.items():
        spent_amount = monthly_spending.get(category, 0)
        remaining = budget_amount - spent_amount
        utilization = (spent_amount / budget_amount) * 100 if budget_amount > 0 else 0

        # Determine status and color
        if utilization > 100:
            status, color = "Over", "red"
        elif utilization > 70:
            status, color = "Warning", "yellow"
        else:
            status, color = "OK", "green"

        # Create progress bar
        progress = ProgressBar(total=100, completed=min(utilization, 100), width=15, complete_style=color)

        table.add_row(
            category,
            f"{budget_amount / 100:.2f}",
            f"[{color}]{spent_amount / 100:.2f}[/{color}]",
            f"{remaining / 100:.2f}",
            progress,
            f"[{color}]{status}[/{color}]"
        )

    console.print(table)


# --- Helper Functions ---

def _read_budgets():
    """Reads all budgets from the file."""
    budgets = {}
    try:
        with open(BUDGETS_FILE, "r") as f:
            for line in f:
                if line.strip():
                    category, amount_cents = line.strip().split(',')
                    budgets[category] = int(amount_cents)
    except FileNotFoundError:
        pass
    return budgets

def _write_budgets(budgets):
    """Writes all budgets to the file, overwriting it."""
    with open(BUDGETS_FILE, "w") as f:
        for category, amount in budgets.items():
            f.write(f"{category},{amount}\n")