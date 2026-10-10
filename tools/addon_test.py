# /// script
# requires-python = ">=3.11"
# dependencies = ["selenium==4.49.*"]
# ///
"""Install the add-on in the driven Firefox and run the scenarios.

Usage: uv run --python 3.13 tools/addon_test.py [path to a signed .xpi]

Without an argument, the test installs src/ as a temporary add-on.
The test saves sh.itjust.works as the home instance in the settings tab that the installation opens.
With a signed .xpi, the test installs it as a permanent add-on, so Firefox checks the signature.

Each scenario opens a live page and checks where the browser ends up.
The add-on sends its requests without cookies, so a redirect needs no login on the home instance.
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.expanduser("~/.claude/tools"))
import driven_firefox as ff  # noqa: E402
from selenium.webdriver.common.action_chains import ActionChains  # noqa: E402
from selenium.webdriver.common.by import By  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HOME = "https://sh.itjust.works"
WAIT_S = 25

# (name, start URL, expected final URL or None when the browser must not go to the home instance)
# A private Lemmy server, for example feddit.uk, answers the post address with a redirect to /signup.
CASES = [
    ("PieFed post behind the PieFed login page", "https://piefed.ca/c/ikillthebear@piefed.ca/p/999061/i-kill-the-bear-official-series-trailer", "https://sh.itjust.works/post/67963857"),
    ("Post on a private Lemmy server", "https://feddit.uk/post/56670482", "https://sh.itjust.works/post/68083955"),
    ("Lemmy post from a Lemmy server", "https://lemmy.ml/post/53817994", "https://sh.itjust.works/post/68083608"),
    ("Lemmy post from a PieFed server", "https://lemmy.ml/post/53818249", "https://sh.itjust.works/post/68083908"),
    ("Lemmy community", "https://lemmy.ml/c/memes", "https://sh.itjust.works/c/memes@lemmy.ml"),
    ("Address with #noredirect", "https://lemmy.ml/c/memes#noredirect", None),
    ("Other site with /post/ path", "https://example.com/post/1", None),
    ("Other site with /u/ path", "https://www.reddit.com/u/spez", None),
]


def settle(driver):
    """Wait until the URL stays the same for 4 s, or until WAIT_S passes."""
    deadline = time.time() + WAIT_S
    last, stable_since = driver.current_url, time.time()
    while time.time() < deadline:
        time.sleep(0.5)
        now = driver.current_url
        if now != last:
            last, stable_since = now, time.time()
        elif time.time() - stable_since >= 4:
            break
    return last


def same(a, b):
    return a.split("#")[0].rstrip("/") == b.split("#")[0].rstrip("/")


def run_case(driver, name, url, expected):
    driver.get(url)
    final = settle(driver)
    ok = same(final, expected) if expected else not final.startswith(HOME)
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {final}")
    if not ok:
        print(f"      expected {expected or 'no redirect to ' + HOME}, title {driver.title!r}")
    return ok


def run_referrer_case(driver, name, target, expected):
    """Leave sh.itjust.works for a remote post, as the link to the original page does.

    Firefox under WebDriver sends no referrer for a navigation from execute_script,
    so the test clicks a real link with ActionChains.
    """
    driver.get(f"{HOME}/robots.txt")
    ff.page(
        driver,
        "const a = document.createElement('a'); a.href = arguments[0]; a.id = 'original';"
        " a.textContent = 'original'; document.body.prepend(a);",
        target,
    )
    ActionChains(driver).move_to_element(driver.find_element(By.ID, "original")).click().perform()
    final = settle(driver)
    referrer = ff.page(driver, "return document.referrer")
    ok = same(final, expected)
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {final} (referrer {referrer!r})")
    return ok


def popup_status(driver, wait_s=15):
    """Wait until the popup status stops showing 'Checking…' and return its class and text."""
    deadline = time.time() + wait_s
    while time.time() < deadline:
        el = driver.find_element(By.ID, "status")
        if el.text and not el.text.startswith("Checking"):
            return el.get_attribute("class"), el.text
        time.sleep(0.3)
    return "timeout", driver.find_element(By.ID, "status").text


def popup_save(driver, popup_url, value):
    driver.get(popup_url)
    popup_status(driver)
    field = driver.find_element(By.ID, "host")
    field.clear()
    field.send_keys(value)
    driver.find_element(By.ID, "save").click()
    time.sleep(0.5)
    return popup_status(driver)


def extension_host(driver, addon_id):
    with driver.context(driver.CONTEXT_CHROME):
        return driver.execute_script("return WebExtensionPolicy.getByID(arguments[0]).mozExtensionHostname", addon_id)


def run_first_start_cases(driver, addon_id, work_tab):
    """After the installation, the settings tab opens, and the add-on does not redirect until the user saves a home."""
    results = []
    settings_url = f"moz-extension://{extension_host(driver, addon_id)}/popup.html"
    settings_tab = None
    deadline = time.time() + 10
    while settings_tab is None and time.time() < deadline:
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            if driver.current_url.startswith(settings_url):
                settings_tab = handle
                break
        else:
            time.sleep(0.5)
    print(f"{'PASS' if settings_tab else 'FAIL'}  Installation opens the settings tab")
    results.append(settings_tab is not None)

    driver.switch_to.window(work_tab)
    target = "https://feddit.uk/post/56670482"
    driver.get(target)
    final = settle(driver)
    ok = final.startswith("https://feddit.uk/")
    print(f"{'PASS' if ok else 'FAIL'}  No redirect before a home instance is saved: {final}")
    results.append(ok)

    driver.switch_to.window(settings_tab or work_tab)
    if not settings_tab:
        driver.get(settings_url)
    kind, text = popup_status(driver)
    hint = driver.find_element(By.CSS_SELECTOR, ".hint").text
    in_tab = "tab" in driver.find_element(By.TAG_NAME, "body").get_attribute("class")
    value = driver.find_element(By.ID, "host").get_attribute("value")
    ok = in_tab and value == "" and hint == "Example: sh.itjust.works" and "Redirects are off" in text
    print(f"{'PASS' if ok else 'FAIL'}  Settings tab is empty with an example: tab layout {in_tab}, hint {hint!r}, {text!r}")
    results.append(ok)

    field = driver.find_element(By.ID, "host")
    field.send_keys("sh.itjust.works")
    driver.find_element(By.ID, "save").click()
    time.sleep(0.5)
    kind, text = popup_status(driver)
    ok = "ok" in kind and text.startswith("Saved")
    print(f"{'PASS' if ok else 'FAIL'}  Settings tab saves sh.itjust.works: {text!r}")
    results.append(ok)
    driver.switch_to.window(work_tab)
    return results


def run_popup_cases(driver, addon_id):
    """The popup shows the home instance, refuses a server without Lemmy and changes the redirect target."""
    popup_url = f"moz-extension://{extension_host(driver, addon_id)}/popup.html"
    results = []

    driver.get(popup_url)
    kind, text = popup_status(driver)
    value = driver.find_element(By.ID, "host").get_attribute("value")
    ok = value == "sh.itjust.works" and "ok" in kind and "Lemmy" in text
    print(f"{'PASS' if ok else 'FAIL'}  Popup shows the saved home instance: {value!r}, {text!r}")
    results.append(ok)

    kind, text = popup_save(driver, popup_url, "example.com")
    driver.get(popup_url)
    popup_status(driver)
    kept = driver.find_element(By.ID, "host").get_attribute("value")
    ok = "error" in kind and kept == "sh.itjust.works"
    print(f"{'PASS' if ok else 'FAIL'}  Popup refuses a server without Lemmy: {text!r}, value after reopen {kept!r}")
    results.append(ok)

    kind, text = popup_save(driver, popup_url, "https://lemmy.ml/")
    driver.get("https://feddit.uk/post/56670482")
    final = settle(driver)
    ok = "ok" in kind and final.startswith("https://lemmy.ml/")
    print(f"{'PASS' if ok else 'FAIL'}  Home instance lemmy.ml from the popup: {text!r}, feddit.uk post -> {final}")
    results.append(ok)

    popup_save(driver, popup_url, "sh.itjust.works")
    return results


def print_install_state(driver, addon_id):
    """Print the signature state and the granted host permissions of the installed add-on."""
    with driver.context(driver.CONTEXT_CHROME):
        state = driver.execute_async_script(
            "const [id, done] = arguments;"
            "const { AddonManager } = ChromeUtils.importESModule('resource://gre/modules/AddonManager.sys.mjs');"
            "AddonManager.getAddonByID(id).then(a => done({"
            "  name: a.name, version: a.version, signedState: a.signedState, active: a.isActive,"
            "  temporary: a.temporarilyInstalled,"
            "  origins: WebExtensionPolicy.getByID(id).allowedOrigins.patterns.map(p => p.pattern),"
            "}));",
            addon_id,
        )
    # AddonManager.SIGNEDSTATE_SIGNED is 2, SIGNEDSTATE_MISSING is 0.
    print(f"Installed {addon_id}: {state}")


def main():
    xpi = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else None
    with ff.session() as driver:
        if xpi:
            addon_id = driver.install_addon(str(xpi), temporary=False)
        else:
            addon_id = driver.install_addon(str(ROOT / "src"), temporary=True)
        time.sleep(3)
        # The start tab of the session can be gone after the installation, so work in a new tab.
        driver.switch_to.window(driver.window_handles[-1])
        driver.switch_to.new_window("tab")
        work_tab = driver.current_window_handle
        print_install_state(driver, addon_id)
        results = run_first_start_cases(driver, addon_id, work_tab)
        results += [run_case(driver, *case) for case in CASES]
        results.append(run_referrer_case(
            driver, "Came from sh.itjust.works", "https://lemmy.ml/post/53817994", "https://lemmy.ml/post/53817994"))
        results.append(run_referrer_case(
            driver, "Came from sh.itjust.works to a private server", "https://feddit.uk/post/56670482",
            "https://feddit.uk/signup"))
        results.extend(run_popup_cases(driver, addon_id))
    print(f"{sum(results)}/{len(results)} passed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
