import logging
import os

from EsketitBrowser import EsketitBrowser, MarketType, NotEnoughCashException

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    browser = EsketitBrowser(os.environ["ESKETIT_EMAIL"], os.environ["ESKETIT_PASSWORD"])

    # amount (in EUR) for each purchase
    AMOUNT_TO_BUY = 50

    browser.login()

    loans = []

    # first look for secondary loans with a discount
    # or no discount but still more interesting than new loans because term should be closer
    for max_premium in [-2, -1.5, -1, -0.5, 0]:
        loans += browser.get_available_loans(MarketType.SECONDARY, maximum_premium=max_premium)

    # then look for primary loans
    loans += browser.get_available_loans(MarketType.PRIMARY)

    for loan in loans:
        try:
            browser.buy_loan(loan, min(loan.principal_available, AMOUNT_TO_BUY))
        except NotEnoughCashException:
            logging.info("No more cash left. Stopping loans purchase.")
            break
