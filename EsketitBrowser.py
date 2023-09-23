import logging
from datetime import datetime
from enum import Enum
from typing import List

import requests as requests

from Investment import Investment
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

    def get_portfolio(self) -> List[Investment]:
        data = {"page": 1,
                "pageSize": 5000,
                "filter": {"showActive": True,
                           "showClosed": False}
                }
        self.session.headers["X-Xsrf-Token"] = self.session.cookies.get_dict()["XSRF-TOKEN"]
        resp = self.session.post(API_URL + "/investor/query-my-investments", json=data).json()

        investments = []

        for item in resp["items"]:
            investment = Investment()
            investment.investment_id = item["investmentId"]
            investment.interest_rate = item["interestRatePercent"]  # 14.00,
            investment.investment_date = datetime.strptime(item["investmentDate"], "%Y-%m-%d")  # "2023-07-03",
            investment.issue_date = datetime.strptime(item["issueDate"], "%Y-%m-%d")  # "2023-02-15",
            investment.maturity_date = datetime.strptime(item["maturityDate"], "%Y-%m-%d")  # "2023-08-14",
            investment.next_payment_date = datetime.strptime(item["nextPaymentDate"], "%Y-%m-%d")  #: "2023-08-14",
            investment.term_days = item["termInDays"]  #: 23,
            investment.loan_originator = item["originatorCompanyName"]  #: "Money for Finance JO",
            investment.loan_originator_id = item["originatorId"]  #: 1693687,
            investment.country_code = item["countryCode"]  #: "JO",
            investment.principal_invested = item["principalInvested"]  #: 10.000000,
            investment.principal_outstanding = item["principalOutstanding"]  #: 10.000000,
            investment.principal_paid = item["principalPaid"]  #: 0.000000,
            investment.principal_pending = item["principalPending"]  #: 0.000000,
            investment.principal_received = item["principalReceived"]  #: 0.000000,
            investment.interest_paid = item["interestPaid"]  #: 0.046032,
            investment.interest_bonus_paid = item["interestBonusPaid"]  #: 0.000000,
            investment.interest_pending = item["interestPending"]  #: 0.000000,
            investment.interest_received = item["interestReceived"]  #: 0.046032,
            investment.bonus_paid = item["bonusPaid"]  #: 0.000000,
            investment.bonus_pending = item["bonusPending"]  #: 0.000000,
            investment.bonus_received = item["bonusReceived"]  #: 0.000000,
            investment.total_pending = item["totalPending"]  #: 0.000000,
            investment.secondary_market_discount_or_premium_percent = item["smDiscountOrPremiumPercent"]  #: null,
            investments.append(investment)

        return investments

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
                "currencyCode": "EUR",
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

    def buy_loan(self, loan: Loan, amount: int):
        logging.info(f"Buying loan {loan.investment_id}...")
        data = {
            "amount": amount,
            "investmentId": loan.investment_id
        }
        self.session.headers["X-Xsrf-Token"] = self.session.cookies.get_dict()["XSRF-TOKEN"]
        req = self.session.post(API_URL + "/investor/buy-investment", json=data)
        if req.status_code == 400 and "NOT_ENOUGH_CASH" in req.text:
            raise NotEnoughCashException
        logging.info(f"Bought loan {loan.investment_id}")

    def sell_loan(self, investment: Investment, amount: int, discount_or_premium_percent: float):
        """
        Puts a loan up for sale on the secondary market.
        :param investment: The investment/loan to sell
        :param amount: the amount (in EUR) to sell
        :param discount_or_premium_percent: discount or premium.
        Positive: premium (up to 2%)
        Negative: discount (up to -25%)
        Can also be zero.
        """
        logging.info(f"Selling investment {investment.investment_id}...")
        data = {"amount": amount,
                "discountOrPremiumPercent": discount_or_premium_percent,
                "investmentId": investment.investment_id}
        self.session.headers["X-Xsrf-Token"] = self.session.cookies.get_dict()["XSRF-TOKEN"]
        self.session.post(API_URL + "/investor/sell-investment", json=data)
