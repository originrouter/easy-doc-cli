import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elements.base import BaseElement
from latex_to_leaves import latex_to_leaves


def _build_children(args) -> list:
    if getattr(args, "latex", None):
        return latex_to_leaves(args.latex)
    return [{"type": "default", "text": getattr(args, "text", "") or ""}]


class H2Element(BaseElement):
    TYPE = "h2"

    def __init__(self, children: list, style: dict = None):
        super().__init__(children=children, style=style)
        self.type = self.TYPE

    @classmethod
    def from_cli_args(cls, args) -> "H2Element":
        return cls(children=_build_children(args))
