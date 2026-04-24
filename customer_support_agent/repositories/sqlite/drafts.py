from __future__ import annotations
from typing import Any

from customer_support_agent.repositories.sqlite.base import connect, row_to_dict

class DraftsRepository:
    def create(self, ticket_id: int, content: str, context_used: str | None = None,status: str = "pending") -> dict[str, Any]:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO drafts (ticket_id, content, context_used, status) VALUES (?, ?, ?, ?)",
            (ticket_id, content, context_used, status)
        )
        conn.commit()
        draft_id = cursor.lastrowid
        conn.close()
        return {
            "id": draft_id,
            "ticket_id": ticket_id,
            "content": content,
            "context_used": context_used,
            "status": status,
            "created_at": None
        }
    def get_ticket_and_customer_by_draft(self, draft_id: int) -> dict[str, Any] | None:
        with connect() as conn:
            row = conn.execute(
                """
                SELECT
                    d.id AS draft_id,
                    d.ticket_id,
                    d.content AS draft_content,
                    d.status AS draft_status,
                    t.subject,
                    t.description,
                    t.status AS ticket_status,
                    c.id AS customer_id,
                    c.email AS customer_email,
                    c.name AS customer_name,
                    c.company AS customer_company
                FROM drafts d
                JOIN tickets t ON t.id = d.ticket_id
                JOIN customers c ON c.id = t.customer_id
                WHERE d.id = ?
                """,
                (draft_id,),
            ).fetchone()
            return row_to_dict(row)
        
    def update(self,
        draft_id: int,
        content: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any] | None:
        with connect() as conn:
            if content is not None and status is not None:
                conn.execute(
                    "UPDATE drafts SET content = ?, status = ? WHERE id = ?",
                    (content, status, draft_id),
                )
            elif content is not None:
                conn.execute(
                    "UPDATE drafts SET content = ? WHERE id = ?",
                    (content, draft_id),
                )
            elif status is not None:
                conn.execute(
                    "UPDATE drafts SET status = ? WHERE id = ?",
                    (status, draft_id),
                )
            else:
                return self.get_ticket_and_customer_by_draft(draft_id)
            conn.commit()
            return self.get_ticket_and_customer_by_draft(draft_id)
        
    def get_by_id(self, draft_id: int) -> dict[str, Any] | None:
        with connect() as conn:
            row = conn.execute(
                "SELECT * FROM drafts WHERE id = ?",
                (draft_id,),
            ).fetchone()
            return row_to_dict(row)
        
    def get_latest_for_ticket(self, ticket_id: int) -> dict[str, Any] | None:
        with connect() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM drafts
                WHERE ticket_id = ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (ticket_id,),
            ).fetchone()
            return row_to_dict(row)