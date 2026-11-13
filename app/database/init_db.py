from app.database.db import get_connection


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL
                    CHECK(transaction_type IN ('CREDIT', 'PAYMENT')),
                amount REAL NOT NULL CHECK(amount > 0),
                note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS customer_aliases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                alias TEXT NOT NULL COLLATE NOCASE,
                UNIQUE(customer_id, alias),
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        """)

        conn.commit()


if __name__ == "__main__":
    initialize_database()
    print("DATABASE INITIALIZED SUCCESSFULLY")