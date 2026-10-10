'use strict';

// The add-on does nothing until the user sets a home instance, so ask for it at once.
browser.runtime.onInstalled.addListener(({ reason }) => {
  if (reason === 'install') browser.runtime.openOptionsPage();
});

// The background script makes the requests, because its host permission lifts CORS.
browser.runtime.onMessage.addListener((message) => {
  if (message?.type !== 'home-url') return undefined;
  return homeUrlForPage(message.url, message.referrer);
});

// Returns the address on the home instance for a page that the content script found, or null.
async function homeUrlForPage(pageUrl, referrer) {
  const home = await getHome();
  if (!home) return null;
  const url = new URL(pageUrl);
  if (url.host === home || url.hash.includes('noredirect')) return null;
  // The "original" link on the home instance leads here. The user wants the original page then.
  if (referrer && new URL(referrer).host === home) return null;
  const target = classify(url);
  return target ? homeUrl(target, home) : null;
}

// A private server sends a guest from the address of an object to its login page.
// The page of the object never loads, so only this listener sees the original address.
const handledTabs = new Map();

browser.webRequest.onBeforeRedirect.addListener(
  async (details) => {
    const from = new URL(details.url);
    const to = new URL(details.redirectUrl, details.url);
    if (!isLoginWall(from, to)) return;
    const home = await getHome();
    if (!home || from.host === home) return;
    // The "original" link on the home instance leads here. The user wants the original page then.
    if (details.originUrl && new URL(details.originUrl).host === home) return;
    // One navigation can pass the same redirect again, for example after a bot check.
    if (handledTabs.get(details.tabId) === details.url) return;
    handledTabs.set(details.tabId, details.url);
    try {
      const url = await homeUrl(classify(from), home);
      await browser.tabs.update(details.tabId, { url });
    } finally {
      handledTabs.delete(details.tabId);
    }
  },
  { urls: ['https://*/*'], types: ['main_frame'] },
);
