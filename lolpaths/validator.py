from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Annotated, Any, Literal, TypeAlias

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

Identifier = Annotated[str, Field(pattern=r"^[a-z0-9]+(?:[.-][a-z0-9]+)*$")]
NonEmptyString = Annotated[str, Field(min_length=1)]
NonEmptyStrings = Annotated[list[NonEmptyString], Field(min_length=1)]

Category: TypeAlias = Literal[
    "cloud",
    "ssh",
    "source-control",
    "containers",
    "kubernetes",
    "cicd",
    "package-manager",
    "database",
    "secret-manager",
    "infrastructure",
    "certificates",
    "shell",
    "browser",
    "email",
    "vpn",
    "remote-access",
    "application",
    "crypto-wallet",
    "identity",
    "system",
    "development",
]
ArtifactType: TypeAlias = Literal[
    "credential",
    "token",
    "api-key",
    "private-key",
    "certificate",
    "configuration",
    "history",
    "database",
    "wallet",
    "session",
    "cookie",
    "connection-string",
    "password-store",
    "backup",
    "state-file",
    "environment",
]
Sensitivity: TypeAlias = Literal["critical", "high", "medium", "low", "informational"]
Platform: TypeAlias = Literal["windows", "linux", "macos"]
PathKind: TypeAlias = Literal["file", "directory", "glob"]
Environment: TypeAlias = Literal[
    "workstation",
    "server",
    "container",
    "cicd-runner",
    "kubernetes-node",
    "development",
    "cloud-host",
]
SourceType: TypeAlias = Literal[
    "vendor-documentation",
    "upstream",
    "research",
    "incident",
    "community",
    "other",
]
Confidence: TypeAlias = Literal["high", "medium", "low"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class PathMatcher(StrictModel):
    path: NonEmptyString
    kind: PathKind
    platforms: Annotated[list[Platform], Field(min_length=1)]

    @field_validator("platforms", mode="after")
    @classmethod
    def _unique_platforms(cls, values: list[Platform]) -> list[Platform]:
        return _unique(values)


class ContentMatcher(StrictModel):
    contains: NonEmptyStrings | None = None
    regex: NonEmptyStrings | None = None

    @field_validator("contains", "regex", mode="after")
    @classmethod
    def _unique_values(cls, values: NonEmptyStrings | None) -> NonEmptyStrings | None:
        return _unique(values) if values is not None else None

    @model_validator(mode="after")
    def _has_matcher(self) -> ContentMatcher:
        if self.contains is None and self.regex is None:
            raise ValueError("at least one of contains or regex is required")
        return self


class Match(StrictModel):
    paths: Annotated[list[PathMatcher], Field(min_length=1)]
    content: ContentMatcher | None = None


class Credentials(StrictModel):
    types: NonEmptyStrings | None = None

    @field_validator("types", mode="after")
    @classmethod
    def _unique_types(cls, values: NonEmptyStrings | None) -> NonEmptyStrings | None:
        return _unique(values) if values is not None else None


class Impact(StrictModel):
    credential_access: bool | None = None
    lateral_movement: bool | None = None
    remote_access: bool | None = None
    cloud_access: bool | None = None
    source_code_access: bool | None = None
    privilege_escalation: bool | None = None
    discovery: bool | None = None


class Scope(StrictModel):
    environments: Annotated[list[Environment], Field(min_length=1)] | None = None

    @field_validator("environments", mode="after")
    @classmethod
    def _unique_environments(cls, values: list[Environment] | None) -> list[Environment] | None:
        return _unique(values) if values is not None else None


class Reference(StrictModel):
    name: NonEmptyString
    url: NonEmptyString


class Source(StrictModel):
    name: NonEmptyString
    type: SourceType
    url: NonEmptyString | None = None


class Metadata(BaseModel):
    model_config = ConfigDict(extra="allow", strict=True)

    confidence: Confidence | None = None
    last_reviewed: str | None = None
    created: str | None = None
    modified: str | None = None
    contributors: NonEmptyStrings | None = None

    @field_validator("last_reviewed", "created", "modified", mode="after")
    @classmethod
    def _date_string(cls, value: str | None) -> str | None:
        if value is not None:
            date.fromisoformat(value)
        return value

    @field_validator("contributors", mode="after")
    @classmethod
    def _unique_contributors(cls, values: NonEmptyStrings | None) -> NonEmptyStrings | None:
        return _unique(values) if values is not None else None


class Rule(StrictModel):
    schema_version: Literal[1]
    id: Identifier
    name: NonEmptyString
    category: Category
    sensitivity: Sensitivity
    match: Match
    description: NonEmptyString | None = None
    subcategory: Identifier | None = None
    artifact_types: Annotated[list[ArtifactType], Field(min_length=1)] | None = None
    credentials: Credentials | None = None
    impact: Impact | None = None
    scope: Scope | None = None
    tags: NonEmptyStrings | None = None
    references: list[Reference] | None = None
    sources: list[Source] | None = None
    metadata: Metadata | None = None

    @field_validator("artifact_types", "tags", mode="after")
    @classmethod
    def _unique_lists(cls, values: list[Any] | None) -> list[Any] | None:
        return _unique(values) if values is not None else None


@dataclass(frozen=True)
class ValidationIssue:
    message: str
    file: Path | None = None


def validate_rule_file(path: Path) -> tuple[str | None, list[ValidationIssue]]:
    rule, issues = _load_rule(path)
    if issues:
        return None, issues
    assert rule is not None

    rule_id = rule.get("id") if isinstance(rule.get("id"), str) else None
    issues = _model_issues(path, rule)
    issues.extend(_regex_issues(path, rule))
    return rule_id, issues


def validate_rules(rules_dir: Path) -> tuple[list[str], list[ValidationIssue]]:
    ids: list[str] = []
    seen: dict[str, Path] = {}
    issues: list[ValidationIssue] = []

    for path in _rule_files(rules_dir):
        rule_id, file_issues = validate_rule_file(path)
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


def load_valid_rule_files(rules_dir: Path) -> list[tuple[Path, dict[str, Any]]]:
    _, issues = validate_rules(rules_dir)
    if issues:
        raise ValueError(_format_issues(issues))

    rules: list[tuple[Path, dict[str, Any]]] = []
    for path in _rule_files(rules_dir):
        rule, file_issues = _load_rule(path)
        if file_issues or not isinstance(rule, dict):
            raise ValueError(_format_issues(file_issues))
        model = Rule.model_validate(rule)
        rules.append((path, model.model_dump(exclude_none=True)))
    return sorted(rules, key=lambda item: item[1]["id"])


def load_valid_rules(rules_dir: Path) -> list[dict[str, Any]]:
    return [rule for _, rule in load_valid_rule_files(rules_dir)]


def format_issues(issues: list[ValidationIssue]) -> str:
    return _format_issues(issues)


def _rule_files(rules_dir: Path) -> list[Path]:
    if not rules_dir.exists():
        return []
    files = [*rules_dir.rglob("*.yaml"), *rules_dir.rglob("*.yml")]
    return sorted(path for path in files if path.is_file())


def _load_rule(path: Path) -> tuple[dict[str, Any] | None, list[ValidationIssue]]:
    try:
        rule = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        return None, [ValidationIssue(f"invalid YAML: {error}", path)]

    if not isinstance(rule, dict):
        return None, [ValidationIssue("rule must be a YAML mapping", path)]
    return rule, []


def _model_issues(path: Path, rule: dict[str, Any]) -> list[ValidationIssue]:
    try:
        Rule.model_validate(rule)
    except ValidationError as error:
        errors = sorted(error.errors(), key=_issue_sort_key)
        return [_model_issue(path, issue) for issue in errors]
    return []


def _model_issue(path: Path, issue: Any) -> ValidationIssue:
    message = f"{_field_path(issue['loc'])}: {issue['msg']}"
    value = issue.get("input")
    if not isinstance(value, dict | list | type(None)):
        message = f"{message} (input: {value!r})"
    return ValidationIssue(message, path)


def _field_path(location: tuple[str | int, ...]) -> str:
    parts: list[str] = []
    for part in location:
        if isinstance(part, int):
            if parts:
                parts[-1] = f"{parts[-1]}[{part}]"
            else:
                parts.append(f"[{part}]")
        else:
            parts.append(str(part))
    return ".".join(parts) if parts else "(root)"


def _issue_sort_key(issue: Any) -> str:
    return _field_path(_issue_loc(issue))


def _issue_loc(issue: Any) -> tuple[str | int, ...]:
    location = issue.get("loc", ())
    return location if isinstance(location, tuple) else ()


def _unique(values: list[Any]) -> list[Any]:
    if len(values) != len(set(values)):
        raise ValueError("items must be unique")
    return values


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
