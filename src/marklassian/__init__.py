from importlib.metadata import version

from .converter import markdown_to_adf
from .types import AdfDocument, AdfMark, AdfNode

__all__ = ["AdfDocument", "AdfMark", "AdfNode", "markdown_to_adf"]
__version__ = version("marklassian")
