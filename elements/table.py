from elements.base import BaseElement
from latex_table_parser import latex_table_to_dict


class TableElement(BaseElement):
    TYPE = "table"

    def __init__(self, children: list, row_length: int, col_length: int, style: dict = None):
        super().__init__(children=children, style=style)
        self.row_length = row_length
        self.col_length = col_length

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "children": self.children,
            "rowLength": self.row_length,
            "colLength": self.col_length,
            "style": self.style,
        }

    @classmethod
    def from_cli_args(cls, args) -> "TableElement":
        if not getattr(args, "latex", None):
            raise ValueError("table 类型需要 --latex 传入 tabular 代码")
        d = latex_table_to_dict(args.latex)
        return cls(
            children=d["children"],
            row_length=d["rowLength"],
            col_length=d["colLength"],
            style=d.get("style", {}),
        )
