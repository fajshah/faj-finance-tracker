import questionary
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime
from features.smart_assistant.smart_assistant import detect_unusual_spending

# Initialize Rich Console
console = Console()

# --- Categories ---
EXPENSE_CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"]
INCOME_CATEGORIES = ["Salary", "Freelance", "Business", "Investment", "Gift", "Other"]

# --- File Path ---
TRANSACTIONS_FILE = "database/transactions.txt"

# --- Helper Functions ---

def _read_transactions():
    """Reads all transactions from the file."""
    transactions = []
    try:
        with open(TRANSACTIONS_FILE, "r") as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    try:
                        date_str, type, category, description, amount_cents = line.strip().split(',')
                        transactions.append({
                            "date": datetime.strptime(date_str, "%Y-%m-%d").date(),
                            "type": type,
                            "category": category,
                            "description": description,
                            "amount": int(amount_cents)
                        })
                    except ValueError as e:
                        console.print(
                            f"[bold yellow]Warning: Skipping malformed transaction on line {line_num} "
                            f"in {TRANSACTIONS_FILE}: {line.strip()} ({e})[/bold yellow]"
                        )
    except FileNotFoundError:
        pass  # File might not exist yet, return empty list
    return sorted(transactions, key=lambda t: t['date'], reverse=True)

# --- Core Functions ---

def add_expense():
    """Adds a new expense transaction."""
    console.print("\n[bold cyan]-- Add Expense --[/bold cyan]")
    try:
        amount_str = questionary.text("Enter amount (e.g., 12.50):").ask()
        amount = int(float(amount_str) * 100)  # Store as cents
        if amount <= 0:
            console.print("[bold red]Error: Amount must be positive.[/bold red]")
            return

        category = questionary.select(
            "Select category:",
            choices=EXPENSE_CATEGORIES
        ).ask()

        description = questionary.text("Enter description:").ask()

        date_str = questionary.text(
            "Enter date (YYYY-MM-DD, press Enter for today):"
        ).ask()
        date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.now().date()

        with open(TRANSACTIONS_FILE, "a") as f:
            f.write(f"{date},{'expense'},{category},{description},{amount}\n")

        console.print("\n[bold green]Expense added successfully![/bold green]")
        
        # Check for unusual spending
        all_transactions = _read_transactions()
        new_transaction = {
            "date": date,
            "type": "expense",
            "category": category,
            "description": description,
            "amount": amount
        }
        if detect_unusual_spending(all_transactions, new_transaction):
            console.print(
                f"[bold yellow]Warning: This spending is unusually high for the '{category}' category.[/bold yellow]"
            )

    except (ValueError, TypeError):
        console.print("[bold red]Invalid amount. Please enter a valid number.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An error occurred: {e}[/bold red]")


def add_income():
    """Adds a new income transaction."""
    console.print("\n[bold cyan]-- Add Income --[/bold cyan]")
    try:
        amount_str = questionary.text("Enter amount (e.g., 500.00):").ask()
        amount = int(float(amount_str) * 100)  # Store as cents
        if amount <= 0:
            console.print("[bold red]Error: Amount must be positive.[/bold red]")
            return

        source = questionary.select(
            "Select source:",
            choices=INCOME_CATEGORIES
        ).ask()

        description = questionary.text("Enter description:").ask()

        date_str = questionary.text(
            "Enter date (YYYY-MM-DD, press Enter for today):"
        ).ask()
        date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.now().date()

        with open(TRANSACTIONS_FILE, "a") as f:
            f.write(f"{date},{'income'},{source},{description},{amount}\n")

        console.print("\n[bold green]Income added successfully![/bold green]")

    except (ValueError, TypeError):
        console.print("[bold red]Invalid amount. Please enter a valid number.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An error occurred: {e}[/bold red]")

def list_transactions():
    """Lists all transactions in a formatted table."""
    console.print("\n[bold cyan]-- All Transactions --[/bold cyan]")
    transactions = _read_transactions()

    if not transactions:
        console.print("[yellow]No transactions found.[/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Date", style="dim")
    table.add_column("Type")
    table.add_column("Category/Source")
    table.add_column("Description", width=40)
    table.add_column("Amount", justify="right")

    for t in transactions:
        amount_str = f"{t['amount'] / 100:.2f}"
        color = "red" if t['type'] == 'expense' else "green"
        
        table.add_row(
            str(t['date']),
            f"[{color}]{t['type'].capitalize()}[/{color}]",
            t['category'],
            t['description'],
            f"[{color}]{amount_str}[/{color}]"
        )
    
    console.print(table)


def show_balance():
    """Calculates and displays the current financial balance."""
    console.print("\n[bold cyan]-- Current Balance --[/bold cyan]")
    transactions = _read_transactions()

    total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
    total_expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')
    balance = total_income - total_expenses

    # Format for display
    income_str = f"{total_income / 100:.2f}"
    expenses_str = f"{total_expenses / 100:.2f}"
    balance_str = f"{balance / 100:.2f}"
    balance_color = "green" if balance >= 0 else "red"

    # Create content for the panel
    balance_text = (
        f"[green]Total Income:  {income_str}[/green]\n"
        f"[red]Total Expenses: {expenses_str}[/red]\n"
        f"---------------------------\n"
        f"[bold {balance_color}]Current Balance: {balance_str}[/bold {balance_color}]"
    )

    panel = Panel(
        balance_text,
        title="[bold]Financial Summary[/bold]",
        border_style="blue",
        expand=False
    )
    
    console.print(panel)
