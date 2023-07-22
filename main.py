import logging
import os

from EsketitBrowser import EsketitBrowser, MarketType, NotEnoughCashException

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    browser = EsketitBrowser(os.environ["ESKETIT_EMAIL"], os.environ["ESKETIT_PASSWORD"])

    # amount (in EUR) for each purchase
    AMOUNT_TO_BUY = 10

    browser.login()

    # first look for secondary loans with a discount
    # or no discount but still more interesting than new loans because term should be closer
    secondary_loans_with_discount = browser.get_available_loans(MarketType.SECONDARY, maximum_premium=-0.5)
    secondary_loans_without_discount = browser.get_available_loans(MarketType.SECONDARY, maximum_premium=0)

    # then look for primary loans
    primary_loans = browser.get_available_loans(MarketType.PRIMARY)

    loans = secondary_loans_with_discount + primary_loans + secondary_loans_without_discount

    for loan in loans:
        try:
            browser.buy_loan(loan, AMOUNT_TO_BUY)
        except NotEnoughCashException:
            logging.info("No more cash left. Stopping loans purchase.")
            break
