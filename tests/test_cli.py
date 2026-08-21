from __future__ import annotations

from pathlib import Path

from pytest import CaptureFixture

from lolpaths.cli import main


def write_rule(rules_dir: Path) -> None:
    path = rules_dir / "application" / "sample-secret.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """
schema_version: 1
id: application.sample-secret
name: Sample Secret
category: application
sensitivity: critical
match:
  paths:
    - path: "sample-secret-file"
      kind: file
      platforms: [linux, macos]
""".strip()
        + "\n",
        encoding="utf-8",
    )


def schema_path() -> Path:
    return Path(__file__).resolve().parents[1] / "schema" / "lolpaths.schema.json"


def test_validate_and_generate_commands(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    rules_dir = tmp_path / "rules"
    generated_dir = tmp_path / "generated"
    docs_dir = tmp_path / "docs"
    write_rule(rules_dir)

    validate_code = main(["validate", "--rules", str(rules_dir), "--schema", str(schema_path())])
    generate_code = main(
        [
            "generate",
            "--rules",
            str(rules_dir),
            "--schema",
            str(schema_path()),
            "--output",
            str(generated_dir),
            "--docs",
            str(docs_dir),
        ]
    )

    output = capsys.readouterr().out
    assert validate_code == 0
    assert generate_code == 0
    assert "application.sample-secret" in output
    assert (generated_dir / "linux.txt").exists()
    assert (docs_dir / "public/api/rules.json").exists()
    assert (docs_dir / "content/docs/application/sample-secret.mdx").exists()
    assert not (generated_dir / "rules.json").exists()


def test_list_and_show_commands_filter_rules(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    rules_dir = tmp_path / "rules"
    write_rule(rules_dir)

    list_code = main(
        [
            "list",
            "--rules",
            str(rules_dir),
            "--schema",
            str(schema_path()),
            "--platform",
            "linux",
            "--category",
            "application",
        ]
    )
    show_code = main(
        [
            "show",
            "application.sample-secret",
            "--rules",
            str(rules_dir),
            "--schema",
            str(schema_path()),
        ]
    )

    output = capsys.readouterr().out
    assert list_code == 0
    assert show_code == 0
    assert "application.sample-secret" in output
    assert "Sample Secret" in output
