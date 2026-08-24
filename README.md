# LOLPaths

**LOLPaths** is a community-maintained catalog of filesystem paths and file
characteristics associated with credentials, secrets, tokens, private keys,
configuration, authentication artifacts, and other sensitive files.

LOLPaths provides normalized, machine-readable YAML that can be used for
detection engineering, secret scanning, DLP, EDR monitoring, security
validation, and filesystem guardrails.

## Why This Exists

Sensitive artifacts are spread across cloud CLIs, SSH, package managers,
databases, CI/CD systems, browsers, shells, developer tools, and local
configuration. LOLPaths gives defenders and tool builders one conservative,
human-readable source of truth for where those artifacts commonly live and how
they can be classified.

LOLPaths is a catalog, not an exploitation framework. It does not replay
credentials, log in to accounts, crack passwords, transfer wallet funds, or
dump secret contents.

## Quick Start

```bash
uv sync
uv run lolpaths validate
uv run lolpaths generate
uv run pytest -q
```

Useful read-only queries:

```bash
uv run lolpaths list
uv run lolpaths list --platform windows
uv run lolpaths list --category cloud
uv run lolpaths show ssh.private-keys
```

## Rule Example

```yaml
schema_version: 1
id: ssh.private-keys
name: SSH Private Keys
category: ssh
artifact_types:
  - credential
  - private-key
sensitivity: critical
match:
  paths:
    - path: '%USERPROFILE%\.ssh\id_*'
      kind: glob
      platforms: [windows]
    - path: "$HOME/.ssh/id_*"
      kind: glob
      platforms: [linux, macos]
  content:
    regex:
      - '-----BEGIN OPENSSH PRIVATE KEY-----'
```

## Data Model

Rules describe logical artifacts, not one-off paths. Platform restrictions live
on each path matcher so one rule can model Windows, Linux, and macOS locations
for the same artifact.

Top-level categories stay broad, such as `cloud`, `ssh`, `database`,
`package-manager`, and `cicd`. Product names belong in `subcategory`.
Sensitivity describes exposure risk: `critical`, `high`, `medium`, `low`, or
`informational`.

## Generated Artifacts

Path matchers are mandatory and use `file`, `directory`, and `glob`; content
matchers may add literal strings or regexes.

Generated files are derived from YAML and should not be edited manually:

- `generated/windows.txt`
- `generated/linux.txt`
- `generated/macos.txt`
- `docs/public/api/rules.json`
- `docs/public/api/stats.json`
- `docs/content/docs/<rule path>.mdx`

Run `uv run lolpaths generate` after changing rules.

## Documentation

The Fumadocs app lives in [docs](docs/README.md). Its source pages are:

- [Introduction](docs/content/docs/index.mdx)
- [Rule format](docs/content/docs/rule-format.mdx)
- [Matching semantics](docs/content/docs/matching-semantics.mdx)
- [Generated artifacts](docs/content/docs/generated-artifacts.mdx)

When the docs app is running, LLM-friendly output is available at
`/llms-full.txt`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Add or update one logical artifact rule,
choose sensitivity conservatively, include provenance when possible, then run:

```bash
uv run lolpaths validate
uv run lolpaths generate
uv run pytest -q
```

## License

MIT. See [LICENSE](LICENSE).
