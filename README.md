# Expense Tracker Pro

**Production-grade Python application demonstrating OOP, SOLID principles, and 4 design patterns. Enterprise-level code with logging, error handling, and type hints.**

---

## Features

- ✅ **Add/View/Delete Expenses** with automatic validation
- ✅ **Advanced Analytics** (min, max, average, totals)
- ✅ **Category-wise Breakdown** with percentage charts
- ✅ **Filtering** by category and date range
- ✅ **CSV Export** for external analysis
- ✅ **Comprehensive Logging** (file + console)
- ✅ **Production-Grade Error Handling**
- ✅ **Type Hints & Custom Exceptions**


## Installation

**Requirements:** Python3
 No external dependencies needed!
 Just run:
 python expense_tracker.py

## Usage Examples

### Add an Expense
```
 Enter your choice (1-9): 1
Enter date (DDMMYyyyy): 07122025
Select category (1-8): 1
Enter description: Coffee at Cafe
Enter amount (₹): 150
Expense added: Coffee at Cafe (₹150)
```

### View Total Spending
```
Enter your choice (1-9): 3
TOTAL SPENDING SUMMARY
Total Expenses: 5
Total Spending: ₹2,500.00
Average Expense: ₹500.00
```

### Export to CSV
```
Enter your choice (1-9): 7
Exported 5 expenses to expenses_export.csv
```


## Configuration

### Data Storage
- **Format:** JSON (expenses.json)
- **Location:** Root directory
- **Auto-created:** Yes, on first run

### Logging
- **File:** logs/expense_tracker.log
- **Levels:** DEBUG (file), INFO (console)
- **Auto-created:** Yes

### Categories
```python
ExpenseCategory:
  1. Food
  2. Travel
  3. Shopping
  4. Entertainment
  5. Utilities
  6. Health
  7. Education
  8. Other
```

---

## Example Output

**View All Expenses:**
```
ALL EXPENSES
────────────────────────────────────────────────────────────
#    Date       Category        Description         Amount
────────────────────────────────────────────────────────────
1    07122025   Food            Coffee               ₹150.00
2    07122025   Travel          Taxi                 ₹300.00
3    08122025   Shopping        Books                ₹1,200.00
────────────────────────────────────────────────────────────
```

**Category Breakdown:**
```
SPENDING BY CATEGORY
──────────────────────────────────────
Shopping        ████████████░░   ₹1,200.00 (48.0%)
Travel          ██████░░░░░░░░   ₹300.00  (12.0%)
Food            ████░░░░░░░░░░   ₹150.00  (6.0%)
──────────────────────────────────────
TOTAL                             ₹2,500.00 (100.0%)
```

---

## Architecture

**Design Patterns Implemented:**
- **Singleton:** LoggerSetup (centralized logging)
- **Repository:** DataRepository + JSONRepository
- **Strategy:** Multiple filtering approaches
- **Enum:** Type-safe categories

**SOLID Principles:**
- **S**ingle Responsibility: Each class has one purpose
- **O**pen/Closed: Easy to extend (add SQLRepository)
- **L**iskov Substitution: Any repository implementation works
- **I**nterface Segregation: Minimal, focused interfaces
- **D**ependency Injection: Manager receives repository as parameter

---

## Contributing

### Ideas for Extensions
1. **Database Integration** - Add SQLRepository for PostgreSQL/MySQL
2. **Budget Limits** - Set spending caps per category
3. **Monthly Reports** - Generate comprehensive monthly analysis
4. **Web Interface** - Convert to Flask/Django web app
5. **Data Visualization** - Add matplotlib charts


## Feedback
If you have any feedback, please reach out to me at samithnitta1@gmail.com

## 📄 License

[MIT License](LICENSE) file for details.