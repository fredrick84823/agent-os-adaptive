"""用 tree-sitter 從單一檔案擷取 import 敘述（不做解析，只取原始 specifier）。"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import cache

import tree_sitter as ts


@dataclass(frozen=True)
class RawImport:
    """一個 import 敘述。spec 為 None 代表動態 import 的參數不是字面字串。"""

    spec: str | None
    line: int  # 1-based
    kind: str  # static | type | reexport | require | dynamic
    names: tuple[str, ...] = field(default=())  # Python `from x import a, b` 的 a, b
    expr: str | None = None  # spec 為 None 時的原始運算式（截斷）


@cache
def _language(lang: str) -> ts.Language:
    if lang in ("typescript", "tsx"):
        import tree_sitter_typescript as m
        return ts.Language(m.language_typescript() if lang == "typescript" else m.language_tsx())
    if lang == "javascript":
        import tree_sitter_javascript as m
        return ts.Language(m.language())
    if lang == "python":
        import tree_sitter_python as m
        return ts.Language(m.language())
    raise ValueError(lang)


_JS_QUERY = """
(import_statement) @import
(export_statement source: (_)) @export
(call_expression function: (import)) @dynamic
(call_expression function: (identifier) @_fn arguments: (arguments) (#eq? @_fn "require")) @require
"""

_PY_QUERY = """
(import_statement) @import
(import_from_statement) @from
(call function: (identifier) @_fn (#any-of? @_fn "__import__" "import_module")) @dynamic
(call function: (attribute attribute: (identifier) @_attr) (#eq? @_attr "import_module")) @dynamic
"""


@cache
def _parser_and_query(lang: str) -> tuple[ts.Parser, ts.Query]:
    language = _language(lang)
    src = _PY_QUERY if lang == "python" else _JS_QUERY
    return ts.Parser(language), ts.Query(language, src)


def _text(node: ts.Node) -> str:
    return node.text.decode("utf-8", "replace")


def _expr(node: ts.Node | None) -> str | None:
    if node is None:
        return None
    t = " ".join(_text(node).split())
    return t if len(t) <= 120 else t[:117] + "..."


def _js_literal(node: ts.Node | None) -> str | None:
    """JS/TS 字串或無插值的 template string → 內容；其他 → None。"""
    if node is None:
        return None
    if node.type == "string":
        return "".join(_text(c) for c in node.named_children)
    if node.type == "template_string":
        if any(c.type == "template_substitution" for c in node.named_children):
            return None
        return "".join(_text(c) for c in node.named_children)
    return None


def _first_arg(call: ts.Node) -> ts.Node | None:
    args = call.child_by_field_name("arguments")
    if args is None:
        return None
    named = [c for c in args.named_children if c.type != "comment"]
    return named[0] if named else None


def _captures(query: ts.Query, root: ts.Node) -> list[tuple[str, ts.Node]]:
    caps = ts.QueryCursor(query).captures(root)
    out = []
    for name, nodes in caps.items():
        if name.startswith("_"):
            continue
        out.extend((name, n) for n in nodes)
    out.sort(key=lambda x: (x[1].start_byte, x[0]))
    return out


def _extract_js(root: ts.Node, query: ts.Query) -> list[RawImport]:
    found = []
    for cap, node in _captures(query, root):
        line = node.start_point[0] + 1
        if cap == "import":
            is_type = any(c.type == "type" for c in node.children)
            req = next((c for c in node.named_children if c.type == "import_require_clause"), None)
            if req is not None:
                lit = next((c for c in req.named_children if c.type == "string"), None)
                spec = _js_literal(lit)
                found.append(RawImport(spec, line, "require", expr=None if spec is not None else _expr(node)))
                continue
            src = node.child_by_field_name("source")
            if src is None:
                continue
            found.append(RawImport(_js_literal(src), line, "type" if is_type else "static"))
        elif cap == "export":
            is_type = any(c.type == "type" for c in node.children)
            src = node.child_by_field_name("source")
            found.append(RawImport(_js_literal(src), line, "type" if is_type else "reexport"))
        else:  # dynamic / require
            arg = _first_arg(node)
            lit = _js_literal(arg)
            kind = "dynamic" if cap == "dynamic" else "require"
            found.append(RawImport(lit, line, kind, expr=None if lit is not None else _expr(node)))
    return found


def _py_literal(node: ts.Node | None) -> str | None:
    if node is None or node.type != "string":
        return None
    if any(c.type == "interpolation" for c in node.named_children):
        return None
    return "".join(_text(c) for c in node.named_children if c.type == "string_content")


def _in_type_checking(node: ts.Node) -> bool:
    child, parent = node, node.parent
    while parent is not None:
        if parent.type == "if_statement" and parent.child_by_field_name("consequence") == child:
            cond = parent.child_by_field_name("condition")
            if cond is not None and _text(cond).split(".")[-1] == "TYPE_CHECKING":
                return True
        child, parent = parent, parent.parent
    return False


def _dotted(node: ts.Node) -> str:
    if node.type == "aliased_import":
        node = node.child_by_field_name("name")
    return _text(node)


def _extract_py(root: ts.Node, query: ts.Query) -> list[RawImport]:
    found = []
    for cap, node in _captures(query, root):
        line = node.start_point[0] + 1
        if cap == "import":
            kind = "type" if _in_type_checking(node) else "static"
            for i, c in enumerate(node.children):
                if node.field_name_for_child(i) == "name":
                    found.append(RawImport(_dotted(c), line, kind))
        elif cap == "from":
            kind = "type" if _in_type_checking(node) else "static"
            mod = node.child_by_field_name("module_name")
            if mod is None:
                continue
            names = []
            for i, c in enumerate(node.children):
                if node.field_name_for_child(i) == "name":
                    names.append(_dotted(c))
                elif c.type == "wildcard_import":
                    names.append("*")
            found.append(RawImport("".join(_text(mod).split()), line, kind, tuple(names)))
        else:
            arg = _first_arg(node)
            lit = _py_literal(arg)
            found.append(RawImport(lit, line, "dynamic", expr=None if lit is not None else _expr(node)))
    return found


def extract(lang: str, source: bytes) -> tuple[list[RawImport], bool]:
    """回傳 (imports, 是否有語法錯誤)。"""
    parser, query = _parser_and_query(lang)
    tree = parser.parse(source)
    root = tree.root_node
    items = _extract_py(root, query) if lang == "python" else _extract_js(root, query)
    return items, root.has_error
