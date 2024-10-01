"""A module for performing code generation for fuzz-lang."""

from typing import Any

from fuzz_lang.transpiler.parsing import (
    Function,
    AssignmentStatement,
    Loop,
    Node,
    Nodes,
    PrintStatement,
    ReturnStatement,
)


def get_rust_type(_type: str) -> str:
    """A function to pattern match a fuzz-lang type to a rust type."""
    match _type:
        case "int":
            return "i32"
        case "float":
            return "f32"
        case "string":
            return "&str"
        case _:
            raise ValueError("Provided fuzz-lang type is not valid.")


class CodeGeneration:
    """A class to perform code generation on a fuzz-lang AST."""

    target_code: list[str]

    def __init__(self):
        """Constructor for the fuzz-lang code generation module."""
        self.reset()

    def reset(self) -> None:
        """A method to reset the target code."""
        self.target_code = []

    @staticmethod
    def _construct_rust_loop(node: Loop):
        return f"for {node.element_name} in {node.collection_name}.iter() {{"

    def _construct_rust_assignment(self, node: AssignmentStatement):
        expr = self.generate_expression(node.expr)

        if node.var_type == "array":
            return f"let {node.var_name}: [{get_rust_type(node.expr._type)}; {node.expr.length}] = {expr};"
        else:
            return f"let {node.var_name}: {get_rust_type(node.var_type)} = {expr};"

    def _construct_rust_print_statement(self, node: PrintStatement):
        expr = self.generate_expression(node.expr)
        return f'println!("{{}}", {expr});'

    def _construct_rust_function_header(self, node: Function):
        return f"fn {node.func_name}({node.arg}: {get_rust_type(node.input_type)}) -> {get_rust_type(node.output_type)} {{"

    def _construct_rust_return_statement(self, node: ReturnStatement):
        expr = self.generate_expression(node.expr)
        return f"return {expr};}}"

    def code_generation(self, ast: list[Node]) -> str:
        """A method to perform code generation on an abstract syntax tree."""
        self.reset()
        self.target_code.append("fn main() {")

        i = 0

        while i < len(ast):
            node = ast[i]
            match type(node):
                case Nodes.LOOP.value:
                    self.target_code.append(self._construct_rust_loop(node))

                case Nodes.END_LOOP.value:
                    self.target_code.append(node.token)

                case Nodes.ASSIGNMENT.value:
                    self.target_code.append(self._construct_rust_assignment(node))

                case Nodes.PRINT.value:
                    self.target_code.append(self._construct_rust_print_statement(node))

                case Nodes.FUNCTION.value:
                    counter = 0

                    self.target_code.insert(
                        counter,
                        self._construct_rust_function_header(node),
                    )
                    counter += 1
                    i += 1
                    node = ast[i]
                    while type(node) in [Nodes.ASSIGNMENT.value]:
                        self.target_code.insert(
                            counter,
                            self._construct_rust_assignment(node),
                        )
                        counter += 1
                        i += 1
                        node = ast[i]

                    if type(node) is not Nodes.RETURN.value:
                        raise RuntimeError()
                    else:
                        self.target_code.insert(
                            counter, self._construct_rust_return_statement(node)
                        )

                case _:
                    raise SyntaxError("Cannot generate code for this Node.")

            i += 1

        self.target_code.append("}")
        return "\n".join(self.target_code)

    def generate_expression(self, expr: Any) -> str:
        """A  method to generate an expression."""
        match type(expr):
            case Nodes.BINARY.value:
                left = self.generate_expression(expr.left)
                right = self.generate_expression(expr.right)
                return f"{left} {expr.op} {right}"

            case Nodes.VARIABLE.value:
                return expr.name

            case Nodes.NUMBER.value:
                return str(expr.value)

            case Nodes.FUNCTION_CALL.value:
                return f"{expr.func_name}({expr.arg})"

            case Nodes.STRING.value:
                return expr.value

            case Nodes.ARRAY.value:
                return expr.values

            case _:
                raise RuntimeError("Unknown expression type")
