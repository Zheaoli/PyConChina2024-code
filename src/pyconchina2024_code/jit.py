import ast
import inspect
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
    def __init__(self, args_len, code):
        self.memory_buffer = mmap.mmap(
            -1, len(code), mmap.MAP_PRIVATE, mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC
        )
        self.memory_buffer[: len(code)] = code
        fnc_type = f"fn{args_len}"
        self.fn = ffi.cast(fnc_type, ffi.from_buffer(self.memory_buffer))

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
        self.reg_allocator = None

    def show(self):
        return ast_to_mermaid(self.tree)

    def _new_func(self, name, args_names):
        self.assembler = FunctionAssembler(name, args_names)
        self.reg_allocator = RegisterAllocator()
        for name in args_names:
            self.reg_allocator.get(name)
        self.tmp0 = self.reg_allocator.get("__scratch_register_0__")
        self.tmp1 = self.reg_allocator.get("__scratch_register_1__")

    def visit(self, node):
        methname = node.__class__.__name__
        meth = getattr(self, methname, None)
        if meth is None:
            raise NotImplementedError(methname)
        return meth(node)

    def Module(self, node):
        for child in node.body:
            self.visit(child)

    def FunctionDef(self, node):
        assert not self.assembler, "cannot compile more than one function"
        argnames = [arg.arg for arg in node.args.args]
        self._new_func(node.name, argnames)
        for child in node.body:
            self.visit(child)
        # return 0 by default
        self.assembler.PXOR(self.assembler.xmm0, self.assembler.xmm0)
        self.assembler.RET()

    def Pass(self, node):
        pass

    def Return(self, node):
        self.visit(node.value)
        self.assembler.popsd(self.assembler.xmm0)
        self.assembler.RET()

    def Num(self, node):
        self.assembler.MOVSD(self.tmp0, self.assembler.const(node.n))
        self.assembler.pushsd(self.tmp0)

    def BinOp(self, node):
        OPS = {
            "ADD": self.assembler.ADDSD,
            "SUB": self.assembler.SUBSD,
            "MULT": self.assembler.MULSD,
            "DIV": self.assembler.DIVSD,
        }
        opname = node.op.__class__.__name__.upper()
        self.visit(node.left)
        self.visit(node.right)
        self.assembler.popsd(self.tmp1)
        self.assembler.popsd(self.tmp0)
        OPS[opname](self.tmp0, self.tmp1)
        self.assembler.pushsd(self.tmp0)

    def Name(self, node):
        reg = self.reg_allocator.get(node.id)
        self.assembler.pushsd(reg)

    def compile(self):
        self.visit(self.tree)
        assert self.assembler is not None, "No function found?"
        code = self.assembler.assemble_and_relocate()
        return CompiledFunction(self.assembler.nargs, code)


def compile(func):
    compiler = AstCompiler(inspect.getsource(func))
    return compiler.compile()
