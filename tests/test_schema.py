from pathlib import Path
from typing import Any, cast

import pytest
from conftest import load_fixture
from jsonschema.protocols import Validator

from marklassian import markdown_to_adf

FIXTURE_NAMES = sorted(path.stem for path in (Path(__file__).parent / "fixtures").glob("*.json"))


@pytest.mark.parametrize("fixture_name", FIXTURE_NAMES)
def test_fixture_conforms_to_adf_schema(
    fixture_name: str,
    adf_validator: Validator,
) -> None:
    adf_validator.validate(load_fixture(fixture_name))


@pytest.mark.parametrize(
    ("markdown", "expected_top_level_type"),
    [
        ("- [ ] Parent\n  - [x] Child", "taskList"),
        ("- [ ] Parent\n  - Child", "bulletList"),
        ("- [ ] First paragraph\n\n  Second paragraph", "taskList"),
        ("- [ ] Task\n\n  ```python\n  pass\n  ```", "bulletList"),
        ("- [ ]", "taskList"),
        ("-", "bulletList"),
        ("```\n```", "codeBlock"),
        (">", "blockquote"),
    ],
)
def test_edge_case_conforms_to_adf_schema(
    markdown: str,
    expected_top_level_type: str,
    adf_validator: Validator,
) -> None:
    result = cast(dict[str, Any], markdown_to_adf(markdown))

    adf_validator.validate(result)
    assert result["content"][0]["type"] == expected_top_level_type


def test_empty_document_conforms_to_adf_schema(adf_validator: Validator) -> None:
    result = cast(dict[str, Any], markdown_to_adf(""))

    adf_validator.validate(result)
    assert result["content"] == []
