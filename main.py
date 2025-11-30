import questionary
from rich.console import Console
from rich.panel import Panel
import os
# Import features
from features.transactions import transactions
from features.budgets import budgets
from features.analytics import analytics
from features.smart_assistant import smart_assistant
from features.data_management import data_management

# Initialize Rich Console
console = Console()

def show_smart_assistant():
    """Shows recommendations from the Smart Financial Assistant."""
    console.print("\n[bold cyan]-- Smart Financial Assistant --[/bold cyan]")
    
    all_transactions = transactions._read_transactions()
    all_budgets = budgets._read_budgets()

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


def main():
    """Main function to run the finance tracker CLI."""
    console.print("\n[bold magenta]Welcome to your Personal Finance Tracker![/bold magenta]")
    console.print("What would you like to do today?")

    while True:
        choice = questionary.select(
            "Main Menu:",
            choices=[
                "Add Expense",
                "Add Income",
                "List Transactions",
                "Show Balance",
                "Set Budget",
                "View Budgets",
                "--- Analytics ---",
                "Spending Analysis",
                "Income Analysis",
                "Savings Analysis",
                "Financial Health Score",
                "Financial Summary & Recommendations",
                "Generate Monthly Report",
                "--- Smart Assistant ---",
                "Smart Financial Assistant",
                "--- Data Management ---",
                "Data Management",
                "---",
                "Exit"
            ]
        ).ask()

        if choice == "Add Expense":
            transactions.add_expense()
        elif choice == "Add Income":
            transactions.add_income()
        elif choice == "List Transactions":
            transactions.list_transactions()
        elif choice == "Show Balance":
            transactions.show_balance()
        elif choice == "Set Budget":
            budgets.set_budget()
        elif choice == "View Budgets":
            budgets.view_budget()
        elif choice == "Spending Analysis":
            analytics.analyze_spending()
        elif choice == "Income Analysis":
            analytics.analyze_income()
        elif choice == "Savings Analysis":
            analytics.analyze_savings()
        elif choice == "Financial Health Score":
            analytics.financial_health_score()
        elif choice == "Financial Summary & Recommendations":
            analytics.show_financial_summary_and_recommendations()
        elif choice == "Generate Monthly Report":
            analytics.generate_monthly_report()
        elif choice == "Smart Financial Assistant":
            show_smart_assistant()
        elif choice == "Data Management":
            data_management.main()
        elif choice == "Exit" or choice is None:
            console.print("\n[bold]Goodbye![/bold]\n")
            break

if __name__ == "__main__":
    main()