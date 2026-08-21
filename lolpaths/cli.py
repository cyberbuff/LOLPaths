from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from lolpaths.generator import generate_outputs
from lolpaths.validator import format_issues, load_valid_rules, validate_rules


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.command == "validate":
        return _validate(args)
    if args.command == "generate":
        return _generate(args)
    if args.command == "list":
        return _list(args)
    if args.command == "show":
        return _show(args)
    parser.print_help()
    return 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lolpaths")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate")
    _add_rule_args(validate)

    generate = subparsers.add_parser("generate")
    _add_rule_args(generate)
    generate.add_argument("--output", type=Path, default=Path("generated"))
    generate.add_argument("--docs", type=Path, default=Path("docs"))

    list_parser = subparsers.add_parser("list")
    _add_rule_args(list_parser)
    list_parser.add_argument("--platform", choices=["windows", "linux", "macos"])
    list_parser.add_argument("--category")
    list_parser.add_argument("--sensitivity")

    show = subparsers.add_parser("show")
    show.add_argument("rule_id")
    _add_rule_args(show)
    return parser


def _add_rule_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--rules", type=Path, default=Path("rules"))
    parser.add_argument("--schema", type=Path, default=Path("schema/lolpaths.schema.json"))


def _validate(args: argparse.Namespace) -> int:
    print("Validating LOLPaths rules...")
    ids, issues = validate_rules(args.rules, args.schema)
    for rule_id in ids:
        print(f"✓ {rule_id}")
    if issues:
        print(format_issues(issues))
        print(f"Validation failed: {len(issues)} error(s)")
        return 1
    print(f"{len(ids)} rules validated")
    print("0 errors")
    return 0


def _generate(args: argparse.Namespace) -> int:
    try:
        generate_outputs(args.rules, args.schema, args.output, args.docs)
    except ValueError as error:
        print(error)
        return 1
    print(f"Generated LOLPaths artifacts in {args.output} and {args.docs}")
    return 0


def _list(args: argparse.Namespace) -> int:
    try:
        rules = load_valid_rules(args.rules, args.schema)
    except ValueError as error:
        print(error)
        return 1
    for rule in rules:
        if _matches_filters(rule, args):
            print(f"{rule['id']}\t{rule['name']}")
    return 0


def _show(args: argparse.Namespace) -> int:
    try:
        rules = load_valid_rules(args.rules, args.schema)
    except ValueError as error:
        print(error)
        return 1
    for rule in rules:
        if rule["id"] == args.rule_id:
            print(json.dumps(rule, indent=2, sort_keys=True))
            return 0
    print(f'Rule not found: "{args.rule_id}"')
    return 1


def _matches_filters(rule: dict[str, Any], args: argparse.Namespace) -> bool:
    if args.category and rule.get("category") != args.category:
        return False
    if args.sensitivity and rule.get("sensitivity") != args.sensitivity:
        return False
    return not (args.platform and not _has_platform(rule, args.platform))


def _has_platform(rule: dict[str, Any], platform: str) -> bool:
    paths = rule.get("match", {}).get("paths", [])
    return any(platform in matcher.get("platforms", []) for matcher in paths)


if __name__ == "__main__":
    raise SystemExit(main())
