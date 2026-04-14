from elements.base import BaseElement
from latex_to_leaves import latex_to_leaves


class LabelElement(BaseElement):
    TYPE = "label"

    def __init__(self, items: list[tuple[str, str]], style: dict | None = None):
        """
        items: list of (name, content) tuples.
               name    — plain text label
               content — LaTeX-formatted rich text
        """
        children = [
            {
                "type": "label-item",
                "name": name,
                "children": latex_to_leaves(content),
            }
            for name, content in items
        ]
        super().__init__(children=children, style=style)
        self.type = self.TYPE

    @classmethod
    def from_cli_args(cls, args) -> "LabelElement":
        raw = getattr(args, "items", None)
        if not raw:
            raise ValueError("--items is required for type 'label'")
        if len(raw) % 2 != 0:
            raise ValueError(
                "--items for 'label' requires an even number of values: "
                "name1 content1 name2 content2 ..."
            )
        items = [(raw[i], raw[i + 1]) for i in range(0, len(raw), 2)]
        return cls(items=items)
