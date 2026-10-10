---
name: amo-signing
description: Read this file before you run or change a sign recipe or script, the API key in `.env`, the version, `src/manifest.json` or `amo-metadata.json`.
metadata:
  type: project
---

- `just sign` (`npm run sign:listed`) and `just sign-unlisted` (`npm run sign`) make a lasting record in the addons.mozilla.org account of the user, also with `--channel unlisted`. `just sign` also makes a public page in the catalog. Never run them, also not as a test. `.env` can hold the real API key at any time. The hook `.claude/hooks/block_sign.py` refuses these commands of an agent.
- Before you give the user the command, say that it makes this lasting record. Then show the user each value that addons.mozilla.org gets, and get the approval of the user for each value. The user runs the command.
- The values from `src/manifest.json` are the ID, the name, the description, the version, the homepage and the icon. The permissions, the data collection declaration and the minimum Firefox version are values too.
- The values from `amo-metadata.json` are the categories, the summary, the full description, the homepage, `requires_payment`, the license and the release notes. The channel is a value too.
- addons.mozilla.org refuses a version that it already signed. A deleted version keeps its number.
- After the owner deletes an add-on on addons.mozilla.org, Firefox soft-blocks its ID. The add-on stops about 30 seconds after the start of Firefox, when Firefox loads the blocklist: `blocklistState` is 1. A temporary add-on with that ID stops too. The ID `lemmy-home-redirect@alexe` is blocked in this way.
- web-ext writes `.amo-upload-uuid` into `src/` during a signature. `.gitignore` keeps it out of git, and web-ext leaves dot files out of the package.
- The manifest declares `data_collection_permissions` with `browsingActivity`, because the add-on sends page addresses to the server of the page and to the home instance. Firefox shows its own consent dialog for this from version 140, so `strict_min_version` is 140. On Android the key works from version 142.
