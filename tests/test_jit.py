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


def test_basic_jit():
    """
    push rbp          ; 55
    mov rbp, rsp      ; 48 89 e5
    mov eax, edi      ; 89 f8
    add eax, esi      ; 01 f0
    pop rbp           ; 5d
    ret               ; c3
    """
    import mmap

    from cffi import FFI

    byte = bytearray(b"\x55\x48\x89\xe5\x48\x89\xf8\x48\x01\xf0\x5d\xc3")
    buffer = mmap.mmap(-1, len(byte), mmap.MAP_PRIVATE, mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC)
    buffer[: len(byte)] = byte
    ffi = FFI()

    ffi.cdef("typedef int (*fn2)(int, int);")
    fn = ffi.cast("fn2", ffi.from_buffer(buffer))
    assert fn(1, 2) == 3
