import argparse
import json
import sys

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

    if args.css_style:
        try:
            css_style = json.loads(args.css_style)
        except json.JSONDecodeError as e:
            sys.exit(f"error: --css-style JSON 解析失败: {e}")
        errors = validate_css_style(block_type, css_style)
        if errors:
            sys.exit("error: css-style 校验失败:\n" + "\n".join(f"  {e}" for e in errors))
        payload["style"] = css_style

    if args.style:
        try:
            block_style = json.loads(args.style)
        except json.JSONDecodeError as e:
            sys.exit(f"error: --style JSON 解析失败: {e}")
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
    p_bstyle.add_argument("--css-style", default=None, help="CSS 样式 JSON，如 '{\"fontSize\":\"16px\",\"color\":\"#333\"}'")
    p_bstyle.add_argument("--style", default=None, help="block 特有样式 JSON，如 '{\"isTemplate\":true,\"indent\":true}'")
    p_bstyle.set_defaults(func=cmd_block_style)

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
