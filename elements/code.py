import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elements.base import BaseElement

VALID_LANGUAGES = [
    "纯文本", "Bash", "C", "C#", "C++", "CSS", "Dart", "Dockerfile",
    "F#", "Fortran", "Go", "HTML", "Java", "JavaScript", "JSON",
    "Julia", "Kotlin", "Less", "Lua", "Markdown", "MATLAB", "PHP",
    "PowerShell", "Python", "R", "Rust", "Sass", "SQL", "Swift",
    "TypeScript", "YAML", "XML",
]


class CodeElement(BaseElement):
    TYPE = "code"

    def __init__(self, code: str, language: str = "纯文本", style: dict = None):
        super().__init__(children=[], style=style)
        self.type = self.TYPE
        self.code = code
        self.language = language

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["code"] = self.code
        d["language"] = self.language
        return d

    @classmethod
    def from_cli_args(cls, args) -> "CodeElement":
        if not getattr(args, "code", None):
            raise ValueError("--code is required for type 'code'")
        language = getattr(args, "language", "纯文本") or "纯文本"
        if language not in VALID_LANGUAGES:
            raise ValueError(f"不支持的语言 '{language}'，可选值: {', '.join(VALID_LANGUAGES)}")
        return cls(code=args.code, language=language)
