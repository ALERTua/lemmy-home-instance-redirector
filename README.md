# Lemmy Home Instance Redirector

[![CI](https://github.com/ALERTua/lemmy-home-instance-redirector/actions/workflows/ci.yml/badge.svg)](https://github.com/ALERTua/lemmy-home-instance-redirector/actions/workflows/ci.yml)
[![License: GPL-3.0](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](LICENSE)

A Firefox add-on that opens Lemmy and PieFed links on your home Lemmy instance, where you are logged in and can vote, comment and subscribe.

[<img src="docs/get-the-addon.svg" alt="Get the add-on for Firefox" height="60">](https://addons.mozilla.org/firefox/addon/lemmy-home-instance-redirector/)

![The toolbar popup with the home instance sh.itjust.works](docs/screenshots/toolbar-popup.png)

## Features

- Opens posts, comments, communities and users from any Lemmy or PieFed server on your home instance.
- Works past the login page of private Lemmy servers, for example `feddit.uk`, and of PieFed servers that hide their content from guests, for example `piefed.ca`.
- Leaves other sites alone. It checks the page itself and sends no request for a site that is not Lemmy or PieFed.
- Does not redirect when you come from your home instance, for example through the link to the original page. To open one page without a redirect, add `#noredirect` to its address.
- Needs no login data. Its requests carry no cookies.

## Settings

After the installation, the add-on opens its settings page. Enter the host name of your home instance, for example `sh.itjust.works`. The home instance must be a Lemmy server. Links from PieFed servers work, but a PieFed server cannot be the home instance. The add-on checks that the server answers as Lemmy before it saves the value. Until you save a home instance, the add-on does not redirect.

| Settings page | Toolbar popup |
|---|---|
| ![Settings page before the first save](docs/screenshots/settings-empty-light.png) | ![Toolbar popup](docs/screenshots/popup-light.png) |

To change the home instance later, click the add-on button on the toolbar, or open the settings of the add-on in `about:addons`.

## How it works

- A content script runs on addresses with the paths `/post/`, `/comment/`, `/c/` or `/u/`. It reads the `<head>` of the page. A Lemmy page has an inline script that sets `window.isoData`. A PieFed page links the `high_contrast` theme as an alternate stylesheet. On any other site, the content script stops.
- A private server sends a guest from the address of a post to its login page, so the page of the post never loads. The background script watches redirects of top-level pages and catches this case.
- For a found object, the background script asks the server of the page for the ActivityPub ID of the object. Then it asks the home instance for its local copy with `resolve_object`. If the home instance already has the object, the browser opens it directly. If not, the browser opens the search page of the home instance with the ActivityPub ID, and that page fetches the object when you are logged in.

## Privacy

The add-on sends the address of a Lemmy or PieFed page to the server of that page and to your home instance. It sends nothing to the author or to a third party. For details, read [PRIVACY.md](PRIVACY.md).

## Development

You need Node.js 22 or later.

```bash
npm ci
```

| Command | What it does |
|---|---|
| `npm run start` | Starts Firefox with the add-on from `src/` and reloads it after each change. |
| `npm run lint` | Checks the add-on with the rules of addons.mozilla.org. |
| `npm run build` | Packs `src/` into a `.zip` file in `dist/`. |
| `npm run sign:listed` | Sends a new version to the catalog of addons.mozilla.org with the listing data from `amo-metadata.json`. The catalog publishes it after its checks. |
| `npm run sign` | Signs the add-on as unlisted for self-distribution and puts the `.xpi` file into `dist/`. |

The `justfile` gives the same tasks as [just](https://github.com/casey/just) recipes, for example `just lint`, `just test`, `just version 0.1.3` and `just sign`. `just help` lists them.

### Sign a release

1. Copy `.env.example` to `.env`, and fill in the API key from https://addons.mozilla.org/developers/addon/api/key/. Never commit `.env`.
2. Run `npm version <x.y.z>`. It changes `package.json`, copies the version into `src/manifest.json`, and makes a git commit with a tag. addons.mozilla.org refuses a version that it already signed.
3. Add the changes to `CHANGELOG.md`, and the release notes to `version.release_notes` in `amo-metadata.json`.
4. Run `just sign` or `npm run sign:listed`.

### End-to-end tests

`tools/addon_test.py` installs the add-on into Firefox, opens live Lemmy and PieFed pages and prints PASS or FAIL for each scenario. `tools/screenshots.py` makes the screenshots in `docs/screenshots/`. Both scripts start Firefox through Selenium with a clean temporary profile. You need Firefox and [uv](https://docs.astral.sh/uv/).

```bash
uv run --python 3.13 tools/addon_test.py
```

Set `FIREFOX_BIN` to use another Firefox binary, and `FIREFOX_HEADLESS=1` to hide the window.

## License

[GPL-3.0](LICENSE)
