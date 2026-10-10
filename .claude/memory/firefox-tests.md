---
name: firefox-tests
description: Read this file before you run, change or debug `tools/addon_test.py` or `tools/screenshots.py`.
metadata:
  type: project
---

- Both tools start Firefox through `tools/firefox.py` with a clean temporary profile. The profile has no logins, and the add-on needs none, because its requests carry no cookies.
- The start tab of the session can be gone after the installation of the add-on ("Browsing context has been discarded"). Switch to the last handle, then open a new tab for the scenarios.
- Firefox under WebDriver sends no referrer for a navigation from `execute_script`. A scenario that needs the referrer clicks a real link with `ActionChains`.
- Do not set `content.cors.disable`. With it, Firefox fails each cross-origin `fetch`.
- WebDriver cannot open the popup of the toolbar button. `tools/screenshots.py` shows `popup.html` without the `tab` class and saves the `<body>`.
- A screenshot in the chrome context shows the toolbar and the address bar. If a tool takes one, remove the `remotecontrol` attribute of the root element first. Without this step, the address bar has stripes and a robot icon.
- `sh.itjust.works` shows a Cloudflare bot check to a Firefox without its cookies. Never pass a bot check. The screenshots use `lemmy.ml` as the home instance. The redirect scenarios check only the final address, so the bot check does not stop them.
- An installation through WebDriver skips the consent dialog of Firefox. Only an installation by hand shows it.
- A private Lemmy server redirects a guest before the page loads. A redirect scenario with a private server checks the final address, not the page.
