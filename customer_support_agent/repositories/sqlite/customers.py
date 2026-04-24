from __future__ import annotations
from typing import Any
from customer_support_agent.repositories.sqlite.base import connect, row_to_dict

class CustomersRepository:
    
    def create_or_get(self, email: str, name: str | None = None, company: str | None = None) -> dict[str, Any]:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            customer = row_to_dict(row)
        else:
            cursor.execute(
                "INSERT INTO customers (email, name, company) VALUES (?, ?, ?)",
                (email, name, company)
            )
            conn.commit()
            customer_id = cursor.lastrowid
            customer = {
                "id": customer_id,
                "email": email,
                "name": name,
                "company": company,
                "created_at": None
            }
        conn.close()
        return customer
    
    def get_by_id(self,customer_id: int) -> dict[str, Any] | None:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        row = cursor.fetchone()
        conn.close()
        return row_to_dict(row)
    
    def get_by_email(self, email: str) -> dict[str, Any] | None:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        return row_to_dict(row)