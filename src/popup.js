'use strict';

const form = document.getElementById('form');
const input = document.getElementById('host');
const save = document.getElementById('save');
const status = document.getElementById('status');

function show(kind, text) {
  status.className = `status ${kind}`;
  status.textContent = text;
}

function describe(host, site) {
  return `${host} · Lemmy ${site.version}`;
}

async function showCurrent() {
  // tabs.getCurrent() gives a tab only when the page is open in a tab, not in the toolbar popup.
  if (await browser.tabs.getCurrent()) document.body.classList.add('tab');
  const home = await getHome();
  if (!home) {
    show('', 'No home instance yet. Redirects are off.');
    input.focus();
    return;
  }
  input.value = home;
  show('', 'Checking…');
  const site = await lemmySite(home);
  if (site) show('ok', describe(home, site));
  else show('error', `${home} does not answer as a Lemmy server`);
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const host = normalizeHost(input.value);
  if (!host) {
    show('error', 'Enter a server name, for example sh.itjust.works');
    return;
  }
  input.value = host;
  save.disabled = true;
  show('', 'Checking…');
  const site = await lemmySite(host);
  save.disabled = false;
  if (!site) {
    show('error', `${host} does not answer as a Lemmy server. Nothing saved.`);
    return;
  }
  await browser.storage.local.set({ home: host });
  show('ok', `Saved · ${describe(host, site)}`);
});

showCurrent();
