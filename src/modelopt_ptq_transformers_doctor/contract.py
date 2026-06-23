"""Static AST extraction of modelopt PTQ's transformers dependency contract."""

from __future__ import annotations

import ast
import glob
import importlib.util
import os

from .allowlist import EXPORT_FILES, EXPORT_PLUGIN_GLOB, QUANT_FILES, ROLE_OF
from .models import ContractRecord

_IMPORT_EXCEPTIONS = {"ImportError", "ModuleNotFoundError"}


def installed_modelopt_root() -> str:
    """Locate the installed modelopt package and return the root directory that
    contains it (i.e. the dir under which ``modelopt/torch/...`` resolves).

    Uses ``find_spec`` so modelopt is *located* but never imported (importing it
    would pull in torch and other heavy dependencies). Raises ModuleNotFoundError
    if modelopt is not installed in the current runtime environment.
    """
    spec = importlib.util.find_spec("modelopt")
    if spec is None or not spec.origin:
        raise ModuleNotFoundError(
            "modelopt is not installed in this environment. Install it with:\n"
            "  pip install git+https://github.com/NVIDIA/Model-Optimizer.git"
        )
    # spec.origin -> <site-packages>/modelopt/__init__.py
    return os.path.dirname(os.path.dirname(spec.origin))


def _handler_catches_importerror(handler: ast.ExceptHandler) -> bool:
    t = handler.type
    if t is None:  # bare except
        return True
    names = []
    if isinstance(t, ast.Tuple):
        names = [e.id for e in t.elts if isinstance(e, ast.Name)]
    elif isinstance(t, ast.Name):
        names = [t.id]
    return any(n in _IMPORT_EXCEPTIONS for n in names)


def _dotted_name(node: ast.AST) -> list[str] | None:
    """Return the dotted-name parts for an Attribute/Name chain, else None."""
    parts: list[str] = []
    cur = node
    while isinstance(cur, ast.Attribute):
        parts.append(cur.attr)
        cur = cur.value
    if isinstance(cur, ast.Name):
        parts.append(cur.id)
        parts.reverse()
        return parts
    return None


class _Visitor(ast.NodeVisitor):
    def __init__(self, file: str, role: str):
        self.file = file
        self.role = role
        self.records: list[ContractRecord] = []
        self._guarded = False

    def _add(self, module_path, symbol, line, dynamic=False):
        self.records.append(ContractRecord(
            module_path=module_path, symbol=symbol, file=self.file, line=line,
            guarded=self._guarded, dynamic=dynamic, role=self.role,
        ))

    def visit_Try(self, node: ast.Try):
        catches = any(_handler_catches_importerror(h) for h in node.handlers)
        prev = self._guarded
        self._guarded = prev or catches
        for stmt in node.body:
            self.visit(stmt)
        self._guarded = prev
        for h in node.handlers:
            self.visit(h)
        for stmt in node.orelse + node.finalbody:
            self.visit(stmt)

    # ast.TryStar (Python 3.11+ except* syntax) has the same body/handlers
    # shape as ast.Try, so we reuse the same visitor.
    visit_TryStar = visit_Try

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if node.module and (node.module == "transformers"
                            or node.module.startswith("transformers.")):
            for alias in node.names:
                if alias.name == "*":
                    continue
                self._add(node.module, alias.name, node.lineno)

    def visit_Attribute(self, node: ast.Attribute):
        parts = _dotted_name(node)
        if parts and parts[0] == "transformers" and len(parts) >= 2:
            symbol = parts[-1]
            if symbol[:1].isupper():  # class-like; skip __version__, lowercase attrs
                module_path = ".".join(parts[:-1])
                self._add(module_path, symbol, node.lineno)
                return  # maximal chain captured; deeper sub-chains are prefixes
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        func = node.func
        is_register = (isinstance(func, ast.Attribute) and func.attr == "register") or (
            isinstance(func, ast.Name) and func.id == "register")
        if is_register and node.args and isinstance(node.args[0], ast.Dict):
            for key in node.args[0].keys:
                if isinstance(key, ast.Name):  # variable key => runtime-discovered
                    self._add("", key.id, node.lineno, dynamic=True)
        self.generic_visit(node)


def extract_from_source(source: str, file: str, role: str) -> list[ContractRecord]:
    tree = ast.parse(source)
    v = _Visitor(file, role)
    v.visit(tree)
    return v.records


def extract_contract(modelopt_root: str) -> list[ContractRecord]:
    records: list[ContractRecord] = []
    for rel in QUANT_FILES + EXPORT_FILES:
        path = os.path.join(modelopt_root, rel)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"expected modelopt allowlist file missing: {rel}")
        with open(path, encoding="utf-8") as fh:
            records += extract_from_source(fh.read(), rel, ROLE_OF[rel])
    for path in sorted(glob.glob(os.path.join(modelopt_root, EXPORT_PLUGIN_GLOB))):
        rel = os.path.relpath(path, modelopt_root)
        with open(path, encoding="utf-8") as fh:
            records += extract_from_source(fh.read(), rel, "export")
    return records
