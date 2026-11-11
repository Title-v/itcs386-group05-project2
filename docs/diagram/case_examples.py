"""Derive reading-only examples from the real parametrized test AST.

No test module imports, eval(), exec(), credentials or network operations.
Only equality/inequality of literal case values is folded. Runtime checks stay.
"""
import ast
from copy import deepcopy


def known_boolean(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, bool):
        return node.value
    if (isinstance(node, ast.Compare) and len(node.ops) == 1
            and isinstance(node.left, ast.Constant)
            and isinstance(node.comparators[0], ast.Constant)):
        left, right = node.left.value, node.comparators[0].value
        if isinstance(node.ops[0], ast.Eq):
            return left == right
        if isinstance(node.ops[0], ast.NotEq):
            return left != right
    return None


class BindCase(ast.NodeTransformer):
    def __init__(self, values):
        self.values = values

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load) and node.id in self.values:
            return ast.copy_location(ast.Constant(value=self.values[node.id]), node)
        return node

    def block(self, statements):
        output = []
        for statement in statements:
            result = self.visit(statement)
            for item in result if isinstance(result, list) else [result]:
                if item is None:
                    continue
                output.append(item)
                if isinstance(item, (ast.Return, ast.Raise)):
                    return output
        return output

    def visit_If(self, node):
        node.test = self.visit(node.test)
        truth = known_boolean(node.test)
        if truth is not None:
            return self.block(node.body if truth else node.orelse)
        node.body = self.block(node.body)
        node.orelse = self.block(node.orelse)
        return node

    def visit_IfExp(self, node):
        node.test = self.visit(node.test)
        truth = known_boolean(node.test)
        if truth is not None:
            return self.visit(node.body if truth else node.orelse)
        node.body, node.orelse = self.visit(node.body), self.visit(node.orelse)
        return node


def build_example(module, original, values, case_id):
    names = {argument.arg for argument in original.args.args}
    if not set(values) <= names:
        raise ValueError("Case parameters must belong to the original signature")
    if original.args.defaults or original.args.kwonlyargs or original.args.vararg or original.args.kwarg:
        raise ValueError("Review example binding for this more complex signature")
    for node in ast.walk(original):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store) and node.id in values:
            raise ValueError(f"Bound parameter {node.id} is reassigned; cannot specialize safely")
        if node is not original and isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            raise ValueError("Review nested scopes before binding case parameters")
    function = deepcopy(original)
    function.name = "example_" + case_id.lower().replace("-", "_")
    function.decorator_list = []
    function.args.args = [argument for argument in function.args.args if argument.arg not in values]
    function.body = BindCase(values).block(function.body)
    used_names = {n.id for n in ast.walk(function) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
    imports = []
    for node in module.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            copied = deepcopy(node)
            copied.names = [a for a in node.names if (a.asname or a.name.split(".")[0]) in used_names]
            if copied.names:
                imports.append(copied)
    result = ast.fix_missing_locations(ast.Module(body=[*imports, function], type_ignores=[]))
    code = ast.unparse(result)
    compile(code, f"reading-example-{case_id}", "exec")  # Syntax only; never executes.
    return (f"# {case_id}: reading example derived from the real test.\n"
            "# api/products are the project's pytest fixtures.\n"
            "# products cleanup runs in conftest.py's finally block.\n\n" + code + "\n")
