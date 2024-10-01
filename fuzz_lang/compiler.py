"""Script to compile fuzz-lang code."""

import argparse
import os
import subprocess

from fuzz_lang.code_gen import CodeGeneration
from fuzz_lang.lexical_analysis import Tokenizer
from fuzz_lang.parsing import parse


def compiler():
    """A function to compile fuzz-lang source code to rust."""
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("program")

    args = parser.parse_args()

    with open(args.filename) as f:
        source_code = f.read()

    tokens = Tokenizer.tokenize(source_code)
    ast = parse(tokens)

    code_generator = CodeGeneration()

    rust_code = code_generator.code_generation(ast)

    os.makedirs("__transpiled__", exist_ok=True)

    with open(f"__transpiled__/{args.program}.rs", "w") as f:
        f.write(rust_code)

    subprocess.run(["rustc", f"__transpiled__/{args.program}.rs"], check=True)


if __name__ == "__main__":
    compiler()
