---
name: lemmy-piefed
description: Read this file before you change how the add-on finds a page, finds an ActivityPub ID, resolves an object or detects a login wall.
metadata:
  type: project
---

## Find a Lemmy or PieFed page

- lemmy-ui starts `<head>` with an inline script that sets `window.isoData`.
- PieFed links `/static/themes/high_contrast/styles.css` as an alternate stylesheet in `<head>`. The template `app/templates/base.html` of PieFed adds it without a condition.
- The check reads only `<head>`, after the parser reaches `<body>`. It sends no request, so a site that is not Lemmy or PieFed sees nothing.

## Find the ActivityPub ID

- A Lemmy server shows a post of another server under its own number. A request with `Accept: application/activity+json` gets a 308 redirect to the original server, and `fetch` follows it.
- PieFed uses the long address `/c/<name>/p/<id>/<slug>` as the ActivityPub ID. It answers `/post/<id>` with the same long ID.
- The ActivityPub request passes the Anubis bot check of PieFed. The HTML page does not.
- The ActivityPub ID of a community or a user is `https://<host>/c/<name>` or `https://<host>/u/<name>` on Lemmy and on PieFed.

## Resolve on the home instance

- `resolve_object` without a login finds only the objects that the home instance already stores. A handle such as `!name@host` does not resolve without a login. The URL of the actor resolves.
- The search page of lemmy-ui calls `resolveObject` when the user is logged in, so an unknown object appears as the first result.
- The Lemmy API sends CORS headers for each origin.

## Login walls

- A private Lemmy server, for example `feddit.uk`, answers a post address with `302 Location: /signup`, without the path of the post. Only `webRequest.onBeforeRedirect` sees the original address.
- PieFed, for example `piefed.ca`, sends a guest to `/auth/login?next=/post/<id>`. The `next` value can point to another host, so `classify` takes only a path that starts with one `/`.
