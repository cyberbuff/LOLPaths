from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


@dataclass(frozen=True)
class ValidationIssue:
    message: str
    file: Path | None = None


def validate_rule_file(path: Path, schema_path: Path) -> tuple[str | None, list[ValidationIssue]]:
    schema = _load_schema(schema_path)
    rule, issues = _load_rule(path)
    if issues:
        return None, issues
    assert rule is not None

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(rule), key=lambda error: list(error.absolute_path))
    issues = [_schema_issue(path, error) for error in errors]
    issues.extend(_regex_issues(path, rule))
    rule_id = rule.get("id") if isinstance(rule.get("id"), str) else None
    return rule_id, issues


def validate_rules(rules_dir: Path, schema_path: Path) -> tuple[list[str], list[ValidationIssue]]:
    ids: list[str] = []
    seen: dict[str, Path] = {}
    issues: list[ValidationIssue] = []

    for path in _rule_files(rules_dir):
        rule_id, file_issues = validate_rule_file(path, schema_path)
        issues.extend(file_issues)
        if rule_id is None:
            continue
        ids.append(rule_id)
        if rule_id in seen:
            issues.append(
                ValidationIssue(f'duplicate rule id "{rule_id}" also used in {seen[rule_id]}', path)
            )
        else:
            seen[rule_id] = path

    return sorted(ids), issues


def load_valid_rules(rules_dir: Path, schema_path: Path) -> list[dict[str, Any]]:
    _, issues = validate_rules(rules_dir, schema_path)
    if issues:
        raise ValueError(_format_issues(issues))

    rules: list[dict[str, Any]] = []
    for path in _rule_files(rules_dir):
        rule, file_issues = _load_rule(path)
        if file_issues or not isinstance(rule, dict):
            raise ValueError(_format_issues(file_issues))
        rules.append(rule)
    return sorted(rules, key=lambda rule: rule["id"])


def format_issues(issues: list[ValidationIssue]) -> str:
    return _format_issues(issues)


def _rule_files(rules_dir: Path) -> list[Path]:
    if not rules_dir.exists():
        return []
    files = [*rules_dir.rglob("*.yaml"), *rules_dir.rglob("*.yml")]
    return sorted(path for path in files if path.is_file())


def _load_schema(schema_path: Path) -> dict[str, Any]:
    import json

    return json.loads(schema_path.read_text(encoding="utf-8"))


def _load_rule(path: Path) -> tuple[dict[str, Any] | None, list[ValidationIssue]]:
    try:
        rule = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        return None, [ValidationIssue(f"invalid YAML: {error}", path)]

    if not isinstance(rule, dict):
        return None, [ValidationIssue("rule must be a YAML mapping", path)]
    return rule, []


def _schema_issue(path: Path, error: ValidationError) -> ValidationIssue:
    field = _field_path(error)
    return ValidationIssue(f"{field}: {error.message}", path)


def _field_path(error: ValidationError) -> str:
    parts: list[str] = []
    for part in error.absolute_path:
        if isinstance(part, int):
            if parts:
                parts[-1] = f"{parts[-1]}[{part}]"
            else:
                parts.append(f"[{part}]")
        else:
            parts.append(str(part))
    return ".".join(parts) if parts else "(root)"


def _regex_issues(path: Path, rule: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    match = rule.get("match")
    if not isinstance(match, dict):
        return issues

    content = match.get("content", {})
    regexes = content.get("regex", []) if isinstance(content, dict) else []
    if isinstance(regexes, list):
        for index, pattern in enumerate(regexes):
            issues.extend(_compile_regex(path, f"match.content.regex[{index}]", pattern))
    return issues


def _compile_regex(path: Path, field: str, pattern: object) -> list[ValidationIssue]:
    if not isinstance(pattern, str):
        return []
    try:
        re.compile(pattern)
    except re.error as error:
        return [ValidationIssue(f"{field}: invalid regex: {error}", path)]
    return []


def _format_issues(issues: list[ValidationIssue]) -> str:
    lines: list[str] = []
    for issue in issues:
        prefix = f"{issue.file}\n  " if issue.file else ""
        lines.append(f"{prefix}{issue.message}")
    return "\n".join(lines)
