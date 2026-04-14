from elements.style_schemas import validate_style


class BaseElement:
    TYPE = ""

    def __init__(self, children: list, style: dict | None = None):
        self.type = self.TYPE
        self.children = children
        self.style = style or {}
        if self.type and self.style:
            errors = validate_style(self.type, self.style)
            if errors:
                raise ValueError("Style validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "children": self.children,
            "style": self.style,
        }

    @classmethod
    def from_cli_args(cls, args) -> "BaseElement":
        raise NotImplementedError
