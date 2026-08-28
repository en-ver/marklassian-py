import sys
from typing import Any, Literal, TypedDict

if sys.version_info >= (3, 11):
    from typing import Required
else:
    from typing_extensions import Required


class AdfMark(TypedDict, total=False):
    type: Required[str]
    attrs: dict[str, Any]


class AdfNode(TypedDict, total=False):
    type: Required[str]
    attrs: dict[str, Any]
    content: list["AdfNode"]
    marks: list[AdfMark]
    text: str


class AdfDocument(TypedDict):
    version: Literal[1]
    type: Literal["doc"]
    content: list[AdfNode]
