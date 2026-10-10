"""Start Firefox through Selenium with a clean temporary profile for the end-to-end tools.

The profile has no logins, so the tests never see an account of the developer.
FIREFOX_BIN sets the Firefox binary, and FIREFOX_HEADLESS=1 hides the window.
"""

import contextlib
import os

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service


@contextlib.contextmanager
def session():
    """Yield a WebDriver of a new Firefox, and quit Firefox at the end."""
    options = Options()
    if os.environ.get("FIREFOX_BIN"):
        options.binary_location = os.environ["FIREFOX_BIN"]
    if os.environ.get("FIREFOX_HEADLESS") == "1":
        options.add_argument("-headless")
    # Without these, a new profile opens welcome pages that take the place of the start tab.
    options.set_preference("browser.startup.page", 0)
    options.set_preference("browser.startup.homepage_override.mstone", "ignore")
    options.set_preference("startup.homepage_welcome_url", "")
    options.set_preference("startup.homepage_welcome_url.additional", "")
    options.set_preference("browser.aboutwelcome.enabled", False)
    options.set_preference("datareporting.policy.dataSubmissionEnabled", False)
    options.set_preference("intl.accept_languages", "en-US, en")
    # The chrome context (prefs, AddonManager, the toolbar) needs this flag of geckodriver.
    driver = webdriver.Firefox(options=options, service=Service(service_args=["--allow-system-access"]))
    try:
        yield driver
    finally:
        driver.quit()


def page(driver, body, *args):
    """Run JavaScript in the page and return the value of its return."""
    return driver.execute_script(body, *args)


def chrome(driver, body, *args):
    """Run JavaScript in the privileged context of Firefox, where Services exists."""
    with driver.context(driver.CONTEXT_CHROME):
        return driver.execute_script(body, *args)
