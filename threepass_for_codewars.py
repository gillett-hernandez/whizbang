#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File Name: threepass_for_codewars.py
# @Author: Copyright (c) 2017-01-28 01:03:16 gilletthernandez
# @Date:   2017-01-28 01:03:16
# @Last Modified by:   Gillett Hernandez
# @Last Modified time: 2017-01-31 18:23:08

import re

global debug
debug = False

OP = "OP"
CP = "CP"
IMM = "imm"
ARG = "arg"
OPR = "op"

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

    def __repr__(self):
        if hasattr(self, 'n'):
            string2 = ", 'n': {}".format(self.n)
        elif hasattr(self, 'a') and hasattr(self, 'b'):
            string2 = ", 'a': {0!r}, 'b': {1!r}".format(self.a, self.b)
        else:
            string2 = ""
        # print("op = ",self.op)
        # print("string2 = ", string2)
        rstring = "'op': '{0}'{1}".format(self.op, string2)
        rstring = "{" + rstring + "}"
        return rstring

    def __str__(self):
        return str(self.token)

    def todict(self):
        base = {"op":self.op}
        if hasattr(self, "n"):
            base["n"] = self.n
        else:
            base["a"] = self.a.todict()
            base["b"] = self.b.todict()
        return base

    @staticmethod
    def fromdict(dict):
        if "n" in dict:
            if dict["op"] == ARG:
                node = Arg(dict["n"])
            else:
                node = Const(dict["n"])
        else:
            node = Op(dict["op"], Node.fromdict(dict["a"]), Node.fromdict(dict["b"]))
        return node

class Const(Node):
    __slots__ = ['n']
    def __init__(self, n):
        super(Const, self).__init__(IMM)
        self.n = n

class Arg(Node):
    __slots__ = ['n']
    def __init__(self, n):
        super(Arg, self).__init__(ARG)
        self.n = n

class Op(Node):
    __slots__ = ['a', 'b']
    def __init__(self, optype, a, b):
        super(Op, self).__init__(optype)
        self.a = a
        self.b = b

class Compiler(object):
    def compile(self, code):
        return self.pass3(self.pass2(self._pass1(code)))

    def tokenizer(self, code):
        """Turn a code string into an array of tokens.  Each token
           is either '[', ']', '(', ')', '+', '-', '*', '/', a variable
           name or a number (as a string)"""
        token_iter = (m.group(0) for m in re.finditer(r'[-+*/()[\]]|[A-Za-z]+|\d+', code))
        tokens = []
        parens = []
        self.ptable = {}
        for i, token in enumerate([int(tok) if tok.isdigit() else tok for tok in token_iter]):
            if isinstance(token, int):
                node = Const(token)
            elif token.isalpha():
                node = Arg(token)
            elif token in "+-*/":
                optype = OPR
                node = Op(token, None, None)
            elif token == "(":
                node = Node(OP)
                parens.append(i)
            elif token == ")":
                node = Node(CP)
                self.ptable[parens.pop()] = i
            else:
                node = Node(None)
            node.token = str(token)
            node.ti = i
            tokens.append(node)
        if debug: print(self.ptable)
        if debug: print(parens)
        self.rptable = {b:a for a,b in self.ptable.items()}
        return tokens

    def pass1(self, code):
        """Returns an un-optimized AST"""
        if debug: print("tokenizer starting")
        tokens = self.tokenizer(code)
        if debug: print("tokenizer done, arglist parsing")
        self.args = self.parse_arglist(tokens)
        if debug: print("arglist done, ast parsing")
        ast = self.parse_expression(tokens)
        if debug: print("ast parsing done")
        return ast.todict()

    def parse_arglist(self, tokens):
        if debug: print("parse arglist", [str(t) for t in tokens])
        ii = 1
        args = []
        tokens[0].token == '['
        while tokens[ii].token != ']':
            args.append(tokens[ii].token)
            ii += 1
        #           ii+1 to include ']' in deletion
        del tokens[:ii+1]
        return args

    def parse_expression(self, tokens):
        # expression ::= term
        #              | expression '+' term
        #              | expression '-' term
        if debug: print("parse expression tokens ", tokens)
        ii = len(tokens)-1
        token = tokens[ii]
        while token.token not in '+-':
            if debug: print("searching for + or -", ii)
            if token.token == ')':
                start = self.rptable[token.ti]
                if token.ti != ii:
                    if debug: print("if branch, token.ti = {}, ii = {}, start = {}".format(token.ti, ii, start))
                    ii -= token.ti - start
                    if debug: print("after, ii = {}".format(ii))
                    if debug: print([str(t) for t in tokens])
                else:
                    if debug: print("else branch, token.ti = {}, ii = {}, start = {}".format(token.ti, ii, start))
                    ii = start
                    if debug: print([str(t) for t in tokens])
            # if it was a parenth, now at start so skip backward past '('
            # else, normally 'advance'
            ii -= 1
            if ii < 0:
                break
            try:
                token = tokens[ii]
            except:
                if debug: print(locals())
                raise
        else:
            assert tokens[ii].token in '+-'
            node = tokens[ii]
            node.a = self.parse_expression(tokens[:ii])
            node.b = self.parse_term(tokens[ii+1:])
            if debug: print("expression a b path", locals())
            return node
        assert ii <= 0, locals()
        if debug: print("subparse into term path", locals())
        # no +- on within tokens that are outside of parens
        node = self.parse_term(tokens)
        return node


    def parse_term(self, tokens):
        # term       ::= factor
        #              | term '*' factor
        #              | term '/' factor
        if debug: print("parse term tokens ", tokens)
        ii = len(tokens) - 1
        token = tokens[ii]
        while token.token not in '*/':
            if debug: print("searching for * or /", ii)
            if token.token == ')':
                start = self.rptable[token.ti]
                # subtraction to offset the offset induced by a slice
                if token.ti != ii:
                    ii -= token.ti - start
                else:
                    ii = start
            # if it was a parenth, now at end so skip past ')'
            # else, normally advance
            ii -= 1
            if ii < 0:
                break
            token = tokens[ii]
        else:
            assert tokens[ii].token in '*/'
            node = tokens[ii]
            node.a = self.parse_term(tokens[:ii])
            node.b = self.parse_factor(tokens[ii+1:])
            if debug: print("term a b path", locals())
            return node
        assert ii < 0, locals()
        # no +- on within tokens that are outside of parens
        if debug: print("subparse into factor path", locals())
        node = self.parse_factor(tokens)
        return node

    def parse_factor(self, tokens):
        # factor     ::= number
        #              | variable
        #              | '(' expression ')'
        if debug: print("parse factor", tokens)
        if tokens[0].op == OP:
            end = self.ptable[tokens[0].ti]
            # end is offsetted because of previous token consumption
            end -= tokens[0].ti
            assert tokens[end].op == CP, locals()
            del tokens[0]
            node = self.parse_expression(tokens[0:end-1])
            # because of token[0] deletion, this next call includes the ending ']' token
            del tokens[:end]
            return node
        elif tokens[0].op in [IMM, ARG]:
            if tokens[0].op == ARG:
                # tee hee.
                # ast manipulation, converting 'n': 'a' to 'n': 0
                tokens[0].n = self.args.index(tokens[0].token)
                return tokens[0]
            else:
                return tokens[0]
        else:
            raise RuntimeError("parse error in parse factor")

    def _pass2(self, ast):
        """Returns an AST with constant expressions reduced"""
        # ast is root node of AST and any operators with only constants on both sides need to be reduced
        # CTFE/CTE
        # Compile Time Evaluation
        if debug: print("subcall")
        if ast.op not in [IMM, ARG]:
            # subcalls in case of nested constants
            ast.a = self._pass2(ast.a)
            ast.b = self._pass2(ast.b)
            # transformations in case they were resolved
            ast.a = self.transformer(ast.a)
            ast.b = self.transformer(ast.b)
            # additional transformation in case self was resolved
            ast = self.transformer(ast)
        return ast

    def pass2(self, ast):
        if not isinstance(ast, Node):
            ast = Node.fromdict(ast)
        return self._pass2(ast).todict()

    @staticmethod
    def transformer(node):
        if hasattr(node, 'a') and hasattr(node, 'b'):
            if node.a.op == IMM and node.b.op == IMM:
                node = Const(eval("{}{}{}".format(node.a.n, node.op, node.b.n)))
        return node

    def pass3(self, ast):
        if not isinstance(ast, Node):
            ast = Node.fromdict(ast)
        """Returns assembly instructions"""
        instructions = []
        # entire call either loads and pushes on to stack
        # or subcalls, pops, swaps, pops, ops, then pushes on to stack
        if ast.op in [IMM, ARG]:
            # load number into r0
            instructions.append(opcodes[ast.op] + str(ast.n))
            # push on to stack
            instructions.append("PU")
        elif ast.op in "+-*/":
            #subcall and push result on to stack
            instructions.extend(self.pass3(ast.a))
            #subcall and push result on to stack
            instructions.extend(self.pass3(ast.b))
            # pop both off stack
            instructions.append("PO")
            instructions.append("SW")
            instructions.append("PO")
            # compute
            instructions.append(opcodes[ast.op])
            # push
            instructions.append("PU")
        return instructions


def simulate(asm, argv):
    r0, r1 = None, None
    stack = []
    for ins in asm:
        if debug: print(ins)
        if ins[:2] == 'IM' or ins[:2] == 'AR':
            ins, n = ins[:2], int(ins[2:])
        if ins == 'IM':   r0 = n
        elif ins == 'AR': r0 = argv[n]
        elif ins == 'SW': r0, r1 = r1, r0
        elif ins == 'PU': stack.append(r0)
        elif ins == 'PO': r0 = stack.pop()
        elif ins == 'AD': r0 += r1
        elif ins == 'SU': r0 -= r1
        elif ins == 'MU': r0 *= r1
        elif ins == 'DI': r0 /= r1
    return r0


def main():
    testcode1 = "[ a b ] a * a + b * b"
    # testcode2 = "[ a b ] (a + b) / 2"
    # testcode3 = "[ a b c d ] (a-b)*(c-d)/(2-a)"
    # testcode4 = "[ a b c d ] a*b*c/d"
    # asm = Compiler().compile(testcode1)
    # print(repr(ast.a))
    asm = Compiler().compile(testcode1)
    if debug: print(asm)
    # ast = Compiler().compile(testcode3)
    # print(repr(ast))
    # ast = Compiler().compile(testcode4)
    # print(repr(ast))
    # testcode5 = "[ a b c d ] a/b*c/d"
    # ast = Compiler().compile(testcode5)
    # print(repr(ast))
    # testcode6 = "[ a ] a / (2 * 5)"
    # ast = Compiler().compile(testcode6)
    # print(repr(ast))
    print(simulate(asm, [5, 7]))
    print(simulate(asm, [3, 4]))

if __name__ == '__main__':
    main()
