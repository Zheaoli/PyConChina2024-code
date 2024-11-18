import inspect

from pyconchina2024_code.jit import AstCompiler


def test_add():
    def abc(a, b):
        return a + b

    source_code = inspect.getsource(abc)
    compiler = AstCompiler(source_code)
    func = compiler.compile()
    assert func(1, 2) == 3


def test_sub():
    def abc(a, b):
        return a - b

    source_code = inspect.getsource(abc)
    compiler = AstCompiler(source_code)
    func = compiler.compile()
    assert func(1, 2) == -1


def test_mul():
    def abc(a, b):
        return a * b

    source_code = inspect.getsource(abc)
    compiler = AstCompiler(source_code)
    func = compiler.compile()
    assert func(3, 2) == 6


def test_div():
    def abc(a, b):
        return a / b

    source_code = inspect.getsource(abc)
    compiler = AstCompiler(source_code)
    func = compiler.compile()
    assert func(6, 2) == 3
