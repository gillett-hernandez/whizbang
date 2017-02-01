#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @File Name: threepass.py
# @Author: Copyright (c) 2017-01-28 01:03:16 gilletthernandez
# @Date:   2017-01-28 01:03:16
# @Last Modified by:   gilletthernandez
# @Last Modified time: 2017-01-31 17:31:59

# language syntax:
#
#
# function   ::= '[' arg-list ']' expression
#
# arg-list   ::= /* nothing */
#              | arg-list variable
#
# expression ::= term
#              | expression '+' term
#              | expression '-' term
#
# term       ::= factor
#              | term '*' factor
#              | term '/' factor
#
# factor     ::= number
#              | variable
#              | '(' expression ')'
# variable   ::= [a-zA-Z]+
# number     ::= [0-9]+

# numbers and variables are marked by the tokenize function

# asm opcodes:
# IM
# AR
# SW
# PU
# PO
# AD
# SU
# MU
# DI

# example
# [ a b ] a*a + b*b

# {
#     'op':'+',
#     'a': {
#         'op':'*',
#         'a': {
#             'op':'arg',
#             'n': 'a'
#         },
#         'b': {
#             'op':'arg',
#             'n': 'a'
#         }
#     },
#     'b': {
#         'op':'*',
#         'a': {
#             'op':'arg',
#             'n': 'b'
#         },
#         'b': {
#             'op':'arg',
#             'n': 'b'
#         }
#     }
# }

# AR 0
# SW
# AR 1
# MU
#
# PU
#
# AR 0
# SW
# AR 1
# MU
#
# SW
# PO
# AD

import re

OP = "OP"
CP = "CP"
IMM = "imm"
ARG = "arg"
OPR = "op"

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
        rstring = "'op': {0}{1}".format(self.op, string2)
        rstring = "{" + rstring + "}"
        return rstring

    def __str__(self):
        return str(self.token)

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
        return self.pass3(self.pass2(self.pass1(code)))

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
        print(self.ptable)
        print(parens)
        self.rptable = {b:a for a,b in self.ptable.items()}
        return tokens

    def pass1(self, code):
        """Returns an un-optimized AST"""
        print("tokenizer starting")
        tokens = self.tokenizer(code)
        print("tokenizer done, arglist parsing")
        self.args = self.parse_arglist(tokens)
        print("arglist done, ast parsing")
        ast = self.parse_expression(tokens)
        print("ast parsing done")
        return ast

    def parse_arglist(self, tokens):
        print("parse arglist", [str(t) for t in tokens])
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
        print("parse expression tokens ", tokens)
        ii = len(tokens)-1
        token = tokens[ii]
        while token.token not in '+-':
            print("searching for + or -", ii)
            if token.token == ')':
                start = self.rptable[token.ti]
                if token.ti != ii:
                    print("if branch, token.ti = {}, ii = {}, start = {}".format(token.ti, ii, start))
                    ii -= token.ti - start
                    print("after, ii = {}".format(ii))
                    print([str(t) for t in tokens])
                else:
                    print("else branch, token.ti = {}, ii = {}, start = {}".format(token.ti, ii, start))
                    ii = start
                    print([str(t) for t in tokens])
            # if it was a parenth, now at start so skip backward past '('
            # else, normally 'advance'
            ii -= 1
            if ii < 0:
                break
            try:
                token = tokens[ii]
            except:
                print(locals())
                raise
        else:
            assert tokens[ii].token in '+-'
            node = tokens[ii]
            node.a = self.parse_expression(tokens[:ii])
            node.b = self.parse_term(tokens[ii+1:])
            print("expression a b path", locals())
            return node
        assert ii <= 0, locals()
        print("subparse into term path", locals())
        # no +- on within tokens that are outside of parens
        node = self.parse_term(tokens)
        return node


    def parse_term(self, tokens):
        # term       ::= factor
        #              | term '*' factor
        #              | term '/' factor
        print("parse term tokens ", tokens)
        ii = len(tokens) - 1
        token = tokens[ii]
        while token.token not in '*/':
            print("searching for * or /", ii)
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
            print("term a b path", locals())
            return node
        assert ii < 0, locals()
        # no +- on within tokens that are outside of parens
        print("subparse into factor path", locals())
        node = self.parse_factor(tokens)
        return node

    def parse_factor(self, tokens):
        # factor     ::= number
        #              | variable
        #              | '(' expression ')'
        print("parse factor", tokens)
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
            return tokens[0]
        else:
            raise RuntimeError("parse error in parse factor")

    def pass2(self, ast):
        """Returns an AST with constant expressions reduced"""
        return ast

    def pass3(self, ast):
        """Returns assembly instructions"""
        return ast

def simulate(asm, argv):
    r0, r1 = None, None
    stack = []
    for ins in asm:
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
    # testcode1 = "[ a b ] a * a + b * b"
    # ast = Compiler().compile(testcode1)
    # print("ast = ", repr(ast))
    # # print(repr(ast.a))
    # testcode2 = "[ a b ] (a + b) / 2"
    # ast = Compiler().compile(testcode2)
    # print(repr(ast))
    testcode3 = "[ a b c d ] (a-b)*(c-d)/(2-a)"
    ast = Compiler().compile(testcode3)
    print(repr(ast))
    # testcode4 = "[ a b c d ] a*b*c/d"
    # ast = Compiler().compile(testcode4)
    # print(repr(ast))
    # testcode5 = "[ a b c d ] a/b*c/d"
    # ast = Compiler().compile(testcode5)
    # print(repr(ast))

if __name__ == '__main__':
    main()
