import logging
import os
import time

from EsketitBrowser import EsketitBrowser
from Investment import Investment


def calculate_profitability(investment: Investment, premium_percent):
    duration = investment.maturity_date - investment.investment_date
    logging.info(f"Days left: {duration.days}")
    interest_pending = investment.interest_rate / 100 * duration.days / 365
    logging.info(f"Interest pending: {round(interest_pending, 2)}€")
    resale_premium_percent = premium_percent / 100

    resale_value = investment.principal_outstanding * resale_premium_percent
    logging.info(f"Resale gain: {resale_value}€")

    profitability = round(resale_value - interest_pending, 2)
    logging.info(f"Profitability: {profitability}€")

    return resale_value - interest_pending


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    browser = EsketitBrowser(os.environ["ESKETIT_EMAIL"], os.environ["ESKETIT_PASSWORD"])

    PREMIUM_PERCENT = 0.5

    browser.login()

    portfolio = browser.get_portfolio()

    total_profit = 0

    for investment in portfolio:
        if not investment.secondary_market_discount_or_premium_percent:
            investment_profit = calculate_profitability(investment, PREMIUM_PERCENT)
            if investment_profit > 0:
                time.sleep(1)
                browser.sell_loan(investment, int(investment.principal_outstanding), PREMIUM_PERCENT)
                total_profit += investment_profit

    logging.info(f"Total profit: {total_profit}")
