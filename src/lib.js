// Shared by the content script, the background script and the popup.
'use strict';

const TIMEOUT_MS = 5000;
const AP_ACCEPT = 'application/activity+json';
// Paths where a server that hides its content from guests sends them.
// Lemmy uses /signup or /login, PieFed uses /auth/login.
const LOGIN_WALL_PATHS = new Set(['/signup', '/login', '/auth/login']);

// Returns null for pages that show no single object, for example the front page or the login page.
// `apId` is the first guess for the ActivityPub ID. When `lookup` is true, the server
// of the page can report a different ID, for example for a post that came from another server.
function classify(url) {
  // A PieFed server that hides its content from guests sends them to /auth/login?next=<object path>.
  if (url.pathname === '/auth/login') {
    const next = url.searchParams.get('next');
    const isLocalPath = next?.startsWith('/') && !next.startsWith('//');
    return isLocalPath ? classify(new URL(next, url.origin)) : null;
  }
  const path = url.pathname.replace(/\/+$/, '');
  let m;
  if ((m = path.match(/^\/(c|u)\/([^/@]+)(?:@([^/]+))?$/))) {
    const host = m[3] || url.host;
    return { kind: m[1], apId: `https://${host}/${m[1]}/${m[2]}`, lookup: false };
  }
  if ((m = path.match(/^\/post\/(\d+)/))) {
    return { kind: 'post', apId: `${url.origin}/post/${m[1]}`, lookup: true };
  }
  if (/^\/c\/[^/]+\/p\/\d+/.test(path)) {
    return { kind: 'post', apId: url.origin + url.pathname, lookup: true };
  }
  if ((m = path.match(/^\/comment\/(\d+)$/))) {
    return { kind: 'comment', apId: `${url.origin}/comment/${m[1]}`, lookup: true };
  }
  return null;
}

// True when a server answers the address of an object with a redirect to its own login page.
function isLoginWall(from, to) {
  return from.host === to.host && LOGIN_WALL_PATHS.has(to.pathname) && classify(from) !== null;
}

// The check reads only the page itself and sends no request.
// lemmy-ui starts <head> with an inline script that sets window.isoData.
// PieFed always links its high_contrast theme as an alternate stylesheet.
function isLemmyOrPiefed() {
  const head = document.head;
  if (!head) return false;
  if (head.querySelector('link[rel="alternate stylesheet"][href^="/static/themes/high_contrast/"]')) {
    return true;
  }
  return [...head.querySelectorAll('script:not([src])')].some((s) =>
    s.textContent.includes('window.isoData'),
  );
}

// Resolves when the parser reaches <body>, so that <head> is complete.
function headParsed() {
  return new Promise((resolve) => {
    if (document.body) return resolve();
    const observer = new MutationObserver(() => {
      if (!document.body) return;
      observer.disconnect();
      resolve();
    });
    observer.observe(document, { childList: true, subtree: true });
  });
}

// Resolves to the parsed JSON body, or to null on an error, a timeout or a non-2xx status.
async function getJson(url, accept) {
  try {
    const r = await fetch(url, {
      headers: { Accept: accept },
      credentials: 'omit',
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
    return r.ok ? await r.json() : null;
  } catch {
    return null;
  }
}

// Lemmy answers a post of another server with a redirect to that server,
// and fetch follows it. PieFed answers /post/<id> with the long /c/<name>/p/<id>/<slug> ID.
async function lookupApId(guess) {
  const doc = await getJson(guess, AP_ACCEPT);
  return typeof doc?.id === 'string' ? doc.id : guess;
}

// The host of the home instance, for example "sh.itjust.works", or null before the user sets it.
// The settings page stores it.
async function getHome() {
  const { home } = await browser.storage.local.get('home');
  return home || null;
}

// Turns "sh.itjust.works", "https://sh.itjust.works/" or a full address into a host, or null.
function normalizeHost(text) {
  const value = text.trim();
  if (!value) return null;
  try {
    const url = new URL(/^[a-z]+:\/\//i.test(value) ? value : `https://${value}`);
    return url.host.includes('.') ? url.host.toLowerCase() : null;
  } catch {
    return null;
  }
}

// Resolves to { name, version } when the host answers as a Lemmy server, else to null.
async function lemmySite(host) {
  const site = await getJson(`https://${host}/api/v3/site`, 'application/json');
  const name = site?.site_view?.site?.name;
  return name && site.version ? { name, version: site.version } : null;
}

function actorHandle(actor, home) {
  const host = new URL(actor.actor_id).host;
  return host === home ? actor.name : `${actor.name}@${host}`;
}

function homePath(resolved, home) {
  if (resolved?.post) return `/post/${resolved.post.post.id}`;
  if (resolved?.comment) return `/comment/${resolved.comment.comment.id}`;
  if (resolved?.community) return `/c/${actorHandle(resolved.community.community, home)}`;
  if (resolved?.person) return `/u/${actorHandle(resolved.person.person, home)}`;
  return null;
}

// Returns the address on the home instance for an object from classify().
async function homeUrl(target, home) {
  const apId = target.lookup ? await lookupApId(target.apId) : target.apId;
  // The request carries no cookies, so the home instance finds only the objects that it already stores.
  const resolved = await getJson(
    `https://${home}/api/v3/resolve_object?q=${encodeURIComponent(apId)}`,
    'application/json',
  );
  const path = homePath(resolved, home);
  // When the user is logged in, the search page of Lemmy fetches an unknown object from its server.
  return path
    ? `https://${home}${path}`
    : `https://${home}/search?q=${encodeURIComponent(apId)}&type=All`;
}
