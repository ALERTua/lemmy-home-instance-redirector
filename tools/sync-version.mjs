// Copies the version of package.json into src/manifest.json, so that the version lives in one place.
// `npm version <x.y.z>` runs it through the "version" script. With --check, it only fails when the two differ.
import { readFile, writeFile } from 'node:fs/promises';

const MANIFEST = 'src/manifest.json';
// The quote before "version" keeps the pattern away from "manifest_version".
const VERSION_FIELD = /("version"\s*:\s*")([^"]*)(")/;

const { version } = JSON.parse(await readFile('package.json', 'utf8'));
const text = await readFile(MANIFEST, 'utf8');
const current = text.match(VERSION_FIELD)?.[2];

if (process.argv.includes('--check')) {
  if (current !== version) {
    console.error(`${MANIFEST} has version ${current}, but package.json has ${version}. Run: npm version ${version}`);
    process.exit(1);
  }
  console.log(`Version ${version} agrees in package.json and ${MANIFEST}.`);
} else if (current !== version) {
  await writeFile(MANIFEST, text.replace(VERSION_FIELD, `$1${version}$3`));
  console.log(`${MANIFEST}: ${current} -> ${version}`);
}
