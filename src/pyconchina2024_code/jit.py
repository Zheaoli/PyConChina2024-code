import ast
import mmap
import textwrap
from collections import defaultdict

from cffi import FFI

from pyconchina2024_code.assember import FunctionAssembler
from pyconchina2024_code.mermaid import ast_to_mermaid

ffi = FFI()

ffi.cdef(
    """
    typedef double (*fn1)(double);
    typedef double (*fn2)(double, double);
    typedef double (*fn3)(double, double, double);
"""
)


class CompiledFunction:
    def __init__(self, nargs, code):
        self.memory_buffer = mmap.mmap(
            -1, len(code), mmap.MAP_PRIVATE, mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC
        )
        self.memory_buffer[: len(code)] = code
        fnc_type = f"fn{len(nargs)}"
        self.fn = ffi.cast(fnc_type, self.memory_buffer)

    def __call__(self, *args):
        return self.fn(*args)


class RegisterAllocator:
    REGISTERS = (
        FunctionAssembler.xmm0,
        FunctionAssembler.xmm1,
        FunctionAssembler.xmm2,
        FunctionAssembler.xmm3,
        FunctionAssembler.xmm4,
        FunctionAssembler.xmm5,
        FunctionAssembler.xmm6,
        FunctionAssembler.xmm7,
        FunctionAssembler.xmm8,
        FunctionAssembler.xmm9,
        FunctionAssembler.xmm10,
        FunctionAssembler.xmm11,
        FunctionAssembler.xmm12,
        FunctionAssembler.xmm13,
        FunctionAssembler.xmm14,
        FunctionAssembler.xmm15,
    )

    def __init__(self):
        self._registers = list(reversed(self.REGISTERS))
        self.vars = defaultdict(self._allocate)

    def _allocate(self):
        try:
            return self._registers.pop()
        except IndexError as e:
            raise NotImplementedError("Too many variables: register spilling not implemented") from e

    def get(self, var):
        return self.vars[var]


class AstCompiler:
    def __init__(self, source_code):
        self.tree = ast.parse(textwrap.dedent(source_code))
        self.assembler = None

    def show(self):
        return ast_to_mermaid(self.tree)
