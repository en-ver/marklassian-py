from pathlib import Path

import pytest
from conftest import load_fixture
from jsonschema.exceptions import ValidationError
from jsonschema.protocols import Validator

FIXTURE_NAMES = sorted(path.stem for path in (Path(__file__).parent / "fixtures").glob("*.json"))


@pytest.mark.parametrize("fixture_name", FIXTURE_NAMES)
def test_fixture_conforms_to_adf_schema(
    fixture_name: str,
    adf_validator: Validator,
) -> None:
    if fixture_name == "gfm-nested-task-list":
        pytest.xfail("Nested task lists currently violate the ADF schema")

    adf_validator.validate(load_fixture(fixture_name))


def test_nested_task_list_fixture_records_known_schema_failure(
    adf_validator: Validator,
) -> None:
    with pytest.raises(ValidationError):
        adf_validator.validate(load_fixture("gfm-nested-task-list"))
