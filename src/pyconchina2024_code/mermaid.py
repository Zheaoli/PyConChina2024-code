from __future__ import annotations

import ast
from typing import Any


def ast_to_mermaid(node: ast.AST, omit_docstrings: bool = True) -> str:
    """Convert Python AST to Mermaid flowchart."""
    nodes = []
    edges = []
    counter = 0

    def process_node(node: Any, parent_id: int | None = None) -> int:
        nonlocal counter
        current_id = counter
        counter += 1

        # Handle node
        if isinstance(node, ast.AST):
            nodes.append(f"    {current_id}[{node.__class__.__name__}]")
            if parent_id is not None:
                edges.append(f"    {parent_id} --> {current_id}")

            # Process fields
            for field_name, field_value in ast.iter_fields(node):
                if field_name == "ctx":
                    continue

                if isinstance(field_value, ast.AST):
                    process_node(field_value, current_id)
                elif isinstance(field_value, list):
                    if (
                        omit_docstrings
                        and field_name == "body"
                        and isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module))
                    ):
                        field_value = _strip_docstring(field_value)
                    for item in field_value:
                        if isinstance(item, ast.AST):
                            process_node(item, current_id)
                elif isinstance(field_value, str):
                    child_id = counter
                    counter += 1
                    nodes.append(f'    {child_id}["{field_value}"]')
                    edges.append(f"    {current_id} --> {child_id}")
                elif field_value is not None:
                    child_id = counter
                    counter += 1
                    nodes.append(f"    {child_id}[{field_value!s}]")
                    edges.append(f"    {current_id} --> {child_id}")

        return current_id

    process_node(node)

    return "flowchart TD\n" + "\n".join(nodes) + "\n" + "\n".join(edges)


def _strip_docstring(body):
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Str):
        return body[1:]
    return body
