# AGENTS.md

Guidance for AI coding agents in this repository. Make small changes, make sure that each claim agrees with the code, and obey the boundaries at the end.

## Project memory

The traps and the decisions with their reasons are in the project memory. Before you start a task, read this file: [.claude/memory/MEMORY.md](.claude/memory/MEMORY.md).

## Project overview

Lemmy Home Instance Redirector is a Firefox add-on (Manifest V3). It opens Lemmy and PieFed posts, comments, communities and users from any server on the home Lemmy instance of the user. The user sets the home instance on the settings page, which opens after the installation. `README.md` gives the user view, and `PRIVACY.md` tells what the add-on sends and to which server.

## Repository layout

| Path | What it holds |
|---|---|
| `src/manifest.json` | the manifest: ID, version, permissions, data collection, content script matches |
| `src/lib.js` | the shared logic: `classify`, `isLoginWall`, `isLemmyOrPiefed`, `getHome`, `homeUrl` |
| `src/content.js` | finds a Lemmy or PieFed page by its `<head>` and asks the background script for the target |
| `src/background.js` | makes all network requests, catches the login wall of private servers, opens the settings after the installation |
| `src/popup.html`, `popup.css`, `popup.js` | the toolbar popup, and the same page as the settings tab |
| `src/icons/icon.svg` | the icon |
| `tools/addon_test.py` | end-to-end scenarios in a driven Firefox |
| `tools/screenshots.py` | makes `docs/screenshots/` |
| `tools/render_icon.py` | renders `src/icons/icon.svg` into `docs/icon-128.png`, the PNG icon of the catalog listing |
| `web-ext-config.mjs` | source folder `src/` and artifact folder `dist/` for web-ext |
| `.github/workflows/ci.yml` | lint with warnings as errors, and build |

## Commands

Use the recipes of `justfile`. Run each command from the repository root. `just help` lists the recipes.

- `just install`: after a clone, and after a change of `package-lock.json`.
- `just lint`: after each change in `src/`. It checks that the versions agree and runs `web-ext lint --warnings-as-errors`. CI runs the same checks.
- `just build`: to make sure that web-ext packs `src/`.
- `just start`: to try a change in a new Firefox by hand.
- `just version <x.y.z>`: to change the version in `package.json`, `package-lock.json` and `src/manifest.json`. It makes no git commit and runs no `git add`. Do not use a bare `npm version`: its `version` script runs `git add`, and it makes a git commit and a tag.
- `just test`: after each change of the behavior. It needs Firefox. `tools/firefox.py` starts it with a clean temporary profile.
- `uv run --python 3.13 tools/addon_test.py dist/<file>.xpi`: to test a signed `.xpi` as a permanent add-on.
- `just screenshots`: after a change that the screenshots show.
- `just icon`: after a change of `src/icons/icon.svg`. Then the user uploads `docs/icon-128.png` in the Developer Hub.
- `just sign` and `just sign-unlisted`: only the user runs them. See the agent boundaries.

## Code style

- Plain JavaScript without a build step and without dependencies in `src/`. The content script and the background script share `lib.js` as a classic script, not as a module.
- The background script makes each network request. The content script makes none, because the host permission lifts CORS only for the background script.
- A comment states a rule or a constraint. It never refers to a plan, an issue number or a review round.
- Write only English in the code, the comments, the documentation and the commit messages.

## Testing

- Each change of the behavior gets a scenario in `tools/addon_test.py`. The scenario opens a live page and checks the final address.
- Prove each new scenario that protects a check or a branch of the code with a mutation. Examples are a skip, a guard and a fallback. Break the protected line in a copy of `src/`, and make sure that the scenario fails.

## Agent boundaries

- Never run `just sign`, `just sign-unlisted`, `npm run sign`, `npm run sign:listed` or another command that sends the add-on to addons.mozilla.org. The user runs it after the approval of each value that the service gets. Read the project memory about signing first. The hook `.claude/hooks/block_sign.py` refuses such a command of an agent.
- Never run a git command that changes the repository (`add`, `commit`, `push`, `reset`, `checkout`, `stash`, `restore`) unless the user asks for it.
- Never change the add-on ID `lemmy-home-instance-redirector@alert` in `src/manifest.json`. An ID never comes back after a deletion on addons.mozilla.org.
- Ask the user before you change a permission, the data collection declaration or the minimum Firefox version.
