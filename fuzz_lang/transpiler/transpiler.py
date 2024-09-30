import argparse
import os
import subprocess

from fuzz_lang.transpiler.code_gen import CodeGeneration
from fuzz_lang.transpiler.lexical_analysis import Tokenizer
from fuzz_lang.transpiler.parsing import parse


def compiler():
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
    subprocess.run([f"./{args.program}"], check=True)


if __name__ == "__main__":
    compiler()
