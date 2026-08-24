from __future__ import annotations

from pathlib import Path

from lolpaths.validator import ValidationIssue, validate_rules


def write_rule(rules_dir: Path, name: str, text: str) -> Path:
    path = rules_dir / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")
    return path


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

    ids, issues = validate_rules(rules_dir)

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

    _, issues = validate_rules(rules_dir)

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

    _, issues = validate_rules(rules_dir)

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

    _, issues = validate_rules(rules_dir)

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

    _, issues = validate_rules(rules_dir)

    text = messages(issues)
    assert "match.paths[0].kind" in text
    assert "regex" in text


def test_duplicate_rule_ids_fail(tmp_path: Path) -> None:
    rules_dir = tmp_path / "rules"
    write_rule(rules_dir, "one.yaml", valid_rule("ssh.private-keys"))
    write_rule(rules_dir, "two.yaml", valid_rule("ssh.private-keys"))

    _, issues = validate_rules(rules_dir)

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

    _, issues = validate_rules(rules_dir)

    assert "match" in messages(issues)
    assert "paths" in messages(issues)
