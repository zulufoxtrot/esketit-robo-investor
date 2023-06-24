import logging
from enum import Enum

import requests as requests

from Loan import Loan

API_URL = "https://esketit.com/api"


class NotEnoughCashException(Exception):
    pass


class MarketType(Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"


class EsketitBrowser:

    def __init__(self, email: str, password: str):
        self.session = requests.session()
        self.email = email
        self.password = password

    def login(self):
        data = {
            "email": self.email,
            "password": self.password,
        }

        try:
            self.session.post(API_URL + "/investor/public/login", json=data)
        except Exception as e:
            logging.error("Login failed")

    def get_available_loans(self, market_type: MarketType, maximum_premium: float = 0.0):
        data = {
            "page": 1,
            "pageSize": 300,
            "filter": {
                "products": [],
                "countries": [],
                "originators": [],
                "collectionStatuses": ["Current"],
                "interestRatePercentFrom": "9",
                "remainingTermInDaysTo": "90",
                "excludeAlreadyInvested": True,
                "buybackOnly": True,
            },
        }

        if market_type == MarketType.PRIMARY:
            url = "/investor/public/query-primary-market"
            data["filter"]["principalOfferFrom"] = "10"

        elif market_type == MarketType.SECONDARY:
            url = "/investor/public/query-secondary-market"
            data["filter"]["smOfferPrincipalAvailableFrom"] = "10"
            data["filter"]["smDiscountOrPremiumPercentTo"] = str(maximum_premium)
            data["sortBy"] = "smDiscountOrPremiumPercent"

        resp = self.session.post(API_URL + url, json=data).json()

        if resp["total"] == 0:
            logging.info(f"No loans available on {market_type} market with these criteria")
            return []

        loans = []
        for loan_item in resp["items"]:
            loan = Loan()
            loan.investment_id = loan_item["investmentId"]
            loan.loan_id = loan_item["loanId"]
            loans.append(loan)

        logging.info(f"Found {len(loans)}.")
        return loans

    def buy_loan(self, loan: Loan):
        logging.info(f"Buying loan {loan.investment_id}...")
        data = {
            "amount": "10",
            "investmentId": loan.investment_id
        }
        self.session.headers["X-Xsrf-Token"] = self.session.cookies.get_dict()["XSRF-TOKEN"]
        req = self.session.post(API_URL + "/investor/buy-investment", json=data)
        if req.status_code == 400 and "NOT_ENOUGH_CASH" in req.text:
            raise NotEnoughCashException
        logging.info(f"Bought loan {loan.investment_id}")
