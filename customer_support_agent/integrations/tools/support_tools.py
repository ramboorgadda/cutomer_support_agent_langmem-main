from __future__ import annotations
import hashlib
import json
from typing import Any
from langchain_core.tools import tool
from customer_support_agent.repositories.sqlite.customers import CustomersRepository
from customer_support_agent.repositories.sqlite.tickets import TicketsRepository


def _stable_bucket(email:str,size:int)-> str:
    """A stable hashing function to bucket customers based on their email."""
    digest = hashlib.sha256(email.encode()).hexdigest()
    return int(digest, 16) % size

def _json(payload: dict[str,Any]) -> str:
    """Helper to convert dict to JSON string for tool input/output."""
    return json.dumps(payload)
def _load_band(open_count: int) -> str:
    """Determine the band for a customer based on their open ticket count."""
    if open_count == 0:
        return "light"
    elif open_count <= 2:
        return "moderate"
    else:
        return "heavy"
@tool
def lookup_customer_plan(customer_email: str) -> str:
    """Tool to lookup a customer's plan based on their email."""
    plans = [{"plan_tier": "free", "sla_hours": 48, "priority_queue": False},
        {"plan_tier": "starter", "sla_hours": 24, "priority_queue": False},
        {"plan_tier": "pro", "sla_hours": 8, "priority_queue": True},
        {"plan_tier": "enterprise", "sla_hours": 1, "priority_queue": True}]
    plan = plans[_stable_bucket(customer_email,size=len(plans))]
    summary = (f"Customer {customer_email} is on the {plan['plan_tier']} with an SLA of {plan['sla_hours']} hours.")
    return _json(
        {
            "tool": "lookup_customer_plan",
            "customer_email":  customer_email,
            "summary": summary,
            "detail": plan,
            "recommended_action":("Use priority handling." if plan["priority_queue"] else "Use standard handling.")
        }
    )
    
@tool
def lookup_open_ticket_load(customer_email: str) ->str:
    """Tool to lookup the number of open tickets for a customer."""
    customers_repo = CustomersRepository()
    tickets_repo = TicketsRepository()
    customer = customers_repo.get_by_email(customer_email)
    if not customer:
        return _json(
            {
                "tool": "lookup_open_ticket_load",
                "customer_email": customer_email,
                "summary": f"No customer found with email {customer_email}.",
                "detail": None,
                "recommended_action": "Verify the customer's email address."
            }
        )
    open_count = tickets_repo.count_open_for_customer(customer_email)
    band = _load_band(open_count)
    summary = f"Customer {customer_email} has {open_count} open tickets, which is considered a {band} load."
    return _json(
        {
            "tool": "lookup_open_ticket_load",
            "customer_email": customer_email,
            "summary": summary,
            "detail": {"open_ticket_count": open_count, "load_band": band},
            "recommended_action": ("Prioritize this customer." if band in ["heavy","moderate"] else "Standard handling.")
        }
    )
    
def get_support_tools() -> list:
    return [lookup_customer_plan, lookup_open_ticket_load]
    