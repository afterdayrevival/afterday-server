# AFTERDAY Launcher update configuration

The launcher should use the repository:

```text
afterdayrevival/afterday-server
```

The local `config.json` may contain a `repo` property. If it is present, it overrides the updater default. Use `config.example.json` as the safe template; copy it to `config.json` locally only when needed. The local config is ignored by Git.

Update manifest URL:

```text
https://github.com/afterdayrevival/afterday-server/releases/latest/download/manifesto.json
```

Version-pinned update ZIP URL:

```text
https://github.com/afterdayrevival/afterday-server/releases/download/<VERSION>/atualizacao.zip
```

Release assets required by the updater:

- `manifesto.json`
- `atualizacao.zip`

The updater verifies the ZIP SHA-256 and each file hash before applying any changes. Never add local player identity, server address, configuration, saves, logs, certificates or private keys to a release package.
