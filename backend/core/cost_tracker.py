"""
Cost tracking and budget management for Investment Research Assistant

Tracks API costs per request and enforces daily limits.
"""
import logging
from datetime import datetime
from typing import Dict, Optional
from collections import defaultdict
import os

logger = logging.getLogger(__name__)

# Configuration from environment
MAX_DAILY_COST_USD = float(os.getenv("MAX_DAILY_COST_USD", "20.0"))
RESET_HOUR = int(os.getenv("COST_RESET_HOUR", "0"))  # Midnight UTC

# In-memory cost tracking (in production, use Redis or database)
_daily_costs: Dict[str, float] = defaultdict(float)  # date -> total cost
_cost_tracking: Dict[str, Dict] = {}  # request_id -> cost details


def get_current_date() -> str:
    """Get current date string for cost tracking"""
    return datetime.utcnow().strftime("%Y-%m-%d")


def get_current_hour() -> int:
    """Get current hour in UTC"""
    return datetime.utcnow().hour


def reset_daily_costs_if_needed():
    """Reset daily costs if it's a new day"""
    current_date = get_current_date()
    # Remove old entries (keep only today and yesterday)
    dates_to_remove = [
        date for date in _daily_costs.keys()
        if date < current_date
    ]
    for date in dates_to_remove:
        del _daily_costs[date]


def add_cost(amount_usd: float, request_id: Optional[str] = None, source: str = "unknown") -> Dict[str, any]:
    """
    Add cost to daily tracking.
    
    Args:
        amount_usd: Cost in USD
        request_id: Optional request identifier
        source: Source of cost (e.g., 'openai', 'pinecone')
        
    Returns:
        Dict with current daily total and whether limit exceeded
    """
    reset_daily_costs_if_needed()
    current_date = get_current_date()
    
    _daily_costs[current_date] += amount_usd
    
    # Track detailed cost if request_id provided
    if request_id:
        _cost_tracking[request_id] = {
            "amount": amount_usd,
            "source": source,
            "timestamp": datetime.utcnow().isoformat(),
            "date": current_date
        }
    
    daily_total = _daily_costs[current_date]
    limit_exceeded = daily_total >= MAX_DAILY_COST_USD
    
    logger.info(
        f"Cost added: ${amount_usd:.4f} | "
        f"Daily total: ${daily_total:.2f}/${MAX_DAILY_COST_USD} | "
        f"Limit exceeded: {limit_exceeded}"
    )
    
    if limit_exceeded:
        logger.warning(
            f"⚠️ DAILY COST LIMIT EXCEEDED: ${daily_total:.2f} >= ${MAX_DAILY_COST_USD}"
        )
    
    return {
        "amount": amount_usd,
        "daily_total": daily_total,
        "daily_limit": MAX_DAILY_COST_USD,
        "limit_exceeded": limit_exceeded,
        "date": current_date
    }


def get_daily_cost() -> float:
    """Get current daily cost"""
    reset_daily_costs_if_needed()
    current_date = get_current_date()
    return _daily_costs.get(current_date, 0.0)


def check_cost_limit() -> tuple[bool, float, float]:
    """
    Check if daily cost limit has been exceeded.
    
    Returns:
        (limit_exceeded, current_cost, limit)
    """
    reset_daily_costs_if_needed()
    current_date = get_current_date()
    current_cost = _daily_costs.get(current_date, 0.0)
    limit_exceeded = current_cost >= MAX_DAILY_COST_USD
    
    return limit_exceeded, current_cost, MAX_DAILY_COST_USD


def get_cost_summary() -> Dict[str, any]:
    """Get summary of costs"""
    reset_daily_costs_if_needed()
    current_date = get_current_date()
    
    return {
        "date": current_date,
        "daily_total": _daily_costs.get(current_date, 0.0),
        "daily_limit": MAX_DAILY_COST_USD,
        "limit_exceeded": _daily_costs.get(current_date, 0.0) >= MAX_DAILY_COST_USD,
        "remaining_budget": max(0, MAX_DAILY_COST_USD - _daily_costs.get(current_date, 0.0))
    }
