# Privacy policy

Lemmy Home Instance Redirector has no server of its own, no analytics and no tracking.

## What the add-on stores

The add-on stores one value in the local storage of Firefox: the host name of your home instance, for example `sh.itjust.works`. This value stays on your computer.

## What the add-on sends

The add-on sends a request only when you open a page of a post, a comment, a community or a user on a Lemmy or PieFed server. It sends the address of that page to two servers:

- The server of the page. The add-on asks it for the ActivityPub ID of the object.
- Your home instance. The add-on asks it for its local copy of the object, and when you save a home instance, it asks for the version of Lemmy.

The add-on sends these requests without cookies, so neither server learns your login from them. Each of these servers can see your IP address and the address of the page, as for each other request that your browser makes.

Firefox shows this transmission as "browsing activity" when you install the add-on.

## What the add-on does not do

- It does not read, store or send your login on any server.
- It does not read the content of other sites. On a page with a path such as `/post/` or `/c/`, the add-on looks at the `<head>` of the page to find out if the site is Lemmy or PieFed. Firefox also tells the add-on the addresses of redirects between pages. For other sites, the add-on sends nothing.
- It sends no data to the author of the add-on or to any third party.
