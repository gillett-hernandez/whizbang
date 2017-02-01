NONE = 0
INCP = 1
DECP = 2
INCN = 3
DECN = 4
OUT  = 5
IN   = 6
JZ   = 7
JNZ  = 8

global debug
debug = False
# debug = True

ntokens = [
    "NONE",
    "INCP",
    "DECP",
    "INCN",
    "DECN",
    "OUT",
    "IN",
    "JZ",
    "JNZ"
]

tokens = {
    '>': INCP,
    '<': DECP,
    '+': INCN,
    '-': DECN,
    '.': OUT,
    ',': IN,
    '[': JZ,
    ']': JNZ
}

ctokens = " ><+-.,[]"
class Token:
    def __init__(self, v):
        self.v = v
    def __repr__(self):
        return ntokens[self.v]
    def __str__(self):
        return ctokens[self.v]
    def __eq__(self, v):
        return self.v == v
    def __ne__(self, v):
        return self.v != v

class Interpreter:
    def __init__(self, code, input):
        # if debug: print("initializing interpreter with ", code, " and ", input)
        self.code = code
        self.tokenizer()
        self.input = input
        self.data = []
        self.out = bytearray()
        if debug: print("end initialization")

    def tokenizer(self):
        tokenl = []
        for c in self.code:
            if debug: print("parsing token ", c)
            if c in tokens:
                tokenl.append(Token(tokens[c]))
            else:
                raise "Invalid syntax"
        self.tokens = tokenl

    # for error codes
    def run(self):
        di = 0 # data index
        ti = 0 # token index
        ii = 0 # input index
        token = self.tokens[ti]
        while True:
            if debug: print("start of run loop", locals())
            # if debug: print(self.__dict__)
            if token == INCP:
                di += 1
                if di == len(self.data):
                    self.data.append(0)
            elif token == DECP:
                di -= 1
                if (di == -1):
                    self.data.insert(0, 0)
                    di += 1
            elif token == INCN:
                self.ensureSpace(di)
                if self.data[di] == 255:
                    self.data[di] = 0
                else:
                    self.data[di] += 1
            elif token == DECN:
                self.ensureSpace(di)
                if self.data[di] == 0:
                    self.data[di] = 255
                else:
                    self.data[di] -= 1
            elif token == OUT:
                self.ensureSpace(di)
                try:
                    pass
#                     if debug: print("data out = {}".format(chr(self.data[di])))
                except UnicodeEncodeError:
                    if debug: print("unicode error")
                self.out.append(self.data[di])
            elif token == IN:
                if debug: print("start of IN")
                self.ensureSpace(di)
                if debug: print("id1")
                try:
                    pass
#                     if debug: print("consuming input at idx ", ii, " which is ", chr(self.input[ii]))
                except UnicodeEncodeError:
                    if debug: print("unicode error")
                if debug: print("di is ", di, " and ti is ", ti)
                # if debug: print("value of self.input[ii] is ", int(self.input[ii]))
                self.data[di] = ord(self.input[ii])
                if debug: print("put input char in data array")
                ii += 1
                if debug: print("incremented input pointer")
            elif token == JZ:
                if (self.data[di] == 0):
                    # by passing ti we give enough information to get the matching bracket
                    ti = self.jumpforward(ti)
                    if (ti < 0):
                        if debug: print("di = ", di, " and ii = ", ii, " and ti = ", ti)
                        raise RuntimeError("Generic jump error")
            elif token == JNZ:
                if (self.data[di] != 0):
                    # by passing ti we give enough information to get the matching bracket
                    ti = self.jumpback(ti)
                    if (ti < 0):
                        if debug: print("di = ", di, " and ii = ", ii, " and ti = ", ti)
                        raise RuntimeError("Generic jump error")
            elif token == NONE:
                return 0
            else:
                if debug: print("syntax error? ", self.tokens[ti])
                raise SyntaxError("BrainF syntax error")
            token, ti = self.consume(ti)
            if debug: print("end of run loop\n")

    def consume(self, i):
        # returns token at that next index
        i += 1 # increment token count and return token at new count
        if (i == len(self.tokens)):
            return NONE, i
        if debug: print("consuming token at ", i, " which is ", repr(self.tokens[i]))
        return self.tokens[i], i

    def jumpforward(self, i):
        if debug: print("jumping forward")
        begin = i+1
        # i is the current position in the token list
        # self function only gets called when actually jumping forward
        if (self.tokens[i] != JZ):
            if debug: print("self error should never happen as jumpforward is only called when tokens[i] = JZ")
            if debug: print("i = ", i, " and was ", i+1)
            raise RuntimeError("incorrect jump error") # indicate error

        # bracket matching done through iteration
        # start with a 1, and move the index forward
        # iterate till ct == 0
        ct = 1
        i += 1

        t = self.tokens[i]
        while i < len(self.tokens) and ct > 0:
            if t == JZ:
                ct += 1 # additional JZ adds 1
            elif t == JNZ:
                ct -= 1 # matching JNZ subs 1
            if ct == 0:
                break
            i += 1
            t = self.tokens[i]

#         i -= 1 # move back so that tokens[i] matches JNZ
        if ct != 0 or self.tokens[i] != JNZ:
            if debug: print("ct = {} and tokens near i are = [{}] and i = {}".format(ct, self.tokens[i-1:i+2],i))
            if debug: print("erronious code seems to be ", self.code[begin-1, 1+i])
            raise RuntimeError("jump forward mismatch error") # indicate error

        #postcondition asserted, ct == 0 and tokens[i] == JNZ
        return i

    def jumpback(self, i):
        if debug: print("jumping backward")
        # i is the current position in the token list
        # self function only gets called when actually jumping forward
        if debug: print("i = {} and token = {}".format(i, repr(self.tokens[i])))
        if self.tokens[i] != JNZ:
            if debug: print(self.tokens[i], JNZ)
            raise RuntimeError("incorrect jump error") # indicate error

        # bracket matching done through iteration
        # start with a 1, and move the index forward
        # iterate till ct == 0
        ct = 1
        i -= 1

        t = self.tokens[i]
        while i >= 0 and ct != 0:
            if t == JZ:
                ct -= 1
            elif t == JNZ:
                ct += 1
            if ct == 0:
                break
            i -= 1
            t = self.tokens[i]


        if debug: print("i = {} ct = {} and token = {}".format(i, ct, repr(self.tokens[i])))
        if debug: print(self.tokens[i-1:i+2])
        if ct != 0 or self.tokens[i] != JZ:
            if debug: print("ct = {} and tokens near i are = [{}] and i = {}".format(ct, self.tokens[i-1:i+2],i))
            if debug: print("erronious code seems to be ", self.code[begin-1, 1+i])
            raise RuntimeError("jump back mismatch error") # indicate error

        #postcondition asserted, ct == 0 and self.tokens[i] == JZ

        if debug: print("i = ", i)
        return i

    def ensureSpace(self, di):
        if (len(self.data) <= di):
            self.data.extend([0]*(di+1 - len(self.data)))


def brainCluck(code, input):
    interpreter = Interpreter(code, input)
    error = interpreter.run()
    if error != 0:
        return "error happened"

    if debug: print("interpreter output")
    if debug: print(interpreter.out)
    return interpreter.out.decode()

def main():
    import sys
    if (len(sys.argv) == 1):
        print("going in to testing mode")
        print("to aid in command line execution, if \\xXX appears in the input string it will be interpreted as a char in the 0-255 range")
        # chararray = bytearray()
        # chararray.append(0)
        # chararray[0] = 99
        # print(chararray[0])

        #echo until "255"
        tw = "codewars"
        tw += chr(255)
        res = brainCluck(",+[-.,+]", tw)
        assert res == "codewars", res

        #echo until "0"
        mw = "codewars"
        mw += chr(0)
        res = brainCluck(",[.[-],]",mw)
        assert res == "codewars", res

        dw = "\x07\x03"
        result = "\x15"
        actual1 = brainCluck(",>,<[>[->+>+<<]>>[-<<+>>]<<<-]>>.",dw)
        print(actual1[0])

        actual2 = brainCluck("++++++++++[>+++++++>++++++++++>+++>+<<<<-]>++.>+.+++++++..+++.>++.<<+++++++++++++++.>.+++.------.--------.>+.", "")
        print(actual2)
    else:
        argv = sys.argv
        argc = len(sys.argv)
        code = str(argv[1])
        input = b""
        if (argc > 2):
            input = bytes(argv[2], "utf-8")

            input.replace("\\\\", "\\")

        interpreter = Interpreter(code, input)
        error = interpreter.run()
        if (error != 0):
            print("error happened")
            return -1

        if debug: print("interpreter output")
        print(interpreter.out)
        return 0


if __name__ == '__main__':
    main()
