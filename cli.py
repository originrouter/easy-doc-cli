import argparse
import json
import sys
from datetime import datetime

import api
import session
from elements.title import TitleElement
from elements.abstract import AbstractElement
from elements.paragraph import ParagraphElement
from elements.h1 import H1Element
from elements.h2 import H2Element
from elements.h3 import H3Element
from elements.equation import EquationElement
from elements.code import CodeElement, VALID_LANGUAGES
from elements.list import ListElement
from elements.author import AuthorElement
from elements.image import ImageElement
from elements.table import TableElement
from elements.label import LabelElement
from elements.style_schemas import ELEMENT_STYLE_SCHEMAS

ELEMENT_REGISTRY = {
    "title":     TitleElement,
    "abstract":  AbstractElement,
    "paragraph": ParagraphElement,
    "h1":        H1Element,
    "h2":        H2Element,
    "h3":        H3Element,
    "equation":  EquationElement,
    "code":      CodeElement,
    "list":      ListElement,
    "author":    AuthorElement,
    "image":     ImageElement,
    "table":     TableElement,
    "label":     LabelElement,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_session() -> str:
    """返回有效的 sessionId，过期则自动重建。"""
    cache = session.get_cache()
    if session.is_expired(cache):
        doc_id = cache.get("docId")
        if not doc_id:
            raise session.SessionError("session 已过期且缓存中无 docId，请手动重新创建")
        print("session 已过期，正在自动重建...")
        data = api.post("/article/v1/session/create", {"docId": doc_id})
        session.save_cache({
            "docId": doc_id,
            "sessionId": data.get("sessionId"),
            "blockCount": data.get("blockCount"),
        })
        sid = data.get("sessionId") or ""
        print(f"session 已自动重建（sessionId: {sid}）")
        return sid
    return cache.get("sessionId") or ""


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

def cmd_session_create(args):
    data = api.post("/article/v1/session/create", {"docId": args.doc_id})
    session.save_cache({
        "docId": args.doc_id,
        "sessionId": data.get("sessionId"),
        "blockCount": data.get("blockCount"),
    })
    print(f"session 创建成功")
    print(f"  sessionId:  {data.get('sessionId')}")
    print(f"  blockCount: {data.get('blockCount')}")


def cmd_session_info(args):
    cache = session.get_cache()
    print(f"docId:      {cache.get('docId')}")
    print(f"sessionId:  {cache.get('sessionId')}")
    print(f"blockCount: {cache.get('blockCount')}")


def cmd_read_doc(args):
    sid = _ensure_session()
    data = api.post("/article/v1/doc/read", {"sessionId": sid})
    if args.blocks:
        for block in data.get("blocks", []):
            print(json.dumps(block, ensure_ascii=False))
    elif args.text:
        print(data.get("text", ""))
    else:
        print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_read_block(args):
    sid = _ensure_session()
    data = api.post("/article/v1/doc/read-block", {
        "sessionId": sid,
        "blockId": args.id,
    })
    print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_insert(args):
    sid = _ensure_session()

    # 通过 block-id 查询 path
    block_data = api.post("/article/v1/doc/read-block", {
        "sessionId": sid,
        "blockId": args.ref_id,
    })
    ref_path = block_data.get("path")
    if ref_path is None:
        sys.exit("error: 无法获取参考块的 path")

    if args.position == "before":
        path = ref_path
    else:  # after
        path = ref_path[:-1] + [ref_path[-1] + 1]

    if args.block:
        try:
            blocks = [json.loads(b) for b in args.block]
        except json.JSONDecodeError as e:
            sys.exit(f"error: --block JSON 解析失败: {e}")
    elif args.type:
        cls = ELEMENT_REGISTRY[args.type]
        try:
            blocks = [cls.from_cli_args(args).to_dict()]
        except (ValueError, NotImplementedError) as e:
            sys.exit(f"error: {e}")
    else:
        sys.exit("error: 请提供 --type 或 --block")

    data = api.post("/article/v1/block/insert", {
        "sessionId": sid,
        "path": path,
        "blocks": blocks,
    })
    print(f"插入成功，共 {len(blocks)} 个块（path={path}）")
    if data:
        print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_append(args):
    sid = _ensure_session()
    from latex_to_leaves import latex_to_leaves
    leaves = latex_to_leaves(args.latex) if args.latex else [{"type": "default", "text": args.text}]
    data = api.post("/article/v1/block/text/append", {
        "sessionId": sid,
        "blockId": args.id,
        "text": leaves,
    })
    print("追加成功")
    if data:
        print(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_replace(args):
    sid = _ensure_session()
    from latex_to_leaves import latex_to_leaves
    leaves = latex_to_leaves(args.latex) if args.latex else [{"type": "default", "text": args.text}]
    data = api.post("/article/v1/block/text/replace", {
        "sessionId": sid,
        "blockId": args.id,
        "children": leaves,
    })
    print("替换成功")
    if data:
        print(json.dumps(data, ensure_ascii=False, indent=2))


def _parse_kv_list(kv_list: list[str], flag_name: str) -> dict:
    """将 ['key=value', ...] 解析为 dict，value 尝试 JSON 解析（支持 true/false/数字）。"""
    result = {}
    for item in (kv_list or []):
        if "=" not in item:
            sys.exit(f"error: {flag_name} 格式应为 key=value，收到: {item!r}")
        k, _, v = item.partition("=")
        try:
            result[k] = json.loads(v)
        except json.JSONDecodeError:
            result[k] = v
    return result


def _fmt_time(ts: int, raw: bool) -> str:
    if raw:
        return str(ts)
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def _fetch_doc_list() -> list:
    return api.post("/article/v1/doc/list", {}).get("articles", [])


def cmd_doc_create(args):
    data = api.post("/article/v1/doc/create", {"group": args.group_id, "name": args.name})
    article = data.get("article", {})
    print(f"创建成功")
    print(f"  outer_id: {article.get('outer_id')}")
    print(f"  name:     {article.get('name')}")
    print(f"  group:    {data.get('group')}")


def cmd_doc_delete(args):
    data = api.post("/article/v1/doc/delete", {"docId": args.doc_id})
    print(f"删除成功：{data.get('article')}")


def cmd_block_delete(args):
    sid = _ensure_session()
    api.post("/article/v1/block/delete", {
        "sessionId": sid,
        "blockId": args.id,
    })
    print(f"块删除成功：{args.id}")


def cmd_list_groups(args):  # noqa: ARG001
    groups = _fetch_doc_list()
    print(f"{'GROUP_ID':<12} NAME")
    print("-" * 40)
    for g in groups:
        print(f"{g['group_id']:<12} {g['name']}")


def cmd_list_articles(args):
    groups = _fetch_doc_list()

    if args.json:
        result = []
        for g in groups:
            if args.group_id is not None and g["group_id"] != args.group_id:
                continue
            result.append(g)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    def print_article(article, group_name, indent=0):
        prefix = "  " * indent + ("└ " if indent > 0 else "")
        ts = _fmt_time(article["time_create"], args.raw)
        gname = group_name if indent == 0 else ""
        print(f"{gname:<14} {prefix}{article['outer_id']:<22} {article['name']:<32} {ts}")
        for child in article.get("children", []):
            print_article(child, "", indent + 1)

    print(f"{'GROUP':<14} {'DOC_ID':<22} {'NAME':<32} 创建时间")
    print("-" * 90)
    for g in groups:
        if args.group_id is not None and g["group_id"] != args.group_id:
            continue
        for article in g.get("articles", []):
            print_article(article, g["name"])


def cmd_style_schema(args):
    types = [args.type] if args.type else sorted(ELEMENT_STYLE_SCHEMAS)
    for block_type in types:
        schema = ELEMENT_STYLE_SCHEMAS[block_type]
        print(f"Block type: {block_type}")
        css_fields = schema.get("style")
        if css_fields:
            print(f"  CSS fields (--css):")
            for f in sorted(css_fields):
                print(f"    {f}")
        props = {k: v for k, v in schema.items() if k != "style"}
        if props:
            print(f"  Block props (--prop):")
            for k, v in sorted(props.items()):
                if isinstance(v, type):
                    type_hint = v.__name__
                elif isinstance(v, set):
                    type_hint = "{" + ", ".join(str(x) for x in sorted(str(i) for i in v)) + "}"
                else:
                    type_hint = str(v)
                print(f"    {k:<20} {type_hint}")
        print()


def cmd_block_style(args):
    from elements.style_schemas import validate_css_style, validate_block_style
    sid = _ensure_session()

    # 先读取 block 获取 type
    block_data = api.post("/article/v1/doc/read-block", {
        "sessionId": sid,
        "blockId": args.id,
    })
    block_type = block_data.get("block", {}).get("type")
    if not block_type:
        sys.exit("error: 无法获取 block 类型")

    payload = {"sessionId": sid, "blockId": args.id}

    # 构建 css_style：--css-style JSON 优先，--css key=value 次之
    css_style = {}
    if args.css_style:
        try:
            css_style = json.loads(args.css_style)
        except json.JSONDecodeError as e:
            sys.exit(f"error: --css-style JSON 解析失败: {e}")
    if args.css:
        css_style.update(_parse_kv_list(args.css, "--css"))
    if css_style:
        errors = validate_css_style(block_type, css_style)
        if errors:
            sys.exit("error: css-style 校验失败:\n" + "\n".join(f"  {e}" for e in errors))
        payload["style"] = css_style

    # 构建 block_style：--style JSON 优先，--prop key=value 次之
    block_style = {}
    if args.style:
        try:
            block_style = json.loads(args.style)
        except json.JSONDecodeError as e:
            sys.exit(f"error: --style JSON 解析失败: {e}")
    if args.prop:
        block_style.update(_parse_kv_list(args.prop, "--prop"))
    if block_style:
        errors = validate_block_style(block_type, block_style)
        if errors:
            sys.exit("error: style 校验失败:\n" + "\n".join(f"  {e}" for e in errors))
        payload.update(block_style)

    data = api.post("/article/v1/block/style", payload)
    print("样式更新成功")
    if data:
        print(json.dumps(data, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cli.py", description="文档编辑 CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    # --- doc ---
    p_doc = sub.add_parser("doc", help="文档管理")
    s_doc = p_doc.add_subparsers(dest="subcommand", required=True)

    p_dcreate = s_doc.add_parser("create", help="创建文档")
    p_dcreate.add_argument("--name", required=True, help="文档名称")
    p_dcreate.add_argument("--group-id", type=int, default=0, help="所属 group ID（默认 0）")
    p_dcreate.set_defaults(func=cmd_doc_create)

    p_ddelete = s_doc.add_parser("delete", help="删除文档")
    p_ddelete.add_argument("--doc-id", required=True, help="文档 ID")
    p_ddelete.set_defaults(func=cmd_doc_delete)

    # --- session ---
    p_session = sub.add_parser("session", help="session 管理")
    s_session = p_session.add_subparsers(dest="subcommand", required=True)

    p_create = s_session.add_parser("create", help="创建 session")
    p_create.add_argument("--doc-id", required=True, help="文档 ID")
    p_create.set_defaults(func=cmd_session_create)

    p_info = s_session.add_parser("info", help="查看当前 session")
    p_info.set_defaults(func=cmd_session_info)

    # --- read ---
    p_read = sub.add_parser("read", help="读取文档或块")
    s_read = p_read.add_subparsers(dest="subcommand", required=True)

    p_rdoc = s_read.add_parser("doc", help="读取完整文档")
    g_rdoc = p_rdoc.add_mutually_exclusive_group()
    g_rdoc.add_argument("--text", action="store_true", help="只输出全文纯文本")
    g_rdoc.add_argument("--blocks", action="store_true", help="逐行输出每个 block JSON")
    p_rdoc.set_defaults(func=cmd_read_doc)

    p_rblock = s_read.add_parser("block", help="读取指定块")
    p_rblock.add_argument("--id", required=True, help="块 ID")
    p_rblock.set_defaults(func=cmd_read_block)

    # --- insert ---
    p_insert = sub.add_parser("insert", help="插入块")
    p_insert.add_argument("--ref-id", required=True, help="参考块 ID")
    p_insert.add_argument("--position", choices=["before", "after"], default="after",
                          help="插入位置：before 在参考块之前，after 在参考块之后（默认）")
    p_insert.add_argument("--type", choices=list(ELEMENT_REGISTRY), help="块类型")
    p_insert.add_argument("--text", default="", help="文本内容")
    p_insert.add_argument("--latex", default=None, help="LaTeX 文本内容")
    p_insert.add_argument("--equation", default=None, help="LaTeX 公式（equation 类型）")
    p_insert.add_argument("--code", default=None, help="代码内容（code 类型）")
    p_insert.add_argument("--language", default="纯文本",
                          help=f"代码语言，可选: {', '.join(VALID_LANGUAGES)}")
    p_insert.add_argument("--items", nargs="+", help="列表项（list 类型）")
    p_insert.add_argument("--author", action="append", nargs="+", metavar="key=value",
                          help="作者信息，可重复，如 --author name=张三 institution=北京大学 isstar=true")
    p_insert.add_argument("--block", action="append", metavar="JSON",
                          help="原始 JSON 块，可重复使用")
    p_insert.set_defaults(func=cmd_insert)

    # --- append ---
    p_append = sub.add_parser("append", help="追加文本到块")
    p_append.add_argument("--id", required=True, help="块 ID")
    g = p_append.add_mutually_exclusive_group(required=True)
    g.add_argument("--text", help="纯文本")
    g.add_argument("--latex", help="LaTeX 文本")
    p_append.set_defaults(func=cmd_append)

    # --- replace ---
    p_replace = sub.add_parser("replace", help="替换块文本")
    p_replace.add_argument("--id", required=True, help="块 ID")
    g = p_replace.add_mutually_exclusive_group(required=True)
    g.add_argument("--text", help="纯文本")
    g.add_argument("--latex", help="LaTeX 文本")
    p_replace.set_defaults(func=cmd_replace)

    # --- block-style ---
    p_bstyle = sub.add_parser("block-style", help="修改块样式")
    p_bstyle.add_argument("--id", required=True, help="块 ID")
    p_bstyle.add_argument("--css-style", default=None, help="CSS 样式 JSON，如 '{\"fontSize\":\"16px\"}'（与 --css 二选一或混用）")
    p_bstyle.add_argument("--css", action="append", metavar="key=value",
                          help="CSS 样式键值对，可重复，如 --css fontSize=16px --css color=#333")
    p_bstyle.add_argument("--style", default=None, help="block 特有样式 JSON，如 '{\"isTemplate\":true}'（与 --prop 二选一或混用）")
    p_bstyle.add_argument("--prop", action="append", metavar="key=value",
                          help="block 特有样式键值对，可重复，如 --prop isTemplate=true --prop indent=true")
    p_bstyle.set_defaults(func=cmd_block_style)

    # --- block ---
    p_block = sub.add_parser("block", help="块管理")
    s_block = p_block.add_subparsers(dest="subcommand", required=True)

    p_bdelete = s_block.add_parser("delete", help="删除块")
    p_bdelete.add_argument("--id", required=True, help="块 ID")
    p_bdelete.set_defaults(func=cmd_block_delete)

    # --- list ---
    p_list = sub.add_parser("list", help="列出 group 或文章")
    s_list = p_list.add_subparsers(dest="subcommand", required=True)

    p_lgroups = s_list.add_parser("groups", help="列出所有 group")
    p_lgroups.set_defaults(func=cmd_list_groups)

    p_larticles = s_list.add_parser("articles", help="列出文章")
    p_larticles.add_argument("--group-id", type=int, default=None, help="只列出指定 group 的文章")
    p_larticles.add_argument("--raw", action="store_true", help="时间戳保留原始数字")
    p_larticles.add_argument("--json", action="store_true", help="输出原始 JSON")
    p_larticles.set_defaults(func=cmd_list_articles)

    # --- style-schema ---
    p_schema = sub.add_parser("style-schema", help="查询 block 类型支持的样式字段")
    p_schema.add_argument("--type", choices=list(ELEMENT_STYLE_SCHEMAS),
                          default=None, help="block 类型，省略则列出所有类型")
    p_schema.set_defaults(func=cmd_style_schema)

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except (api.APIError, session.SessionError) as e:
        sys.exit(f"error: {e}")


if __name__ == "__main__":
    main()
