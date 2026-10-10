# /// script
# requires-python = ">=3.11"
# dependencies = ["selenium==4.49.*"]
# ///
"""Make the screenshots for the README in docs/screenshots/.

Usage: uv run --python 3.13 tools/screenshots.py

The script installs src/ as a temporary add-on in a new Firefox with a clean profile. The screenshots use
lemmy.ml as the home instance, because it has no Cloudflare bot check.
WebDriver cannot open the toolbar popup, so the script shows the popup page in the size of the popup.
toolbar-popup.png is a manual screenshot of the real popup, and this script does not make it.
"""

import base64
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import firefox as ff  # noqa: E402
from selenium.webdriver.common.by import By  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "screenshots"
HOME = "lemmy.ml"


def set_dark(driver, dark):
    # 0 makes the pages dark, 1 makes them light. ui.systemUsesDarkTheme does the same for the browser itself.
    ff.chrome(
        driver,
        "Services.prefs.setIntPref('layout.css.prefers-color-scheme.content-override', arguments[0] ? 0 : 1);"
        "Services.prefs.setIntPref('ui.systemUsesDarkTheme', arguments[0] ? 1 : 0);",
        dark,
    )
    time.sleep(1)


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


if __name__ == "__main__":
    main()
