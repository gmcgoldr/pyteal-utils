ABI Types
--------

Each ABIType must implement encode/decode to convert to and from over the wire formats to stack types

For Uint8-64 this means converting to TealType.uint64
For Uint64-512 this means converting to a set of TealType.uint64s
for String/Bytes[] this means converting to TealType.bytes


# TODO
# generalize uint stuff, use passed in arg to create encoder/decoders

# byte? get/set byte
# bool? get/set bit

# ufixed<N>x<M>: An N-bit unsigned fixed-point decimal number with precision M, where 8 <= N <= 512, N % 8 = 0, and 0 < M <= 160, which denotes a value v as v / (10^M).
# address: Used to represent a 32-byte Algorand address. This is equivalent to byte[32].
# <type>[<N>]: A fixed-length array of length N, where N >= 0. type can be any other type.
# <type>[]: A variable-length array. type can be any other type.
# (T1,T2,...,TN): A tuple of the types T1, T2, …, TN, N >= 0.


Dynamic Types are passed directly with no 
