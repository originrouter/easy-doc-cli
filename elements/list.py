import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elements.base import BaseElement


class ListElement(BaseElement):
    TYPE = "list"

    def __init__(self, items: list[str], style: dict = None):
        children = [
            {"type": "list-item", "children": [{"type": "default", "text": item}]}
            for item in items
        ]
        super().__init__(children=children, style=style)
        self.type = self.TYPE

    @classmethod
    def from_cli_args(cls, args) -> "ListElement":
        if not getattr(args, "items", None):
            raise ValueError("--items is required for type 'list'")
        return cls(items=args.items)
