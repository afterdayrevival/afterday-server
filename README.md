# AFTERDAY Server

Independent community server project for **The Day Before**.

Repository: https://github.com/afterdayrevival/afterday-server

## Project layout

The repository is intended to contain:

- `cliente/` — client-side connection and compatibility scripts.
- `host/` — standard host/server runner and scripts.
- `host_otimizado/` — optional optimized host implementation.
- `servicos/` — local service configuration and helper services.
- `launcher/` — desktop launcher, updater and language resources.
- `tools/build_release.py` — creates updater-compatible release assets.
- `.github/workflows/release.yml` — publishes a GitHub Release when a version tag is pushed.

## Important: source and distribution rights

This repository starts with project automation and documentation. Before importing or publicly distributing code from another repository, confirm that you have permission or a license that allows copying, modification and redistribution. A public GitHub repository is not automatically open-source licensed.

Do not add game binaries, game assets, private keys, certificates, player saves, Steam IDs, server IP configuration, logs or personal data.

## Launcher update endpoint

The launcher must use this repository for update checks:

```text
afterdayrevival/afterday-server
```

Its updater downloads these files from the latest GitHub Release:

- `manifesto.json`
- `atualizacao.zip`

The manifest contains a version, ZIP SHA-256, per-file SHA-256 values and release notes. The updater must verify the ZIP and every file before replacing local files.

## Automatic release process

The workflow publishes a release when a tag beginning with `20` is pushed.

Example version:

```powershell
git add .
git commit -m "Prepare AFTERDAY update"
git push origin main

git tag 2026.11.10-1
git push origin 2026.11.10-1
```

GitHub Actions then:

1. Checks out the tagged source.
2. Builds `dist/<version>/manifesto.json` and `atualizacao.zip`.
3. Creates a GitHub Release for the pushed tag.
4. Uploads both assets and marks the release as latest.

The launcher should never include local configuration or player data in an update. The allowlist in `tools/build_release.py` defines which code files are distributed.

## First-time setup

1. Add the authorized project source files.
2. Confirm the updater's repository constant is `afterdayrevival/afterday-server`.
3. Verify the updater's protected paths and release allowlist.
4. Push a test version tag.
5. Check the Actions run and the two assets on the Release page.

GitHub Actions needs only the built-in `GITHUB_TOKEN` with `contents: write`; do not create or commit a personal access token.
