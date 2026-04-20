from elements.base import BaseElement


class AuthorElement(BaseElement):
    TYPE = "author"

    def __init__(self, authors: list, institutions: list, children: list | None = None, style: dict | None = None):
        super().__init__(children or [], style)
        self.authors = authors
        self.institutions = institutions

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["author"] = self.authors
        d["institution"] = self.institutions
        return d

    @classmethod
    def from_cli_args(cls, args) -> "AuthorElement":
        if not args.author:
            raise ValueError("author 类型需要至少一个 --author 参数")

        institution_map: dict[str, int] = {}  # name -> id
        authors = []

        for tokens in args.author:
            # tokens is a list of key=value strings (nargs="+")
            kv: dict[str, str] = {}
            for token in tokens:
                if "=" not in token:
                    raise ValueError(f"--author 格式应为 key=value，收到: {token!r}")
                k, _, v = token.partition("=")
                kv[k] = v

            name = kv.get("name", "").strip()
            if not name:
                raise ValueError(f"--author 缺少 name 字段: {tokens!r}")

            institution_name = kv.get("institution", "").strip()
            is_star_raw = kv.get("isstar", kv.get("isStar", "false")).lower()
            is_star = is_star_raw in ("true", "1", "yes")

            # deduplicate institutions
            if institution_name and institution_name not in institution_map:
                institution_map[institution_name] = len(institution_map) + 1
            institution_id = institution_map.get(institution_name, 0)

            authors.append({
                "id": len(authors) + 1,
                "name": name,
                "institutionId": institution_id,
                "isStar": is_star,
            })

        institutions = [{"id": iid, "name": iname} for iname, iid in institution_map.items()]
        return cls(authors=authors, institutions=institutions)
