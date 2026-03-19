# Database file path (must match the SQLiteStudio database filename)
DB_PATH = "ecommerce_platform.db"

# Order status constants
STATUS_PENDING = "PENDING"    # Pending (modifiable/cancellable)
STATUS_SHIPPED = "SHIPPED"    # Shipped (non-modifiable)
STATUS_CANCELLED = "CANCELLED"# Cancelled (non-operational)

# CLI interface color constants (for beautification)
COLOR_GREEN = "\033[32m"
COLOR_RED = "\033[31m"
COLOR_YELLOW = "\033[33m"
COLOR_RESET = "\033[0m"