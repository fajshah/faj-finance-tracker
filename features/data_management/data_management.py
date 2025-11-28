# features/data_management/data_management.py

import os
import shutil
import datetime
import json
import csv
import questionary

from rich.console import Console
from rich.table import Table

console = Console()

DATABASE_DIR = "database"
BACKUP_DIR = os.path.join(DATABASE_DIR, "backups")
TRANSACTIONS_FILE = os.path.join(DATABASE_DIR, "transactions.txt")
BUDGETS_FILE = os.path.join(DATABASE_DIR, "budgets.txt")

def export_data_to_csv():
    """Exports transaction and budget data to CSV files."""
    console.print("[bold cyan]Exporting data to CSV...[/bold cyan]")
    # Export transactions to CSV
    transactions_csv_path = "transactions_export.csv"
    try:
        with open(TRANSACTIONS_FILE, 'r') as infile, open(transactions_csv_path, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["Date", "Type", "Category/Source", "Description", "Amount"]) # Header
            for line in infile:
                parts = line.strip().rsplit(',', 4)
                if len(parts) == 5:
                    writer.writerow(parts)
                else: # Handle cases where description might be empty
                    parts = line.strip().rsplit(',', 3)
                    if len(parts) == 4:
                        writer.writerow(parts[:3] + [""] + parts[3:])
        console.print(f"[green]Transactions exported to {transactions_csv_path}[/green]")
    except FileNotFoundError:
        console.print(f"[yellow]'{TRANSACTIONS_FILE}' not found. No transactions to export.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error exporting transactions: {e}[/red]")

    # Export budgets to CSV
    budgets_csv_path = "budgets_export.csv"
    try:
        with open(BUDGETS_FILE, 'r') as infile, open(budgets_csv_path, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["Category", "Amount"]) # Header
            for line in infile:
                parts = line.strip().split(',', 1) # Split by comma, max 1 split
                writer.writerow(parts)
        console.print(f"[green]Budgets exported to {budgets_csv_path}[/green]")
    except FileNotFoundError:
        console.print(f"[yellow]'{BUDGETS_FILE}' not found. No budgets to export.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error exporting budgets: {e}[/red]")
    console.print("[bold green]Data exported to CSV successfully![/bold green]")

def export_data_to_json():
    """Exports all data to a single JSON file."""
    console.print("[bold cyan]Exporting data to JSON...[/bold cyan]")
    data = {"transactions": [], "budgets": []}
    json_export_path = "all_data_export.json"

    # Read transactions
    try:
        with open(TRANSACTIONS_FILE, 'r') as infile:
            for line in infile:
                parts = line.strip().rsplit(',', 4)
                if len(parts) == 5:
                    data["transactions"].append({
                        "date": parts[0],
                        "type": parts[1],
                        "category_source": parts[2],
                        "description": parts[3],
                        "amount": int(parts[4])
                    })
                else: # Handle cases where description might be empty
                    parts = line.strip().rsplit(',', 3)
                    if len(parts) == 4:
                        data["transactions"].append({
                            "date": parts[0],
                            "type": parts[1],
                            "category_source": parts[2],
                            "description": "",
                            "amount": int(parts[3])
                        })
    except FileNotFoundError:
        console.print(f"[yellow]'{TRANSACTIONS_FILE}' not found. No transactions to export.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error reading transactions for JSON export: {e}[/red]")

    # Read budgets
    try:
        with open(BUDGETS_FILE, 'r') as infile:
            for line in infile:
                parts = line.strip().split(',', 1)
                if len(parts) == 2:
                    data["budgets"].append({
                        "category": parts[0],
                        "amount": int(parts[1])
                    })
    except FileNotFoundError:
        console.print(f"[yellow]'{BUDGETS_FILE}' not found. No budgets to export.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error reading budgets for JSON export: {e}[/red]")

    # Write to JSON file
    try:
        with open(json_export_path, 'w') as outfile:
            json.dump(data, outfile, indent=4)
        console.print(f"[green]All data exported to {json_export_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error writing JSON export: {e}[/red]")
    console.print("[bold green]Data exported to JSON successfully![/bold green]")

def create_backup():
    """Creates a timestamped backup of the current database."""
    console.print("[bold cyan]Creating backup...[/bold cyan]")
    # Ensure backup directory exists
    os.makedirs(BACKUP_DIR, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    backup_name = f"backup_{timestamp}"
    backup_path = os.path.join(BACKUP_DIR, backup_name)

    # Create a zip archive of the database files
    shutil.make_archive(backup_path, 'zip', root_dir=DATABASE_DIR)
    console.print(f"[bold green]Backup created: {backup_path}.zip[/bold green]")

def restore_backup():
    """Restores data from a selected backup."""
    console.print("[bold cyan]Restoring backup...[/bold cyan]")
    # Ensure backup directory exists
    if not os.path.exists(BACKUP_DIR):
        console.print("[yellow]No backups found.[/yellow]")
        return

    backups = [f for f in os.listdir(BACKUP_DIR) if f.startswith("backup_") and f.endswith(".zip")]
    if not backups:
        console.print("[yellow]No backups found.[/yellow]")
        return

    backup_choices = {os.path.basename(f).replace(".zip", ""): os.path.join(BACKUP_DIR, f) for f in backups}

    selected_backup_name = questionary.select(
        "Select a backup to restore:",
        choices=list(backup_choices.keys())
    ).ask()

    if not selected_backup_name:
        console.print("[yellow]Backup restoration cancelled.[/yellow]")
        return

    selected_backup_path = backup_choices[selected_backup_name]

    try:
        # Clear existing database files before restoring
        if os.path.exists(TRANSACTIONS_FILE):
            os.remove(TRANSACTIONS_FILE)
        if os.path.exists(BUDGETS_FILE):
            os.remove(BUDGETS_FILE)

        # Extract the backup
        shutil.unpack_archive(selected_backup_path, DATABASE_DIR, 'zip')
        console.print(f"[bold green]Backup '{selected_backup_name}' restored successfully![/bold green]")
    except Exception as e:
        console.print(f"[red]Error restoring backup: {e}[/red]")
    console.print("[bold green]Backup restored successfully![/bold green]")

def main():
    """Main function for data management features."""
    console.print("[bold magenta]Data Management Options:[/bold magenta]")
    while True:
        choice = questionary.select(
            "Select a data management option:",
            choices=[
                "Export data to CSV",
                "Export data to JSON",
                "Create backup",
                "Restore backup",
                "Back to Main Menu"
            ]
        ).ask()

        if choice == "Export data to CSV":
            export_data_to_csv()
        elif choice == "Export data to JSON":
            export_data_to_json()
        elif choice == "Create backup":
            create_backup()
        elif choice == "Restore backup":
            restore_backup()
        elif choice == "Back to Main Menu" or choice is None:
            break

if __name__ == "__main__":
    main()
