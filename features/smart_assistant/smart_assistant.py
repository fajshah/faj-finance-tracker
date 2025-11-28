# features/smart_assistant/smart_assistant.py

def detect_unusual_spending(transactions, new_transaction):
    """
    Detects if a new transaction is unusually high for its category.
    """
    category = new_transaction['category']
    amount = new_transaction['amount']

    # Get all transactions in the same category
    category_transactions = [
        t['amount'] for t in transactions if t['category'] == category
    ]

    if not category_transactions:
        return False  # Not enough data to compare

    # Calculate the average spending for the category
    average_spending = sum(category_transactions) / len(category_transactions)

    # Define a threshold for "unusual"
    # For simplicity, we'll say anything 2x the average is unusual.
    # A more robust solution might use standard deviations.
    unusual_threshold = average_spending * 2

    if amount > unusual_threshold:
        return True
    
    return False

def get_recommendations(transactions, budgets):
    """
    Generates personalized financial recommendations.
    """
    recommendations = []

    # Recommendation 1: Identify categories with high spending but no budget
    spending_by_category = {}
    for t in transactions:
        if t['type'] == 'expense':
            category = t['category']
            amount = t['amount']
            spending_by_category[category] = spending_by_category.get(category, 0) + amount
    
    budgeted_categories = set(budgets.keys())

    for category, total_spent in spending_by_category.items():
        if category not in budgeted_categories and total_spent > 20000: # Example threshold: 200.00
            recommendations.append(
                f"You've spent a significant amount in '{category}' without a budget. "
                f"Consider setting one to manage your spending."
            )

    # Recommendation 2: Savings opportunities
    if spending_by_category:
        highest_spending_category = max(spending_by_category, key=spending_by_category.get)
        recommendations.append(
            f"Your highest spending category is '{highest_spending_category}'. "
            f"Reviewing your spending here could be a good way to save money."
        )

    return recommendations
