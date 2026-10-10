# https://github.com/casey/just
set dotenv-load
set shell := ["powershell", "-c"]
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# Install the Node dependencies from package-lock.json
install:
    npm ci

# Check that the versions agree, and check the add-on with the rules of addons.mozilla.org
lint:
    npm run check-version; npm run lint

# Pack src/ into a .zip file in dist/
build:
    npm run build

# Start Firefox with the add-on from src/ and reload it after each change
start:
    npm run start

# Run the end-to-end scenarios in a new Firefox with a clean profile
test:
    uv run --python 3.13 tools/addon_test.py

# Remake the screenshots in docs/screenshots/
screenshots:
    uv run --python 3.13 tools/screenshots.py

# Set the version in package.json, package-lock.json and src/manifest.json, without a git commit
version VERSION:
    npm version {{ VERSION }} --no-git-tag-version --ignore-scripts; node tools/sync-version.mjs

# Send the version to the catalog of addons.mozilla.org: a lasting public record. Needs the API key in .env
sign:
    npm run sign:listed

# Sign the version as unlisted for self-distribution: a lasting record in the account. Needs the API key in .env
sign-unlisted:
    npm run sign

# Show the recipes
help:
    @just --list
