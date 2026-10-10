// Runs at document_start on the paths of Lemmy and PieFed objects on any site.
// The background script decides about the home instance and makes the requests.
'use strict';

(async () => {
  if (location.hash.includes('noredirect')) return;
  if (!classify(new URL(location.href))) return;

  await headParsed();
  if (!isLemmyOrPiefed()) return;

  const to = await browser.runtime.sendMessage({
    type: 'home-url',
    url: location.href,
    referrer: document.referrer,
  });
  if (to) location.replace(to);
})();
