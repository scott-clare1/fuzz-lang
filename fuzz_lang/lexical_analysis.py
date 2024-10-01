"""A module for performing lexical analysis on fuzz-lang source code."""

import re
from enum import StrEnum


class Tokenizer(StrEnum):
    """An enum representing the available tokens in the language."""

    NUMBER = r"[+-]?([0-9]*[.])?[0-9]+"
    ASSIGNMENT = r"fuzzy"
    ARROW = r"\->"
    OP = r"[+\-*/]"
    EQUALS = r"="
    PRINT = r"labs"
    FUNCTION = r"suzy"
    RETURN = r"flabs"
    LBRACK = r"\{"
    RBRACK = r"\}"
    LSBRACK = r"\["
    RSBRACK = r"\]"
    LPAREN = r"\("
    RPAREN = r"\)"
    SEMICOLON = r";"
    LOOP = r"every"
    COMMA = r","
    COMMENT = r"comment:+.*"
    SKIP = r"[ \t]+"
    NEWLINE = r"\n"
    ID = r"[a-zA-Z_][a-zA-Z_]*"
    STRING = r'"+.*"'
    MISMATCH = r"."

    @classmethod
    def regex(cls) -> str:
        """The regex string generated from enum variants."""
        return "|".join(f"(?P<{variant.name}>{variant})" for variant in cls)

    @classmethod
    def tokenize(cls, code: str) -> list[str]:
        """A method to perform tokenisation on some source code."""
        tokens = []
        for match in re.finditer(cls.regex(), code):
            kind = match.lastgroup
            value = match.group()
            if kind == cls.NUMBER.name:
                value = float(value) if "." in value else int(value)
            elif any(
                item.name == kind for item in [cls.SKIP, cls.NEWLINE, cls.COMMENT]
            ):
                continue
            elif kind == cls.MISMATCH.name:
                raise RuntimeError(f"Unexpected character: {value}")
            tokens.append((kind, value))
        return tokens
