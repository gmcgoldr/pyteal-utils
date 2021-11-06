from ast import *

with open("thing.py", "r") as f:
    source = f.read()

tree = parse(source)

class RewriteFor(NodeTransformer):
    def visit_For(self, node):
        i = node.target.id
        maxval = node.iter.args[0].value

        declare = Assign(
            targets=[Name(id=i, ctx=Store())],
            value=Call(
                func=Name(id='ScratchVar', ctx=Load()),
                args=[], keywords=[]
            )
        )

        initialize = Assign(
            targets=[Name('init', ctx=Store())],
            value = Call(
               func=Attribute(
                   value=Name(id=i, ctx=Load()),
                   attr='store',
                   ctx=Load()),
                   args=[Constant(value=0)],
                   keywords=[]
                )
        )


        comparator = Assign(
           targets=[Name(id='comp', ctx=Store())],
           value=Compare(
               left=Call(
                   func=Attribute(
                       value=Name(id='s', ctx=Load()),
                       attr='load',
                       ctx=Load()
                   ),
                   args=[],
                   keywords=[]
                ),
                ops=[Lt()],
                comparators=[
                   Call(
                       func=Name(id='Int', ctx=Load()),
                       args=[Constant(value=maxval)],
                       keywords=[]
                    )
                ]
            )
        )

        increment = Assign(
           targets=[Name(id='incr', ctx=Store())],
           value=Call(
               func=Attribute(
                   value=Name(id=i, ctx=Load()),
                   attr='store',
                   ctx=Load()),
               args=[
                   BinOp(
                       left=Call(
                           func=Attribute(
                               value=Name(id=i, ctx=Load()),
                               attr='load',
                               ctx=Load()),
                           args=[],
                           keywords=[]),
                       op=Add(),
                       right=Constant(value=1))],
               keywords=[]
            )
        )

        new_for = Expr(
            value=Call(
                func=Attribute(
                    value=Call(
                        func=Name(id='For', ctx=Load()),
                        args=[ 
                            Name(id='init', ctx=Load()), 
                            Name(id='comp', ctx=Load()), 
                            Name(id='incr', ctx=Load())
                        ]
                    ),
                    attr='Do',
                    ctx=Load()
                ),
                args=[Call(
                    func=Name(id='Log', ctx=Load()),
                    args=[Call(
                        func=Name(id='Itob', ctx=Load()),
                        args=[Call(
                            func=Attribute(
                                value=Name(id=i, ctx=Load()),
                                attr='load',
                                ctx=Load()
                            ),
                        )],
                    )],
                )]
            )
        )

        return [
            declare, 
            initialize, 
            comparator, 
            increment, 
            new_for
        ]

print(fix_missing_locations(
    RewriteFor().visit(tree)
))

print(dump(tree, indent=4))

