import datetime


class Loan:
    investment_id: int
    loan_id: int
    principal_available: float
    interest_rate: float
    investment_date: datetime.date
    issue_date: datetime.date
    maturity_date: datetime.date
    next_payment_date: datetime.date
    term_days: int
    loan_originator: str
    loan_originator_id: int
    country_code: str
