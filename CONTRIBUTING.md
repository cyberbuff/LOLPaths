# Contributing to LOLPaths

Thanks for helping improve LOLPaths. The source of truth is YAML under
`rules/`.

## Add a Rule

1. Select the broad category, such as `cloud`, `ssh`, or `package-manager`.
2. Create or update one logical artifact rule.
3. Add platform-specific paths under each path matcher.
4. Add content indicators only when they are well supported.
5. Choose sensitivity conservatively.
6. Add reliable references or provenance when available.
7. Run:

```bash
uv run lolpaths validate
uv run lolpaths generate
uv run pytest -q
```

## Naming

Rule IDs are lowercase identifiers using dots and hyphens:

```text
cloud.aws.credentials
ssh.private-keys
kubernetes.service-account-token
```

Do not create a new top-level category for each product. Use `subcategory` for
vendors, tools, and technologies.

## Safety

Do not submit rules or tests that include real credentials, private keys,
tokens, cookies, wallet seeds, or customer data. Examples should use metadata,
path templates, and harmless strings only.
