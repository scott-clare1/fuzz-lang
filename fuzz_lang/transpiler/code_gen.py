"""A module for performing code generation for fuzz-lang."""

from typing import Any

from fuzz_lang.transpiler.parsing import Nodes


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

    def code_generation(self, ast: list[Any]) -> str:
        """A method to perform code generation on an abstract syntax tree."""
        self.reset()
        self.target_code.append("fn main() {")

        i = 0

        while i < len(ast):
            node = ast[i]
            match type(node):
                case Nodes.LOOP.value:
                    self.target_code.append(
                        f"for {node.element_name} in {node.collection_name}.iter() {{"
                    )

                case Nodes.END_LOOP.value:
                    self.target_code.append(node.token)

                case Nodes.ASSIGNMENT.value:
                    var_name = node.var_name
                    expr = self.generate_expression(node.expr)
                    if node.var_type == "array":
                        self.target_code.append(
                            f"let {var_name}: [{get_rust_type(node.expr._type)}; {node.expr.length}] = {expr};"
                        )
                    else:
                        self.target_code.append(
                            f"let {var_name}: {get_rust_type(node.var_type)} = {expr};"
                        )

                case Nodes.PRINT.value:
                    expr = self.generate_expression(node.expr)
                    self.target_code.append(f'println!("{{}}", {expr});')

                case Nodes.FUNCTION.value:
                    counter = 0

                    self.target_code.insert(
                        counter,
                        f"fn {node.func_name}({node.arg}: {get_rust_type(node.input_type)}) -> {get_rust_type(node.output_type)} {{",
                    )
                    counter += 1
                    i += 1
                    node = ast[i]
                    while type(node) in [Nodes.ASSIGNMENT.value]:
                        var_name = node.var_name
                        expr = self.generate_expression(node.expr)
                        self.target_code.insert(
                            counter,
                            f"let {var_name}: {get_rust_type(node.var_type)} = {expr};",
                        )
                        counter += 1
                        i += 1
                        node = ast[i]

                    if type(node) is not Nodes.RETURN.value:
                        raise RuntimeError()
                    else:
                        expr = self.generate_expression(node.expr)
                        self.target_code.insert(counter, f"return {expr};}}")

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
