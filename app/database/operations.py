from app.database.db import get_connection


def add_customer(name, phone=None):
    name = name.strip()

    if not name:
        raise ValueError("Customer name cannot be empty.")

    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO customers (name, phone) VALUES (?, ?)",
            (name, phone)
        )
        return cursor.lastrowid


def get_customers():
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM customers ORDER BY name"
        ).fetchall()


def add_transaction(customer_id, transaction_type, amount, note=None):
    transaction_type = transaction_type.upper()

    if transaction_type not in ("CREDIT", "PAYMENT"):
        raise ValueError("Type must be CREDIT or PAYMENT.")

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO transactions
            (customer_id, transaction_type, amount, note)
            VALUES (?, ?, ?, ?)
            """,
            (customer_id, transaction_type, amount, note)
        )
        return cursor.lastrowid


def get_customer_balance(customer_id):
    with get_connection() as conn:
        result = conn.execute(
            """
            SELECT
                COALESCE(SUM(
                    CASE WHEN transaction_type = 'CREDIT'
                    THEN amount ELSE 0 END
                ), 0)
                -
                COALESCE(SUM(
                    CASE WHEN transaction_type = 'PAYMENT'
                    THEN amount ELSE 0 END
                ), 0) AS balance
            FROM transactions
            WHERE customer_id = ?
            """,
            (customer_id,)
        ).fetchone()

        return result["balance"]


def add_customer_alias(customer_id, alias):
    alias = alias.strip()

    if not alias:
        raise ValueError("Alias cannot be empty.")

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO customer_aliases
            (customer_id, alias)
            VALUES (?, ?)
            """,
            (customer_id, alias)
        )
        return cursor.rowcount > 0


def find_customer_by_name(name):
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT DISTINCT c.*
            FROM customers c
            LEFT JOIN customer_aliases a
                ON c.id = a.customer_id
            WHERE c.name = ? COLLATE NOCASE
               OR a.alias = ? COLLATE NOCASE
            """,
            (name.strip(), name.strip())
        ).fetchall()
def get_customer_transactions(customer_id):
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT *
            FROM transactions
            WHERE customer_id = ?
            ORDER BY id DESC
            """,
            (customer_id,)
        ).fetchall()