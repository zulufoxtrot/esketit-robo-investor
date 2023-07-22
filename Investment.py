from Loan import Loan


class Investment(Loan):
    investment_id: int
    principal_invested: float
    principal_outstanding: float
    principal_paid: float
    principal_pending: float
    principal_received: float
    interest_paid: float
    interest_bonus_paid: float
    interest_pending: float
    interest_received: float
    bonus_paid: float
    bonus_pending: float
    bonus_received: float
    total_pending: float
    secondary_market_discount_or_premium_percent: float
