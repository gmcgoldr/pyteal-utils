from pyteal import Expr, Int, Bytes, TealType, Itob, Btoi
from pyteal import Subroutine, If, Exp, Len, Substring, GetByte, Concat

from .math import ilog10

# Wants

# ** syntax for exponentiation
# [] access to byte array; getbyte, substr
# Int => actual int


ascii_offset = Int(48)  # Magic number to convert between ascii chars and integers 

@Subroutine(TealType.uint64)
def ascii_to_int(arg: TealType.uint64):
    return arg - ascii_offset

@Subroutine(TealType.bytes)
def int_to_ascii(arg: TealType.uint64):
    #return arg + ascii_offset Just returns a uint64, cant convert to bytes type
    return Substring(Bytes("0123456789"), arg, arg+Int(1))
 
@Subroutine(TealType.uint64)
def atoi(a: TealType.bytes):
    return If(
            Len(a) > Int(0),
            ( ascii_to_int(head(a)) * ilog10(Len(a)-Int(1)) ) + atoi( Substring(a,Int(1),Len(a)) ),
            Int(0)
        )

@Subroutine(TealType.bytes)
def itoa(i: TealType.uint64):
    return If(
            i == Int(0),
            Bytes(""),
            Concat( itoa(i / Int(10)), int_to_ascii(i % Int(10)) )
        )

@Subroutine(TealType.uint64)
def head(s: TealType.bytes):
    return GetByte(s, Int(0))

@Subroutine(TealType.bytes)
def tail(s: TealType.bytes):
    return Substring(s, Int(1), Len(s))

@Subroutine(TealType.uint64)
def strpos(s: TealType.bytes, sub: TealType.bytes):
    return 0 
