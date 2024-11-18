import inspect

from pyconchina2024_code.jit import AstCompiler


def abc(a, b):
    return a + b


def test_jit():
    source_code = inspect.getsource(abc)
    compiler = AstCompiler(source_code)
    with open("test.txt", "w") as f:
        f.write(compiler.show())
