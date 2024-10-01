"""A module for parsing fuzz-lang tokens into an abstract syntax tree."""

from enum import Enum, StrEnum
from typing import Any, Optional
from abc import ABC, abstractmethod

from fuzz_lang.transpiler.lexical_analysis import Tokenizer


Tokens = list[tuple[str, str]]


class Node(ABC):
    offset: int = 1

    def __init__(self, tokens: Tokens) -> None:
        self._build_node(tokens)

    @abstractmethod
    def _build_node(self, tokens: Tokens) -> None:
        pass


class LetStatement(Node):
    var_name: str
    var_type: str
    expr: Any

    def _build_node(self, tokens: Tokens) -> None:
        self.var_type = tokens[self.offset][1]
        self.offset += 1
        if self.var_type not in Types:
            raise RuntimeError(f"Invalid type: {self.var_type}")

        if self.var_type == Types.ARRAY:
            self.offset += 1
            _type = tokens[self.offset][1]
            self.offset += 2
            length = tokens[self.offset][1]
            self.offset += 2
            array = Array(_type, int(length))
        else:
            array = None

        self.var_name = tokens[self.offset][1]
        self.offset += 1
        if tokens[self.offset][0] == Tokenizer.EQUALS.name:
            self.offset += 1
            left_operand = tokens[self.offset]
            self.offset += 1
            operator = (
                tokens[self.offset]
                if tokens[self.offset][0] == Tokenizer.OP.name
                else None
            )
            if operator:
                self.offset += 1
                right_operand = tokens[self.offset]
                self.offset += 1
            else:
                right_operand = None

            left_expr = None
            right_expr = None

            if left_operand[0] == Tokenizer.ID.name:
                if not operator and tokens[self.offset][0] == Tokenizer.LPAREN.name:
                    self.offset += 1
                    left_expr = FunctionCall(left_operand[1], tokens[self.offset][1])
                    self.offset += 2
                else:
                    left_expr = Variable(left_operand[1])
            elif left_operand[0] == Tokenizer.NUMBER.name:
                left_expr = Number(left_operand[1])
            elif left_operand[0] == Tokenizer.STRING.name:
                left_expr = String(left_operand[1])

            elif left_operand[0] == Tokenizer.LSBRACK.name:
                value = tokens[self.offset]
                self.offset += 1
                if not array:
                    raise SyntaxError("Using square brackets in non-array based value.")
                array.values.append(value[1])
                while value[0] != Tokenizer.RSBRACK.name:
                    value = tokens[self.offset]
                    self.offset += 1
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
                self.expr = BinaryOp(left_expr, operator[1], right_expr)
            else:
                self.expr = left_expr
                if not self.expr:
                    raise SyntaxError("No expression declared.")
        else:
            raise RuntimeError("Expected '=' after variable declaration")


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


class Loop(Node):
    collection_name: str
    element_name: str

    def _build_node(self, tokens: Tokens) -> None:
        self.offset = 1
        self.element_name = tokens[self.offset][1]
        self.offset += 2
        self.collection_name = tokens[self.offset][1]
        self.offset += 2


class Variable:
    def __init__(self, name: str):
        self.name = name


class Function(Node):
    func_name: str
    arg: str
    input_type: str
    output_type: str

    def _build_node(self, tokens: Tokens) -> None:
        self.func_name = tokens[self.offset][1]
        self.offset += 1
        if tokens[self.offset][0] == Tokenizer.LPAREN.name:
            self.offset += 1
            self.arg = tokens[self.offset][1]
            if Tokenizer.ID.name != tokens[self.offset][0]:
                raise RuntimeError("Unexpected argument value provided.")

            self.offset += 3

            self.input_type = tokens[self.offset][1]

            self.offset += 2

            self.output_type = tokens[self.offset][1]

            self.offset += 3

        else:
            raise SyntaxError("Function is not constructed properly.")


class ReturnStatement(Node):
    expr: Variable | Number
    offset = 1

    def _build_node(self, tokens: Tokens):
        value = tokens[self.offset]
        self.offset += 1
        if value[0] == "ID":
            self.expr = Variable(value[1])
        elif value[0] == "NUMBER":
            self.expr = Number(value[1])
        else:
            raise SyntaxError("Can only return identifiers or numbers.")
        self.offset += 1


class FunctionCall:
    def __init__(
        self,
        func_name: str,
        arg: str,
        input_type: Optional[str] = None,
        output_type: Optional[str] = None,
    ) -> None:
        self.func_name = func_name
        self.arg = arg
        self.input_type = input_type
        self.output_type = output_type


class EndLoop(Node):
    token = "}"
    offset = 1

    def _build_node(self, tokens: Tokens) -> None:
        return super()._build_node(tokens)


class PrintStatement(Node):
    expr: Variable | Number

    def _build_node(self, tokens: Tokens) -> None:
        if tokens[self.offset][0] == "LPAREN":
            self.offset += 1
            value = tokens[self.offset]

            if value[0] == "ID":
                self.expr = Variable(value[1])
            elif value[0] == "NUMBER":
                self.expr = Number(value[1])
            else:
                raise SyntaxError("Can only print identifiers or numbers.")
        else:
            raise SyntaxError("Expected '(' after 'print'")

        self.offset += 3


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


def process_token(tokens: Tokens) -> Node:
    current_token = tokens[0]
    match current_token[0]:
        case Tokenizer.FUNCTION.name:
            node = Function(tokens)

        case Tokenizer.RETURN.name:
            node = ReturnStatement(tokens)

        case Tokenizer.RBRACK.name:
            node = EndLoop(tokens)

        case Tokenizer.LOOP.name:
            node = Loop(tokens)

        case Tokenizer.ASSIGNMENT.name:
            node = LetStatement(tokens)

        case Tokenizer.PRINT.name:
            node = PrintStatement(tokens)

        case _:
            raise RuntimeError(f"Unexpected token: {current_token[1]}")

    if node.offset < len(tokens) and tokens[node.offset][0] == "SEMICOLON":
        node.offset += 1
    return node


def parse(tokens: Tokens) -> list[Node]:
    """A function to build an abstract syntax tree from a collection of tokens."""
    ast: list[Node] = []

    while tokens:
        node = process_token(tokens)
        ast.append(node)
        tokens = tokens[node.offset :]

    return ast
