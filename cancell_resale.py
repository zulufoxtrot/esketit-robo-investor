import logging
import os
import time

from EsketitBrowser import EsketitBrowser

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    browser = EsketitBrowser(os.environ["ESKETIT_EMAIL"], os.environ["ESKETIT_PASSWORD"])

    browser.login()

    portfolio = browser.get_portfolio()

    for investment in portfolio:
        if investment.secondary_market_discount_or_premium_percent:
            time.sleep(1)
            browser.sell_loan(investment, 0, 0)
