import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elements.base import BaseElement


class EquationElement(BaseElement):
    TYPE = "equation"

    def __init__(self, equation: str, style: dict = None):
        super().__init__(children=[], style=style)
        self.type = self.TYPE
        self.equation = equation

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["equation"] = self.equation
        return d

    @classmethod
    def from_cli_args(cls, args) -> "EquationElement":
        if not getattr(args, "equation", None):
            raise ValueError("--equation is required for type 'equation'")
        return cls(equation=args.equation)
