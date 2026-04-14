from elements.base import BaseElement


class AuthorElement(BaseElement):
    TYPE = "author"

    @classmethod
    def from_cli_args(cls, args) -> "AuthorElement":
        raise NotImplementedError(
            "author 类型暂不支持具名参数，请使用 --block 传入原始 JSON"
        )
