"""
Advanced Expense Tracker - Production-Ready Application
Built with OOP, SOLID Principles, Design Patterns, and Best Practices

Features:
- Object-Oriented Design with Class-Based Architecture
- JSON Data Persistence (SQLite-ready structure)
- Comprehensive Error Handling and Logging
- Input Validation and Type Checking
- Advanced Filtering and Analytics
- Export to CSV Functionality
- Unit Test Ready Structure
- Professional Project Structure
- Comprehensive Documentation
"""

import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from enum import Enum
import csv
from pathlib import Path
from abc import ABC, abstractmethod


# ============================================================================
# LOGGING CONFIGURATION - Production-Grade Logging (Singleton Pattern)
# ============================================================================
class LoggerSetup:
    """Singleton pattern for centralized logging configuration."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerSetup, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance
    
    def _initialize_logger(self):
        """Configure logging with file and console handlers."""
        self.logger = logging.getLogger('ExpenseTracker')
        
        # Prevent duplicate handlers
        if self.logger.hasHandlers():
            return
        
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        Path('logs').mkdir(exist_ok=True)
        
        # File handler - DEBUG level
        file_handler = logging.FileHandler('logs/expense_tracker.log')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler - INFO level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)


# ============================================================================
# ENUMS AND CONSTANTS - Type-Safe Categories
# ============================================================================
class ExpenseCategory(Enum):
    """Enum for expense categories - Type safe and extensible."""
    FOOD = "Food"
    TRAVEL = "Travel"
    SHOPPING = "Shopping"
    ENTERTAINMENT = "Entertainment"
    UTILITIES = "Utilities"
    HEALTH = "Health"
    EDUCATION = "Education"
    OTHER = "Other"


# ============================================================================
# CUSTOM EXCEPTIONS - Professional Error Handling
# ============================================================================
class ExpenseTrackerException(Exception):
    """Base exception for Expense Tracker."""
    pass


class ValidationError(ExpenseTrackerException):
    """Raised when input validation fails."""
    pass


class DataPersistenceError(ExpenseTrackerException):
    """Raised when data persistence operations fail."""
    pass


# ============================================================================
# EXPENSE CLASS - Single Responsibility Principle
# ============================================================================
class Expense:
    """
    Represents a single expense transaction.
    Responsibility: Encapsulate expense data and validation.
    """
    
    def __init__(self, date: str, category: str, description: str, amount: float):
        """
        Initialize an Expense with validation.
        
        Args:
            date: Date in DDMMYYYY format
            category: Expense category
            description: Short description of expense
            amount: Amount spent (float)
        
        Raises:
            ValidationError: If validation fails
        """
        self._validate_inputs(date, category, description, amount)
        self.date = date
        self.category = category
        self.description = description
        self.amount = amount
        self.created_at = datetime.now().isoformat()
    
    @staticmethod
    def _validate_inputs(date: str, category: str, description: str, amount: float) -> None:
        """Validate all input parameters."""
        # Date validation
        if not date or len(date) != 8 or not date.isdigit():
            raise ValidationError(
                f"Invalid date format: '{date}'. Expected DDMMYYYY format."
            )
        
        try:
            day, month, year = int(date[0:2]), int(date[2:4]), int(date[4:8])
            if not (1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2100):
                raise ValidationError(
                    f"Invalid date values: Day={day}, Month={month}, Year={year}"
                )
        except ValueError as e:
            raise ValidationError(f"Date validation failed: {str(e)}")
        
        # Category validation
        valid_categories = [cat.value for cat in ExpenseCategory]
        if category not in valid_categories:
            raise ValidationError(
                f"Invalid category: '{category}'. "
                f"Valid categories: {', '.join(valid_categories)}"
            )
        
        # Description validation
        if not description or len(description.strip()) == 0:
            raise ValidationError("Description cannot be empty.")
        
        if len(description) > 100:
            raise ValidationError("Description must be 100 characters or less.")
        
        # Amount validation
        try:
            amount_float = float(amount)
            if amount_float <= 0:
                raise ValidationError("Amount must be greater than 0.")
            if amount_float > 1000000:
                raise ValidationError("Amount exceeds reasonable limit (1,000,000).")
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid amount: {str(e)}")
    
    def to_dict(self) -> Dict:
        """Convert expense to dictionary for serialization."""
        return {
            'date': self.date,
            'category': self.category,
            'description': self.description,
            'amount': self.amount,
            'created_at': self.created_at
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Expense':
        """Create Expense from dictionary."""
        return Expense(
            date=data['date'],
            category=data['category'],
            description=data['description'],
            amount=data['amount']
        )
    
    def __str__(self) -> str:
        """String representation of expense."""
        return (
            f"Date: {self.date} | Category: {self.category} | "
            f"Description: {self.description} | Amount: ₹{self.amount:.2f}"
        )
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Expense({self.date}, {self.category}, ₹{self.amount})"
    
    def __eq__(self, other) -> bool:
        """Check equality based on date, category, and amount."""
        if not isinstance(other, Expense):
            return False
        return (self.date == other.date and 
                self.category == other.category and 
                self.amount == other.amount)


# ============================================================================
# DATA PERSISTENCE - Repository Pattern (Abstract Base Class)
# ============================================================================
class DataRepository(ABC):
    """Abstract base class for data persistence."""
    
    @abstractmethod
    def load(self) -> List[Expense]:
        """Load expenses from storage."""
        pass
    
    @abstractmethod
    def save(self, expenses: List[Expense]) -> None:
        """Save expenses to storage."""
        pass


class JSONRepository(DataRepository):
    """
    JSON-based data persistence.
    Responsibility: Abstract data storage implementation.
    """
    
    def __init__(self, filename: str = 'expenses.json'):
        """Initialize repository with file path."""
        self.filename = filename
        self.logger = LoggerSetup().logger
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Create file if it doesn't exist."""
        if not Path(self.filename).exists():
            self._save_data([])
            self.logger.info(f"Created new data file: {self.filename}")
    
    def load(self) -> List[Expense]:
        """
        Load expenses from JSON file.
        
        Returns:
            List of Expense objects
            
        Raises:
            DataPersistenceError: If loading fails
        """
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
            
            expenses = [Expense.from_dict(item) for item in data]
            self.logger.info(f"Loaded {len(expenses)} expenses from {self.filename}")
            return expenses
        except json.JSONDecodeError:
            self.logger.error(f"Corrupted JSON file: {self.filename}")
            raise DataPersistenceError(f"Corrupted JSON file: {self.filename}")
        except Exception as e:
            self.logger.error(f"Error loading expenses: {str(e)}")
            raise DataPersistenceError(f"Error loading expenses: {str(e)}")
    
    def save(self, expenses: List[Expense]) -> None:
        """
        Save expenses to JSON file.
        
        Args:
            expenses: List of Expense objects
            
        Raises:
            DataPersistenceError: If saving fails
        """
        try:
            data = [expense.to_dict() for expense in expenses]
            self._save_data(data)
            self.logger.info(f"Saved {len(expenses)} expenses to {self.filename}")
        except Exception as e:
            self.logger.error(f"Error saving expenses: {str(e)}")
            raise DataPersistenceError(f"Error saving expenses: {str(e)}")
    
    def _save_data(self, data: List[Dict]) -> None:
        """Helper method to save data with proper formatting."""
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=4)


# ============================================================================
# EXPENSE MANAGER - Business Logic (Strategy Pattern + SOLID)
# ============================================================================
class ExpenseManager:
    """
    Core business logic for expense management.
    Responsibility: Manage expense operations and calculations.
    Dependency Injection: Receives repository as parameter.
    """
    
    def __init__(self, repository: DataRepository):
        """
        Initialize with repository (Dependency Injection).
        
        Args:
            repository: DataRepository instance
        """
        self.repository = repository
        self.expenses: List[Expense] = []
        self.logger = LoggerSetup().logger
        self._load_expenses()
    
    def _load_expenses(self) -> None:
        """Load expenses from repository."""
        try:
            self.expenses = self.repository.load()
        except DataPersistenceError as e:
            self.logger.warning(f"Using empty expense list: {str(e)}")
            self.expenses = []
    
    def add_expense(self, date: str, category: str, description: str, amount: float) -> Tuple[bool, str]:
        """
        Add a new expense with validation.
        
        Args:
            date: Date in DDMMYYYY format
            category: Expense category
            description: Short description
            amount: Amount spent
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            expense = Expense(date, category, description, amount)
            self.expenses.append(expense)
            self.repository.save(self.expenses)
            self.logger.info(f"Added expense: {expense}")
            return True, f"✅ Expense added: {expense.description} (₹{amount})"
        except ValidationError as e:
            self.logger.warning(f"Failed to add expense: {str(e)}")
            return False, f"❌ Validation Error: {str(e)}"
        except DataPersistenceError as e:
            self.logger.error(f"Failed to save expense: {str(e)}")
            return False, f"❌ Save Error: {str(e)}"
    
    def get_all_expenses(self) -> List[Expense]:
        """Return all expenses."""
        return self.expenses.copy()
    
    def get_total_spending(self) -> float:
        """Calculate total spending."""
        return sum(expense.amount for expense in self.expenses)
    
    def get_spending_by_category(self) -> Dict[str, float]:
        """
        Get spending breakdown by category.
        
        Returns:
            Dictionary with category as key and total amount as value
        """
        breakdown = {}
        for expense in self.expenses:
            if expense.category not in breakdown:
                breakdown[expense.category] = 0
            breakdown[expense.category] += expense.amount
        return breakdown
    
    def get_category_statistics(self) -> Dict[str, Dict]:
        """Get detailed statistics for each category."""
        stats = {}
        for category in ExpenseCategory:
            expenses = self.filter_by_category(category.value)
            if expenses:
                amounts = [e.amount for e in expenses]
                stats[category.value] = {
                    'count': len(expenses),
                    'total': sum(amounts),
                    'average': sum(amounts) / len(amounts),
                    'min': min(amounts),
                    'max': max(amounts)
                }
        return stats
    
    def get_average_spending(self) -> float:
        """Calculate average expense amount."""
        if not self.expenses:
            return 0.0
        return self.get_total_spending() / len(self.expenses)
    
    def filter_by_category(self, category: str) -> List[Expense]:
        """Filter expenses by category."""
        return [exp for exp in self.expenses if exp.category == category]
    
    def filter_by_date_range(self, start_date: str, end_date: str) -> List[Expense]:
        """
        Filter expenses by date range (DDMMYYYY format).
        
        Args:
            start_date: Start date in DDMMYYYY format
            end_date: End date in DDMMYYYY format
        
        Returns:
            List of expenses within date range
        """
        return [
            exp for exp in self.expenses
            if start_date <= exp.date <= end_date
        ]
    
    def delete_expense(self, index: int) -> Tuple[bool, str]:
        """
        Delete expense by index.
        
        Args:
            index: Index of expense to delete
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if 0 <= index < len(self.expenses):
                deleted = self.expenses.pop(index)
                self.repository.save(self.expenses)
                self.logger.info(f"Deleted expense: {deleted}")
                return True, f"✅ Deleted: {deleted.description}"
            return False, "❌ Invalid expense number."
        except DataPersistenceError as e:
            self.logger.error(f"Error deleting expense: {str(e)}")
            return False, f"❌ Delete Error: {str(e)}"
    
    def export_to_csv(self, filename: str = 'expenses_export.csv') -> Tuple[bool, str]:
        """
        Export all expenses to CSV file.
        
        Args:
            filename: Output CSV filename
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.DictWriter(
                    f,
                    fieldnames=['date', 'category', 'description', 'amount', 'created_at']
                )
                writer.writeheader()
                writer.writerows([exp.to_dict() for exp in self.expenses])
            self.logger.info(f"Exported {len(self.expenses)} expenses to {filename}")
            return True, f"✅ Exported {len(self.expenses)} expenses to {filename}"
        except Exception as e:
            self.logger.error(f"Error exporting to CSV: {str(e)}")
            return False, f"❌ Export Error: {str(e)}"


# ============================================================================
# USER INTERFACE - Clean Presentation Logic
# ============================================================================
class ExpenseTrackerUI:
    """
    User interface for the expense tracker.
    Responsibility: Handle user interaction and display.
    """
    
    def __init__(self, manager: ExpenseManager):
        """Initialize UI with expense manager."""
        self.manager = manager
        self.logger = LoggerSetup().logger
    
    def display_welcome(self) -> None:
        """Display welcome message."""
        print("\n" + "="*70)
        print("           🏦 EXPENSE TRACKER PRO (Production Version)")
        print("="*70)
        print("Advanced Money Management System with Analytics & Logging")
        print("Built with OOP, SOLID Principles, and Design Patterns")
        print("="*70 + "\n")
    
    def display_menu(self) -> None:
        """Display main menu."""
        print("\n📋 MAIN MENU")
        print("-" * 50)
        print("1. ➕ Add Expense")
        print("2. 📊 View All Expenses")
        print("3. 💰 View Total Spending")
        print("4. 📈 View Spending by Category")
        print("5. 📊 View Analytics & Statistics")
        print("6. 🔍 Filter Expenses")
        print("7. 💾 Export to CSV")
        print("8. ❌ Delete Expense")
        print("9. 🚪 Exit")
        print("-" * 50)
    
    def get_menu_choice(self) -> str:
        """Get user menu choice with validation."""
        while True:
            choice = input("\n👉 Enter your choice (1-9): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                return choice
            print("❌ Invalid choice. Please enter 1-9.")
    
    def handle_add_expense(self) -> None:
        """Handle adding a new expense."""
        try:
            print("\n📝 ADD NEW EXPENSE")
            print("-" * 50)
            
            date = input("Enter date (DDMMYYYY): ").strip()
            
            print("\nAvailable Categories:")
            for i, category in enumerate(ExpenseCategory, 1):
                print(f"  {i}. {category.value}")
            
            cat_choice = input("Select category (1-8): ").strip()
            categories = list(ExpenseCategory)
            
            if not cat_choice.isdigit() or not (1 <= int(cat_choice) <= len(categories)):
                print("❌ Invalid category selection.")
                return
            
            category = categories[int(cat_choice) - 1].value
            description = input("Enter description (max 100 chars): ").strip()
            
            try:
                amount = float(input("Enter amount (₹): ").strip())
            except ValueError:
                print("❌ Please enter a valid number for amount.")
                return
            
            success, message = self.manager.add_expense(date, category, description, amount)
            print(message)
            
        except Exception as e:
            print(f"❌ Unexpected Error: {str(e)}")
            self.logger.error(f"Error in add_expense: {str(e)}")
    
    def handle_view_all_expenses(self) -> None:
        """Display all expenses."""
        expenses = self.manager.get_all_expenses()
        
        if not expenses:
            print("\n📭 No expenses recorded yet. Start adding some!")
            return
        
        print("\n📊 ALL EXPENSES")
        print("-" * 100)
        print(f"{'#':<4} {'Date':<10} {'Category':<15} {'Description':<30} {'Amount':<12}")
        print("-" * 100)
        
        for idx, expense in enumerate(expenses, 1):
            print(
                f"{idx:<4} {expense.date:<10} {expense.category:<15} "
                f"{expense.description:<30} ₹{expense.amount:<11,.2f}"
            )
        
        print("-" * 100)
    
    def handle_view_total(self) -> None:
        """Display total spending."""
        total = self.manager.get_total_spending()
        count = len(self.manager.get_all_expenses())
        avg = self.manager.get_average_spending()
        
        print("\n💰 TOTAL SPENDING SUMMARY")
        print("-" * 50)
        print(f"Total Expenses: {count}")
        print(f"Total Spending: ₹{total:,.2f}")
        print(f"Average Expense: ₹{avg:,.2f}")
        print("-" * 50)
    
    def handle_view_by_category(self) -> None:
        """Display spending by category."""
        breakdown = self.manager.get_spending_by_category()
        
        if not breakdown:
            print("\n📭 No expenses recorded yet.")
            return
        
        print("\n📈 SPENDING BY CATEGORY")
        print("-" * 50)
        
        total = sum(breakdown.values())
        for category, amount in sorted(breakdown.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total) * 100
            bar = "█" * int(percentage // 5)
            print(f"{category:<15} {bar:<20} ₹{amount:>10,.2f} ({percentage:>5.1f}%)")
        
        print("-" * 50)
        print(f"{'TOTAL':<15} {'':<20} ₹{total:>10,.2f} (100.0%)")
    
    def handle_analytics(self) -> None:
        """Display detailed analytics and statistics."""
        expenses = self.manager.get_all_expenses()
        
        if not expenses:
            print("\n📭 No expenses recorded yet.")
            return
        
        total = self.manager.get_total_spending()
        avg = self.manager.get_average_spending()
        min_exp = min(expenses, key=lambda x: x.amount)
        max_exp = max(expenses, key=lambda x: x.amount)
        category_stats = self.manager.get_category_statistics()
        
        print("\n📊 ANALYTICS & INSIGHTS")
        print("-" * 60)
        print(f"Total Transactions: {len(expenses)}")
        print(f"Total Spending: ₹{total:,.2f}")
        print(f"Average Spending: ₹{avg:,.2f}")
        print(f"Highest Expense: ₹{max_exp.amount:,.2f} ({max_exp.category})")
        print(f"Lowest Expense: ₹{min_exp.amount:,.2f} ({min_exp.category})")
        
        print("\n📊 CATEGORY STATISTICS:")
        print("-" * 60)
        for category, stats in category_stats.items():
            print(f"\n{category}:")
            print(f"  Count:   {stats['count']}")
            print(f"  Total:   ₹{stats['total']:,.2f}")
            print(f"  Average: ₹{stats['average']:,.2f}")
            print(f"  Min:     ₹{stats['min']:,.2f}")
            print(f"  Max:     ₹{stats['max']:,.2f}")
        
        print("\n" + "-" * 60)
    
    def handle_filter(self) -> None:
        """Handle expense filtering."""
        print("\n🔍 FILTER EXPENSES")
        print("-" * 50)
        print("1. Filter by Category")
        print("2. Filter by Date Range")
        print("-" * 50)
        
        choice = input("Select filter type (1-2): ").strip()
        
        if choice == '1':
            self._filter_by_category()
        elif choice == '2':
            self._filter_by_date_range()
        else:
            print("❌ Invalid choice.")
    
    def _filter_by_category(self) -> None:
        """Filter and display expenses by category."""
        print("\nAvailable Categories:")
        for i, category in enumerate(ExpenseCategory, 1):
            print(f"  {i}. {category.value}")
        
        cat_choice = input("Select category (1-8): ").strip()
        categories = list(ExpenseCategory)
        
        if not (cat_choice.isdigit() and 1 <= int(cat_choice) <= len(categories)):
            print("❌ Invalid category selection.")
            return
        
        category = categories[int(cat_choice) - 1].value
        filtered = self.manager.filter_by_category(category)
        
        if not filtered:
            print(f"\n📭 No expenses in {category} category.")
            return
        
        print(f"\n📊 Expenses in {category}:")
        print("-" * 90)
        print(f"{'#':<4} {'Date':<10} {'Description':<35} {'Amount':<12}")
        print("-" * 90)
        
        total = 0
        for idx, expense in enumerate(filtered, 1):
            print(f"{idx:<4} {expense.date:<10} {expense.description:<35} ₹{expense.amount:<11,.2f}")
            total += expense.amount
        
        print("-" * 90)
        print(f"{'TOTAL':<4} {'':<10} {'':<35} ₹{total:<11,.2f}")
    
    def _filter_by_date_range(self) -> None:
        """Filter and display expenses by date range."""
        start_date = input("Enter start date (DDMMYYYY): ").strip()
        end_date = input("Enter end date (DDMMYYYY): ").strip()
        filtered = self.manager.filter_by_date_range(start_date, end_date)
        
        if not filtered:
            print("\n📭 No expenses found in this date range.")
            return
        
        print(f"\n📊 Expenses from {start_date} to {end_date}:")
        print("-" * 100)
        print(f"{'#':<4} {'Date':<10} {'Category':<15} {'Description':<30} {'Amount':<12}")
        print("-" * 100)
        
        total = 0
        for idx, expense in enumerate(filtered, 1):
            print(
                f"{idx:<4} {expense.date:<10} {expense.category:<15} "
                f"{expense.description:<30} ₹{expense.amount:<11,.2f}"
            )
            total += expense.amount
        
        print("-" * 100)
        print(f"{'TOTAL':<4} {'':<10} {'':<15} {'':<30} ₹{total:<11,.2f}")
    
    def handle_delete_expense(self) -> None:
        """Handle expense deletion."""
        expenses = self.manager.get_all_expenses()
        
        if not expenses:
            print("\n📭 No expenses to delete.")
            return
        
        self.handle_view_all_expenses()
        
        try:
            index = int(input("\nEnter expense number to delete: ").strip()) - 1
            
            if 0 <= index < len(expenses):
                expense = expenses[index]
                confirm = input(f"Delete '{expense.description}'? (y/n): ").strip().lower()
                
                if confirm == 'y':
                    success, message = self.manager.delete_expense(index)
                    print(message)
                else:
                    print("❌ Deletion cancelled.")
            else:
                print("❌ Invalid expense number.")
        
        except ValueError:
            print("❌ Please enter a valid number.")
    
    def run(self) -> None:
        """Run the main application loop."""
        self.display_welcome()
        
        try:
            while True:
                self.display_menu()
                choice = self.get_menu_choice()
                
                if choice == '1':
                    self.handle_add_expense()
                elif choice == '2':
                    self.handle_view_all_expenses()
                elif choice == '3':
                    self.handle_view_total()
                elif choice == '4':
                    self.handle_view_by_category()
                elif choice == '5':
                    self.handle_analytics()
                elif choice == '6':
                    self.handle_filter()
                elif choice == '7':
                    success, message = self.manager.export_to_csv()
                    print(message)
                elif choice == '8':
                    self.handle_delete_expense()
                elif choice == '9':
                    print("\n👋 Thank you for using Expense Tracker Pro!")
                    print("📁 Logs saved to 'logs/expense_tracker.log'")
                    print("💾 Data saved to 'expenses.json'")
                    self.logger.info("Application closed by user.")
                    break
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Application interrupted by user.")
            self.logger.info("Application interrupted.")
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            self.logger.error(f"Unexpected error: {str(e)}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================
def main() -> None:
    """Application entry point."""
    try:
        # Initialize logger (Singleton)
        LoggerSetup()
        
        # Initialize repository
        repository = JSONRepository('expenses.json')
        
        # Initialize manager with repository (Dependency Injection)
        manager = ExpenseManager(repository)
        
        # Initialize and run UI
        ui = ExpenseTrackerUI(manager)
        ui.run()
    
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        print(f"❌ Fatal Error: {str(e)}")


if __name__ == '__main__':

    main()
