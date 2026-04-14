from elements.base import BaseElement


class ImageElement(BaseElement):
    TYPE = "image"

    @classmethod
    def from_cli_args(cls, args) -> "ImageElement":
        raise NotImplementedError(
            "image 类型暂不支持具名参数，请使用 --block 传入原始 JSON"
        )
