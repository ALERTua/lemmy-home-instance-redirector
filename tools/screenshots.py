# /// script
# requires-python = ">=3.11"
# dependencies = ["selenium==4.49.*"]
# ///
"""Make the screenshots for the README in docs/screenshots/.

Usage: uv run --python 3.13 tools/screenshots.py

The script installs src/ as a temporary add-on in the driven Firefox. The screenshots use
lemmy.ml as the home instance: it has no Cloudflare bot check, and the profile has no login there.
WebDriver cannot open the toolbar popup, so the script shows the popup page in the size of the popup.
"""

import base64
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.expanduser("~/.claude/tools"))
import driven_firefox as ff  # noqa: E402
from selenium.webdriver.common.by import By  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "screenshots"
HOME = "lemmy.ml"
POST = "https://feddit.uk/post/56670482"


def set_dark(driver, dark):
    # 0 makes the pages dark, 1 makes them light. ui.systemUsesDarkTheme does the same for the browser itself.
    ff.chrome(
        driver,
        "Services.prefs.setIntPref('layout.css.prefers-color-scheme.content-override', arguments[0] ? 0 : 1);"
        "Services.prefs.setIntPref('ui.systemUsesDarkTheme', arguments[0] ? 1 : 0);",
        dark,
    )
    time.sleep(1)


def save_window(driver, name):
    """Save the whole browser window, with the toolbar and the address bar."""
    # Under WebDriver, Firefox paints the address bar with stripes and shows a robot icon.
    ff.chrome(driver, "document.documentElement.removeAttribute('remotecontrol')")
    with driver.context(driver.CONTEXT_CHROME):
        png = driver.get_screenshot_as_png()
    (OUT / name).write_bytes(png)
    print("saved", name)


def save_page(driver, name):
    (OUT / name).write_bytes(base64.b64decode(driver.get_screenshot_as_base64()))
    print("saved", name)


def save_popup(driver, settings_url, name):
    """Save the popup page as the toolbar shows it: the narrow layout without the card."""
    driver.get(settings_url)
    settings_status(driver)
    ff.page(driver, "document.body.classList.remove('tab')")
    time.sleep(0.3)
    (OUT / name).write_bytes(driver.find_element(By.TAG_NAME, "body").screenshot_as_png)
    print("saved", name)


def settings_status(driver):
    deadline = time.time() + 15
    while time.time() < deadline:
        text = driver.find_element(By.ID, "status").text
        if text and not text.startswith("Checking"):
            return text
        time.sleep(0.3)
    return text


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with ff.session() as driver:
        addon_id = driver.install_addon(str(ROOT / "src"), temporary=True)
        time.sleep(3)
        driver.switch_to.window(driver.window_handles[-1])
        driver.set_window_rect(width=760, height=520)
        host = ff.chrome(driver, "return WebExtensionPolicy.getByID(arguments[0]).mozExtensionHostname", addon_id)
        settings_url = f"moz-extension://{host}/popup.html"
        ff.chrome(driver, "Services.prefs.setCharPref('intl.accept_languages', 'en-US, en')")

        # The settings tab, as the installation opens it, with the example under the field.
        for dark in (False, True):
            set_dark(driver, dark)
            driver.get(settings_url)
            settings_status(driver)
            save_page(driver, f"settings-empty-{'dark' if dark else 'light'}.png")

        set_dark(driver, False)
        driver.get(settings_url)
        settings_status(driver)
        driver.find_element(By.ID, "host").send_keys(HOME)
        driver.find_element(By.ID, "save").click()
        time.sleep(0.5)
        settings_status(driver)
        save_page(driver, "settings-saved-light.png")

        for dark in (False, True):
            set_dark(driver, dark)
            save_popup(driver, settings_url, f"popup-{'dark' if dark else 'light'}.png")

        # The redirect: a post on a private Lemmy server opens on the home instance.
        driver.set_window_rect(width=1280, height=800)
        ff.chrome(
            driver,
            "const id = arguments[0].toLowerCase().replace(/[^a-z0-9_-]/g, '_') + '-browser-action';"
            "window.CustomizableUI.addWidgetToArea(id, window.CustomizableUI.AREA_NAVBAR);",
            addon_id,
        )
        for dark in (False, True):
            set_dark(driver, dark)
            driver.get(POST)
            deadline = time.time() + 20
            while not driver.current_url.startswith(f"https://{HOME}/post/") and time.time() < deadline:
                time.sleep(0.5)
            time.sleep(4)
            save_window(driver, f"redirect-{'dark' if dark else 'light'}.png")


if __name__ == "__main__":
    main()
