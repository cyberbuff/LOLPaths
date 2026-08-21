from __future__ import annotations

from pathlib import Path

from lolpaths.validator import ValidationIssue, load_valid_rules, validate_rules


def write_rule(rules_dir: Path, name: str, text: str) -> Path:
    path = rules_dir / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return path


def schema_path() -> Path:
    return Path(__file__).resolve().parents[1] / "schema" / "lolpaths.schema.json"


def valid_rule(rule_id: str = "cloud.aws.credentials") -> str:
    return f"""
schema_version: 1
id: {rule_id}
name: AWS CLI Credentials
category: cloud
sensitivity: critical
match:
  paths:
    - path: "windows-sample-credentials"
      kind: file
      platforms: [windows]
    - path: "unix-sample-credentials"
      kind: file
      platforms: [linux, macos]
  content:
    contains:
      - aws_access_key_id
    regex:
      - '(?i)aws_secret_access_key\\s*='
metadata:
  confidence: high
"""


def messages(issues: list[ValidationIssue]) -> str:
    return "\n".join(issue.message for issue in issues)


def test_valid_rule_with_platform_specific_paths_passes(tmp_path: Path) -> None:
    rules_dir = tmp_path / "rules"
    write_rule(rules_dir, "cloud/aws/credentials.yaml", valid_rule())

    ids, issues = validate_rules(rules_dir, schema_path())

    assert ids == ["cloud.aws.credentials"]
    assert issues == []


def test_missing_required_field_fails(tmp_path: Path) -> None:
    rules_dir = tmp_path / "rules"
    write_rule(
        rules_dir,
        "bad.yaml",
        """
schema_version: 1
id: ssh.private-keys
name: SSH Private Keys
category: ssh
match:
  paths:
    - path: "sample-key-glob"
      kind: glob
      platforms: [linux, macos]
""",
    )

    _, issues = validate_rules(rules_dir, schema_path())

    assert "sensitivity" in messages(issues)


def test_invalid_enums_fail(tmp_path: Path) -> None:
    rules_dir = tmp_path / "rules"
    write_rule(
        rules_dir,
        "bad.yaml",
        valid_rule().replace("category: cloud", "category: product"),
    )
    write_rule(
        rules_dir,
        "bad2.yaml",
        valid_rule("ssh.bad").replace("sensitivity: critical", "sensitivity: severe"),
    )
    write_rule(
        rules_dir,
        "bad3.yaml",
        valid_rule("ssh.bad-kind").replace("kind: file", "kind: shortcut", 1),
    )
    write_rule(
        rules_dir,
        "bad4.yaml",
        valid_rule("ssh.bad-platform").replace("platforms: [linux, macos]", "platforms: [unix]", 1),
    )

    _, issues = validate_rules(rules_dir, schema_path())

    text = messages(issues)
    assert "category" in text
    assert "sensitivity" in text
    assert "kind" in text
    assert "platforms" in text


def test_invalid_regexes_fail(tmp_path: Path) -> None:
    rules_dir = tmp_path / "rules"
    write_rule(
        rules_dir,
        "bad-content-regex.yaml",
        valid_rule("cloud.aws.bad-regex").replace(
            "(?i)aws_secret_access_key\\s*=", "[unterminated"
        ),
    )

    _, issues = validate_rules(rules_dir, schema_path())

    text = messages(issues)
    assert "match.content.regex[0]" in text


def test_path_regex_kind_fails(tmp_path: Path) -> None:
    rules_dir = tmp_path / "rules"
    write_rule(
        rules_dir,
        "path-regex.yaml",
        valid_rule()
        .replace('path: "windows-sample-credentials"', "path: '.*credentials$'", 1)
        .replace("kind: file", "kind: regex", 1),
    )

    _, issues = validate_rules(rules_dir, schema_path())

    text = messages(issues)
    assert "match.paths[0].kind" in text
    assert "regex" in text


def test_duplicate_rule_ids_fail(tmp_path: Path) -> None:
    rules_dir = tmp_path / "rules"
    write_rule(rules_dir, "one.yaml", valid_rule("ssh.private-keys"))
    write_rule(rules_dir, "two.yaml", valid_rule("ssh.private-keys"))

    _, issues = validate_rules(rules_dir, schema_path())

    assert "duplicate rule id" in messages(issues)


def test_content_only_rule_requires_paths(tmp_path: Path) -> None:
    rules_dir = tmp_path / "rules"
    write_rule(
        rules_dir,
        "content.yaml",
        """
schema_version: 1
id: application.env-secrets
name: Environment Secrets
category: application
sensitivity: high
match:
  content:
    contains:
      - SECRET_KEY=
""",
    )

    _, issues = validate_rules(rules_dir, schema_path())

    assert "match" in messages(issues)
    assert "paths" in messages(issues)


def test_catalog_includes_databricks_config_rule() -> None:
    rules = load_valid_rules(Path("rules"), schema_path())
    rule_ids = {rule["id"] for rule in rules}

    assert "cloud.databricks.config" in rule_ids


def test_catalog_covers_requested_secret_artifacts() -> None:
    rules = load_valid_rules(Path("rules"), schema_path())
    rule_ids = {rule["id"] for rule in rules}

    assert {
        "cloud.aws.imds-credentials",
        "remote-access.netrc",
        "remote-access.lftp-config",
        "email.msmtp-config",
        "database.mongodb-shell-config",
        "database.mongodb-shell-global-config",
        "cloud.mongodb.cli-config",
        "cloud.mongodb-atlas.cli-config",
        "identity.ldap-client-config",
        "crypto-wallet.bitcoin.wallets",
        "crypto-wallet.litecoin.wallets",
        "crypto-wallet.dogecoin.wallets",
        "crypto-wallet.zcash.wallets",
        "crypto-wallet.dash.wallets",
        "crypto-wallet.ripple.wallets",
        "crypto-wallet.monero.wallets",
        "crypto-wallet.ethereum.keystore",
        "crypto-wallet.cardano.wallets",
        "crypto-wallet.solana.config",
        "cicd.gitlab-ci.config",
        "cicd.travis-ci.config",
        "cicd.jenkinsfile.config",
        "cicd.drone.config",
        "cicd.anchor.config",
        "infrastructure.terraform-variable-files",
    } <= rule_ids
    assert "cicd.pipeline-configs" not in rule_ids
    assert "crypto-wallet.common-wallets" not in rule_ids


def test_catalog_covers_litellm_compromise_artifact_paths() -> None:
    rules = load_valid_rules(Path("rules"), schema_path())
    rule_ids = {rule["id"] for rule in rules}

    assert {
        "ssh.host-private-keys",
        "kubernetes.service-account-ca-certificate",
        "kubernetes.service-account-namespace",
        "containers.runtime-secret-files",
        "vpn.wireguard-config",
        "kubernetes.helm-directory",
        "system.environment-file",
        "system.passwd-file",
        "system.shadow-file",
        "system.ssh-auth-logs",
        "email.postfix-sasl-passwords",
        "identity.ldap-server-config",
        "database.redis-config",
        "crypto-wallet.solana.keypair-files",
        "crypto-wallet.solana.ledger-files",
    } <= rule_ids
