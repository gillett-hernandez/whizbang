#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File Name: sparkle.py
# @Author: Copyright (c) 2017-02-02 17:31:33 Gillett Hernandez
# @Date:   2017-02-02 17:31:33
# @Last Modified by:   Gillett Hernandez
# @Last Modified time: 2017-02-18 22:40:50

import re
from enum import Enum
from collections import OrderedDict, ChainMap

global debug
debug = False

# token matchers
token_regexs = (
    ("Whitespace" , r'[ \t\r\n]+'),
    ("Comment"    , r'/\*.*?\*/'),
    ("Return"     , r'return'),
    ("Let"        , r'let'),
    ("Fn"         , r'fn'),
    ("Integer"    , r'[0-9]+'),
    ("Ident"      , r'[a-zA-Z_$][a-zA-Z0-9_$]*'),
    ("Comma"      , r','),
    ("LParen"     , r'\('),
    ("RParen"     , r'\)'),
    ("LBrace"     , r'{'),
    ("RBrace"     , r'}'),
    ("Semicolon"  , r';'),
    ("Function"   , r'->'),
    ("Plus"       , r'\+'),
    ("Minus"      , r'-'),
    ("Times"      , r'\*'),
    ("Divide"     , r'/'),
    ("Modulo"     , r'%'),
    ("Assign"     , r'='),
    ("EOF"        , r'$')
)
token_regexs = OrderedDict(token_regexs)

# language grammer
# start      ::= statement*
# statement  ::= expression ';'?
#            ::= 'return' expression  ';'?
#            ::= 'let' identifier '=' expression ';'?
#            ::= '{' statement* '}'
# expression ::= assignment
#            ::= 'fn' '(' (identifier (',' identifier)*)? ')' -> statement
# assignment ::= additive ('=' expression)*
# additive   ::= multiply (('+'|'-') multiply)*
# multiply   ::= postfix (('*'|'/'|'%') postfix)*
# postfix    ::= terminal
#            ::= terminal '(' (expression (',' expression)*)? ')'
# terminal   ::= integer
#            ::= identifier
#            ::= '(' expression ')'
# integer    ::= [0-9]+
# identifier ::= [a-zA-Z_$][a-zA-Z0-9_$]*


# tokens
class T(Enum):
    Root       = "Start"
    Whitespace = "Whitespace"
    Comment    = "Comment"
    Return     = "Return"
    Arrow      = "Arrow"
    Let        = "Let"
    Fn         = "Fn"
    Integer    = "Integer"
    Ident      = "Ident"
    Comma      = "Comma"
    LParen     = "LParen"
    RParen     = "RParen"
    LBrace     = "LBrace"
    RBrace     = "RBrace"
    Semicolon  = "Semicolon"
    Function   = "Function"
    Plus       = "Plus"
    Minus      = "Minus"
    Times      = "Times"
    Divide     = "Divide"
    Modulo     = "Modulo"
    Assign     = "Assign"
    EOF        = "EOF"
    OP         = "operator"
    FCALL      = "FunctionCall"
    Assignment = "Assignment"
    Block      = "BlockStatement"

opcodes = {
    "+": "AD",
    "-": "SU",
    "*": "MU",
    "/": "DI",
    "imm": "IM",
    "arg": "AR"
}

class Node(object):
    __slots__ = ['op', 'token', 'ti']
    def __init__(self, optype):
        self.op = optype
        self.token = ""
        self.ti = 0

    # def __repr__(self):
    #     # print("node repr")
    #     if hasattr(self, 'n'):
    #         string2 = ", 'n': {}".format(self.n)
    #     elif hasattr(self, 'a') and hasattr(self, 'b'):
    #         string2 = ", 'a': {0!r}, 'b': {1!r}".format(self.a, self.b)
    #     elif any(e not in Node.__slots__ for e in self.__slots__):
    #         string2 = ", " + ", ".join("'{}': '{}'".format(k, getattr(self, k)) for k in self.__slots__)
    #     else:
    #         string2 = ""
    #     string2 += ", 'token': '{}'".format(self.token)
    #     # print("op = ",self.op)
    #     # print("string2 = ", string2)
    #     rstring = "'op': '{0}'{1}".format(self.op, string2)
    #     rstring = "{" + rstring + "}"
    #     return rstring

    def __repr__(self):
        return "<{}>".format(self.token)

class Root(Node):
    __slots__ = ["statements"]
    def __init__(self, statements=None):
        super(Root, self).__init__(T.Root)
        self.statements = statements
    def visit(self, visitor):
        if isinstance(visitor, AstPrinter):
            return visitor.parenthesize(self.op, *self.statements)

class Constant(Node):
    __slots__ = ['n']
    def __init__(self, n=None):
        super(Constant, self).__init__(T.Integer)
        self.n = n
    def visit(self, visitor):
        if isinstance(visitor, AstPrinter):
            return str(self.n)

class Identifier(Node):
    __slots__ = ['identifier']
    def __init__(self, identifier=None):
        super(Identifier, self).__init__(T.Ident)
        self.identifier = identifier
    def visit(self, visitor):
        if isinstance(visitor, AstPrinter):
            return visitor.parenthesize("ID", self.identifier)

class Op(Node):
    __slots__ = ['a', 'b']
    def __init__(self, optype, a, b):
        super(Op, self).__init__(optype)
        self.a = a
        self.b = b
    def visit(self, visitor):
        if isinstance(visitor, AstPrinter):
            return visitor.parenthesize(self.op, self.a, self.b)

# class Expression(Node):
#     __slots__ = ['']

class FCall(Node):
    __slots__ = ['fn', 'args']
    def __init__(self, fn=None, args=None):
        super(FCall, self).__init__(T.FCALL)
        self.fn = fn
        self.args = args
    def visit(self, visitor):
        if isinstance(visitor, AstPrinter):
            return visitor.parenthesize("FC", self.fn, *self.args)

class ReturnStatement(Node):
    """Return statements return the expressions value to the callee's scope, or exit the program if used in the global scope"""
    __slots__ = ['expression']
    def __init__(self, expression=None):
        super(ReturnStatement, self).__init__(T.Return)
        self.expression = expression
    def visit(self, visitor):
        if isinstance(visitor, AstPrinter):
            return visitor.parenthesize("RT", self.expression)

class LetStatement(Node):
    """Let statements instantiate a variable and put it in the local scope"""
    __slots__ = ['identifier', 'expression']
    def __init__(self, identifier=None, expression=None):
        super(LetStatement, self).__init__(T.Let)
        self.identifier = identifier
        self.expression = expression
    def visit(self, visitor):
        if isinstance(visitor, AstPrinter):
            return visitor.parenthesize("{} =".format(visitor.tostring(self.identifier)), self.expression)

class Assignment(Node):
    __slots__ = ['lhs', 'rhs']
    def __init__(self, lhs=None, rhs=None):
        super(Assignment, self).__init__(T.Assignment)
        self.lhs = lhs
        self.rhs = rhs
    def visit(self, visitor):
        if isinstance(visitor, AstPrinter):
            return visitor.parenthesize(self.op, self.lhs, self.rhs)

class MultiExpressionNode(Node):
    __slots__ = ['nodes', 'ops']
    def __init__(self, nodes=[], ops=[]):
        super(MultiExpressionNode, self).__init__("MultiExpression")
        self.nodes = nodes
        self.ops = ops
    def visit(self, visitor):
        if isinstance(visitor, AstPrinter):
            s = "("
            for node, op in zip(self.nodes, self.ops):
                s += visitor.tostring(node)
                s += " {}".format(str(op))
            s += " "
            s += visitor.tostring(self.nodes[-1])
            s += ")"
            return s

class BlockStatement(Node):
    """Block statements start a new scope"""
    __slots__ = ['statements']
    def __init__(self, statements=[]):
        super(BlockStatement, self).__init__(T.Block)
        self.statements = statements
    def visit(self, visitor):
        if isinstance(visitor, AstPrinter):
            return visitor.parenthesize(self.op, *self.statements)

class Function(Node):
    """functions start a new scope with every call, but the arguments are bound to the parameters"""
    __slots__ = ['arguments', 'statements']
    def __init__(self, arguments=None, statements=None):
        super(Function, self).__init__(T.Function)
        self.arguments = arguments
        self.statements = statements
        # self.internal_name = Function.getid()
    def visit(self, visitor):
        if debug: print("Function visitor called")
        if isinstance(visitor, AstPrinter):
            return visitor.parenthesize("F", self.arguments, self.statements)

Ref = type("Ref", (object,), {"i": 0, "__repr__":(lambda self: "<Ref i={}>".format(self.i) )})

class AstPrinter:
    def tostring(self, expression):
        """handles Root, Block, Multiexpression, anything with attribute 'n',\nanything with attributes ('a', 'b')"""
        if isinstance(expression, Node):
            if debug: print(expression, type(expression), expression.op, expression.token)
            return expression.visit(self)
        elif isinstance(expression, (list, tuple)):
            return self.parenthesize("L", *expression)
        elif isinstance(expression, str):
            return expression
        elif expression is None:
            return "NULLE"
        else:
            raise RuntimeError("Unaccounted for expression " + str(locals()))

    def parenthesize(self, optype, *args):
        s = "(" + str(optype)
        for node in args:
            s += " "
            s += self.tostring(node)
        s += ")"
        return s

class Parser:
    def __init__(self, code):
        self.code = code

    def tokenizer(self, code):
        """Turn a code string into an array of tokens.  Each token
           is either '{', '}', '(', ')', '+', '-', '*', '/', a variable
           name or a number (as a string)"""
        tok_regex = "|".join("(?P<{}>{})".format(k, v) for k, v in token_regexs.items())
        token_iter = re.finditer(tok_regex, code)
        tokens = []
        parens = []
        braces = []
        self.ptable = {}
        self.btable = {}
        linenum = 1
        linestart = 0
        i = 0
        for retoken in token_iter:
            kind = retoken.lastgroup
            token = retoken.group(kind)
            if debug: print(kind, token)
            if token == '' or kind == "Whitespace":
                continue
            elif token.isdigit():
                node = Constant(int(token))
            elif token.isalpha():
                if token == "fn":
                    node = Function(None)
                elif token == "let":
                    node = LetStatement(None)
                elif token == "return":
                    node = ReturnStatement(None)
                else:
                    node = Identifier(token)
            elif token == "->":
                node = Node(T.Arrow)
            elif token in "+-*/%":
                optype = [T.Plus, T.Minus, T.Times, T.Divide, T.Modulo]["+-*/%".index(token)]
                node = Op(optype, None, None)
            elif token == '(':
                node = Node(T.LParen)
                parens.append(i)
            elif token == ')':
                node = Node(T.RParen)
                self.ptable[parens.pop()] = i
            elif token == '{':
                node = Node(T.LBrace)
                braces.append(i)
            elif token == '}':
                node = Node(T.RBrace)
                self.btable[braces.pop()] = i
            elif token == ',':
                node = Node(T.Comma)
            elif token == '=':
                node = Node(T.Assign)
            else:
                node = Node(None)
            # if debug: print(token)
            node.token = str(token)
            # if debug: print(node.token)
            node.ti = i
            tokens.append(node)
            i += 1
        if debug: print(self.ptable)
        if debug: print(parens)
        self.rptable = {b:a for a,b in self.ptable.items()}
        tokens.append(Node(T.EOF))
        return tokens

    def parse(self):
        """Returns an un-optimized AST"""
        if debug: print("tokenizer starting")
        self.orig_tokens = tokens = self.tokenizer(self.code)
        if debug: print(tokens)
        root = Root([])
        t = Ref()
        assert t.i == 0
        t.i += 1
        assert t.i == 1
        t.i -= 1
        while tokens[t.i].op != T.EOF:
            if debug: print("loop step in Parser.parse")
            node = self.parse_statement(tokens, t)
            if tokens[t.i].token == ';':
                t.i += 1

            if debug: print("node=",node)
            # if debug: print("node.expr=",node.expression)
            if debug: print("after parse_statement")
            root.statements.append(node)
            if debug: print("after append")
        return root

    def parse_statement(self, tokens, t):
        if debug: print("in parse_statement")
        if debug: self.represent_codepos(tokens, t)
        if tokens[t.i].op == T.Return:
            node = tokens[t.i]
            t.i += 1
            node.expression = self.parse_expression(tokens, t)
            return node
        elif tokens[t.i].op == T.Let:
            node = tokens[t.i]
            t.i += 1 # to identifier
            node.identifier = tokens[t.i]
            t.i += 2 # to expression start
            node.expression = self.parse_expression(tokens, t)
            return node
        elif tokens[t.i].op == T.LBrace:
            sti = tokens[t.i].ti # sti == Subjective Token Index
            if sti != t.i:
                # if theyre different
                # make end = t.i + difference of the subjective end and the subjective start
                end = t.i + (self.btable[sti] - sti)
            else:
                end = self.btable[sti]
            if debug: self.represent_codepos(tokens, t)
            if debug: print(t.i)
            if debug: print(tokens[t.i].ti)
            if debug: print(self.btable[tokens[t.i].ti])
            if debug: print(end)
            assert tokens[end].op == T.RBrace
            t.i += 1
            node = self.parse_block(tokens[t.i: end])
            t.i = end+1
            return node
        else:
            return self.parse_expression(tokens, t)

    def parse_block(self, tokenslice):
        if debug: print("block", tokenslice)
        tokenslice.append(Node(T.EOF))
        t = Ref()
        bnode = BlockStatement()
        while tokenslice[t.i].op != T.EOF:
            if debug: print("loop step in parse_block")
            node = self.parse_statement(tokenslice, t)
            if debug: print(AstPrinter().tostring(node))
            bnode.statements.append(node)
            if debug: print("tokenslice[t.i].op = ", tokenslice[t.i].op)
        return bnode

    def parse_expression(self, tokens, t):
        if debug: print("in parse_expression")
        if debug: self.represent_codepos(tokens, t)
        if tokens[t.i].op == T.Function:
            if debug: print("parsing function definition")
            node = tokens[t.i]
            assert isinstance(node, Function)
            t.i += 1 # advance past fn to lparen
            node.arguments = []
            if tokens[t.i+1].op == T.Ident:
                if debug: self.represent_codepos(tokens, t)
                t.i += 1 # advance to Identifier
                if debug: self.represent_codepos(tokens, t)
                node.arguments.append(tokens[t.i])
                t.i += 1 # advance to comma
                if debug: self.represent_codepos(tokens, t)
                if debug: print(tokens[t.i].op)
                while tokens[t.i].op == T.Comma:
                    t.i += 1
                    if debug: self.represent_codepos(tokens, t)
                    node.arguments.append(tokens[t.i])
                    t.i += 1
                    if debug: self.represent_codepos(tokens, t)
            elif tokens[t.i+1].op == T.RParen:
                t.i += 1 # advance to rparen
            else:
                raise RuntimeError("Invalid Parameters")

            if debug: self.represent_codepos(tokens, t)
            assert tokens[t.i].op == T.RParen, locals()
            t.i += 1 # advance to arrow
            assert tokens[t.i].op == T.Arrow
            t.i += 1 # advance to statement start
            node.statements = self.parse_statement(tokens, t)
            return node
        else:
            return self.parse_assignment(tokens, t)

    def parse_assignment(self, tokens, t):
        if debug: print("in parse_assignment")
        if debug: self.represent_codepos(tokens, t)
        lhs = self.parse_additive(tokens, t)
        rhs = None
        if debug: print("right before if ", tokens[t.i].op)
        if tokens[t.i].op == T.Assign:
            if debug: print("took assign branch")
            t.i += 1 # advance to "Expression" start which also subparses additional assignments
            rhs = self.parse_expression(tokens, t)
        if debug: print("lhsrhss --------- ", AstPrinter().tostring(lhs), rhs)
        if rhs is None:
            if debug: print("lhspath")
            return lhs
        else:
            return Assignment(lhs, rhs)

    def parse_additive(self, tokens, t):
        if debug: print("in parse_additive")
        if debug: self.represent_codepos(tokens, t)
        # nodes and ops zip together so that for each op[i], the subexpression is node[i] ~ op[i] ~ node[i+1]
        nodes = []
        ops = []
        nodes.append(self.parse_multiply(tokens, t))
        # if isinstance(nodes[0], MultiExpressionNode): if debug: print(nodes[0].nodes)
        while tokens[t.i].op == T.Plus or tokens[t.i].op == T.Minus:
            ops.append(tokens[t.i].op)
            t.i += 1
            nodes.append(self.parse_multiply(tokens, t))
        if debug: print("in additive ", nodes)
        if len(ops) == 0:
            return nodes[0]
        else:
            if debug: print("MultiExpressionNode path in additive")
            return MultiExpressionNode(nodes, ops)

    def parse_multiply(self, tokens, t):
        if debug: print("in parse_multiply")
        if debug: self.represent_codepos(tokens, t)
        # nodes and ops zip together so that for each op[i], the subexpression is node[i] ~ op[i] ~ node[i+1]
        nodes = []
        ops = []
        nodes.append(self.parse_postfix(tokens, t))
        while tokens[t.i].op == T.Times or tokens[t.i].op == T.Divide:
            ops.append(tokens[t.i].op)
            t.i += 1
            nodes.append(self.parse_postfix(tokens, t))
        if debug: print("nodes =", nodes)
        for node in nodes:
            if node.op == T.Integer:
                assert node.token != ""
        if debug: print("in multiply,",nodes)
        if len(ops) == 0:
            return nodes[0]
        else:
            return MultiExpressionNode(nodes, ops)

    def parse_postfix(self, tokens, t):
        if debug: print("in parse_postfix")
        if debug: self.represent_codepos(tokens, t)
        terminal = self.parse_terminal(tokens, t)
        if tokens[t.i].op == T.LParen:
            args = []
            t.i += 1
            args.append(self.parse_expression(tokens, t))
            while tokens[t.i].op == T.Comma:
                t.i += 1
                args.append(self.parse_expression(tokens,t))
            assert tokens[t.i].op == T.RParen
            t.i += 1
            if debug: print("fcall branch")
            return FCall(terminal, args)
        else:
            if debug: print("terminal = ",terminal)
            return terminal

    def parse_terminal(self, tokens, t):
        if debug: print("in parse_terminal")
        if debug: self.represent_codepos(tokens, t)
        if tokens[t.i].op == T.LParen:
            t.i += 1
            node = self.parse_expression(tokens, t)
            assert tokens[t.i].op == T.RParen
            t.i += 1
            return node
        elif tokens[t.i].op == T.Ident:
            node = tokens[t.i]
            t.i += 1
            if debug: print(node)
            return node
        elif tokens[t.i].op == T.Integer:
            node = tokens[t.i]
            t.i += 1
            return node
        elif tokens[t.i].token == ';':
            return Terminator()
        else:
            print(locals())
            raise RuntimeError("Terminal Parsing Error")

    def __repr__(self):
        return "<Parser object>"

    def represent_codepos(self, tokens, t):
        s1 = " ".join(t.token for t in tokens)
        p = 0
        for tok in tokens[:t.i]:
            p += 1+len(tok.token)
        s2 = " "*p + "^"
        print(s1+"\n"+s2)

class Interpreter:
    def __init__(self, code):
        self.ast = Parser(code).parse()
        self.globals = {}
        self.scope = ChainMap(self.globals)

    def run(self):
        return 0

def test_string(codestring):
    interpreter = Interpreter(codestring)
    print("ast =", AstPrinter().tostring(interpreter.ast))
    print(interpreter.run())

def main():
    test_string("""return 2*3""")
    test_string( # testing multiline statements
"""let x = 10
return x""")
    test_string( # testing multiple let statements
"""let x = 10
let b = 2 * x + 3
return b * 3""")
    test_string( # testing order of ops
"""let x = 10
let b = 3 + 2 * x
return b - 2 * 3""")
    test_string( # testing functions
"""let f = fn (a, b) -> { return 2 * a + b }
return f(5, 69)""")
    test_string( # testing multiple multiplications and stuff
"""return 2 * 3 * 4 + 5 * 6 / (64 - 7*9)""")
    test_string( # testing semicolons
"""let x = 2 * 3;
return 3 - x;
""")
#     test_string( # testing multiple assignment
# """let x = 10*3
# let y = 9
# x = y = 3""")

if __name__ == '__main__':
    main()
