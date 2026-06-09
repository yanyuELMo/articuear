"""Configuration file tests for the scaffold."""

from __future__ import annotations

import csv
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_ROOT = REPO_ROOT / "configs"
EVENTS_CSV = REPO_ROOT / "data" / "metadata" / "events_example.csv"

EXPECTED_EVENT_FIELDS = [
    "subject_id",
    "session_id",
    "event_id",
    "sentence_id",
    "label_id",
    "domain",
    "repeat_id",
    "start_time",
    "end_time",
    "split",
]


def test_yaml_files_are_parseable() -> None:
    """Ensure all placeholder YAML files remain valid."""

    yaml_files = sorted(CONFIG_ROOT.rglob("*.yaml"))
    assert yaml_files, "No YAML configuration files were found."

    for yaml_file in yaml_files:
        with yaml_file.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        assert isinstance(data, dict), f"{yaml_file} did not parse into a mapping."


def test_root_hydra_config_has_defaults() -> None:
    """Ensure the root config follows Hydra defaults composition style."""

    config_path = CONFIG_ROOT / "config.yaml"
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    defaults = config.get("defaults")
    assert isinstance(defaults, list)
    assert "_self_" in defaults


def test_events_example_csv_has_expected_header() -> None:
    """Ensure the metadata example keeps the documented schema."""

    with EVENTS_CSV.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == EXPECTED_EVENT_FIELDS
