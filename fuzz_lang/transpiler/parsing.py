"""A module for parsing fuzz-lang tokens into an abstract syntax tree."""

from enum import Enum, StrEnum
from typing import Any, Optional

from fuzz_lang.transpiler.lexical_analysis import Tokenizer


class LetStatement:
    def __init__(self, var_name: str, var_type: str, expr: Any):
        self.var_name = var_name
        self.var_type = var_type
        self.expr = expr


class BinaryOp:
    def __init__(self, left: Any, op: str, right: Any):
        self.left = left
        self.op = op
        self.right = right


class Number:
    def __init__(self, value: str):
        self.value = value


class String:
    def __init__(self, value: str):
        self.value = value


class Array:
    values: list[Any] = []

    def __init__(self, _type: str, length: int):
        self._type = _type
        self.length = length


class Loop:
    def __init__(self, collection_name: str, element_name: str):
        self.collection_name = collection_name
        self.element_name = element_name


class Variable:
    def __init__(self, name: str):
        self.name = name


class Function:
    def __init__(
        self,
        func_name: str,
        arg: str,
        input_type: Optional[str] = None,
        output_type: Optional[str] = None,
    ):
        self.func_name = func_name
        self.arg = arg
        self.input_type = input_type
        self.output_type = output_type


class ReturnStatement:
    def __init__(self, expr: Variable | Number):
        self.expr = expr


class FunctionCall(Function):
    pass


class EndLoop:
    def __init__(self):
        self.token = "}"


class PrintStatement:
    def __init__(self, expr: Variable | Number):
        self.expr = expr


class Types(StrEnum):
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    ARRAY = "array"


class Nodes(Enum):
    ASSIGNMENT = LetStatement
    PRINT = PrintStatement
    BINARY = BinaryOp
    NUMBER = Number
    VARIABLE = Variable
    FUNCTION = Function
    RETURN = ReturnStatement
    FUNCTION_CALL = FunctionCall
    STRING = String
    ARRAY = Array
    LOOP = Loop
    END_LOOP = EndLoop


def parse(tokens: list[str]) -> list[Any]:
    """A function to build an abstract syntax tree from a collection of tokens."""
    ast: list[Any] = []
    i = 0

    while i < len(tokens):
        token_type, token_value = tokens[i][0], tokens[i][1]

        match token_type:
            case Tokenizer.FUNCTION.name:
                offset = 1
                func_name = tokens[i + offset][1]
                offset += 1
                if tokens[i + offset][0] == Tokenizer.LPAREN.name:
                    offset += 1
                    arg = tokens[i + offset]
                    offset += 3
                    if Tokenizer.ID.name != arg[0]:
                        raise RuntimeError(f"Unexpected argument value: {token_value}")

                    input_type = tokens[i + offset]

                    offset += 2

                    output_type = tokens[i + offset]

                    offset += 3

                else:
                    raise SyntaxError("Function is not constructed properly.")

                ast.append(Function(func_name, arg[1], input_type[1], output_type[1]))
                i += offset

            case Tokenizer.RETURN.name:
                offset = 1
                value = tokens[i + offset]
                offset += 1
                if value[0] == "ID":
                    expr = Variable(value[1])
                elif value[0] == "NUMBER":
                    expr = Number(value[1])
                else:
                    raise SyntaxError("Can only return identifiers or numbers.")

                ast.append(ReturnStatement(expr))
                i += offset + 1

            case Tokenizer.RBRACK.name:
                ast.append(EndLoop())
                i += 1

            case Tokenizer.LOOP.name:
                offset = 1
                element = tokens[i + offset]
                offset += 2
                collection = tokens[i + offset]
                offset += 1

                ast.append(Loop(collection[1], element[1]))
                i += offset + 1

            case Tokenizer.ASSIGNMENT.name:
                offset = 1
                var_type = tokens[i + offset][1]
                offset += 1
                if var_type not in Types:
                    raise RuntimeError(f"Invalid type: {var_type}")

                if var_type == Types.ARRAY:
                    offset += 1
                    _type = tokens[i + offset][1]
                    offset += 2
                    length = tokens[i + offset][1]
                    offset += 2
                    array = Array(_type, int(length))
                else:
                    array = None

                var_name = tokens[i + offset][1]
                offset += 1
                if tokens[i + offset][0] == Tokenizer.EQUALS.name:
                    offset += 1
                    left_operand = tokens[i + offset]
                    offset += 1
                    operator = (
                        tokens[i + offset]
                        if tokens[i + offset][0] == Tokenizer.OP.name
                        else None
                    )
                    if operator:
                        offset += 1
                        right_operand = tokens[i + offset]
                        offset += 1
                    else:
                        right_operand = None

                    left_expr = None
                    right_expr = None

                    if left_operand[0] == Tokenizer.ID.name:
                        if (
                            not operator
                            and tokens[i + offset][0] == Tokenizer.LPAREN.name
                        ):
                            offset += 1
                            left_expr = FunctionCall(
                                left_operand[1], tokens[i + offset][1]
                            )
                            offset += 2
                        else:
                            left_expr = Variable(left_operand[1])
                    elif left_operand[0] == Tokenizer.NUMBER.name:
                        left_expr = Number(left_operand[1])
                    elif left_operand[0] == Tokenizer.STRING.name:
                        left_expr = String(left_operand[1])

                    elif left_operand[0] == Tokenizer.LSBRACK.name:
                        value = tokens[i + offset]
                        offset += 1
                        if not array:
                            raise SyntaxError(
                                "Using square brackets in non-array based value."
                            )
                        array.values.append(value[1])
                        while value[0] != Tokenizer.RSBRACK.name:
                            value = tokens[i + offset]
                            offset += 1
                            if value[0] == Tokenizer.NUMBER.name:
                                array.values.append(value[1])

                        left_expr = array

                    if operator:
                        if not right_operand:
                            raise SyntaxError("No right operand declared.")

                        if not left_expr:
                            raise SyntaxError("No left expression declared.")

                        if right_operand[0] == Tokenizer.ID.name:
                            right_expr = Variable(right_operand[1])
                        elif right_operand[0] == Tokenizer.NUMBER.name:
                            right_expr = Number(right_operand[1])

                        if not right_expr:
                            raise SyntaxError("No right expression declared.")
                        expr = BinaryOp(left_expr, operator[1], right_expr)
                    else:
                        expr = left_expr
                        if not expr:
                            raise SyntaxError("No expression declared.")
                    ast.append(LetStatement(var_name, var_type, expr))
                else:
                    raise RuntimeError("Expected '=' after variable declaration")

                i += offset

                if i < len(tokens) and tokens[i][0] == "SEMICOLON":
                    i += 1

            case "PRINT":
                offset = 1

                if tokens[i + offset][0] == "LPAREN":
                    offset += 1
                    value = tokens[i + offset]

                    if value[0] == "ID":
                        expr = Variable(value[1])
                    elif value[0] == "NUMBER":
                        expr = Number(value[1])
                    else:
                        raise SyntaxError("Can only print identifiers or numbers.")

                    ast.append(PrintStatement(expr))
                else:
                    raise RuntimeError("Expected '(' after 'print'")

                offset += 3

                i += offset  # Move to the next statement

                if i < len(tokens) and tokens[i][0] == "SEMICOLON":
                    i += 1  # Skip over the semicolon

            case _:
                raise RuntimeError(f"Unexpected token: {token_value}")

    return ast
