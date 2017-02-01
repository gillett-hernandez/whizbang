from random import randrange

def ADD(self):
    try:
        a = self.pop()
        b = self.pop()
        self.push(a+b)
        return True
    except:
        print("ADD ret false")
        return False

def DIV(self):
    try:
        a = self.pop()
        b = self.pop()
        self.push(b//a if a != 0 else 0)
        return True
    except:
        print("DIV ret false")
        return False

def DUP(self):
    try:
        n = self.pop()
        self.push(n)
        self.push(n)
        return True
    except:
        print("DUP ret false")
        return False

def EOF(self):
    return False

def GET(self):
    try:
        y = self.pop()
        x = self.pop()
        print("get call at x,y = {},{}, grid[y][x] = {} and chr(`) = '{}'".format(x, y, self.grid[y][x][-1], chr(self.grid[y][x][-1])))
        self.push(self.grid[y][x][-1])
        return True
    except:
        print(x, y, self.checkbounds(x, y))
        print("GET ret false")
        return False

def GT(self):
    try:
        a = self.pop()
        b = self.pop()
        self.push(int(b>a))
        return True
    except:
        print("GT ret false")
        return False

def HIF(self):
    try:
        v = self.pop()
        self.dmode = [1,0][v==0]
        return True
    except:
        print("HIF ret false")
        return False

def MOD(self):
    try:
        a = self.pop()
        b = self.pop()
        self.push(b % a if a != 0 else 0)
        return True
    except:
        print("MOD ret false")
        return False

def MODE(self):
    try:
        self.smode = True
        return True
    except:
        print("MODE ret false")
        return False

def MOVE(self, d):
    try:
        self.dmode = d
        return True
    except:
        print("MOVE ret false")
        return False

def MUL(self):
    try:
        a = self.pop()
        b = self.pop()
        self.push(a*b)
        return True
    except:
        print("MUL ret false")
        return False

def NOP(self):
    return True

def NOT(self):
    try:
        self.push(int(self.pop() == 0))
        return True
    except:
        print("NOT ret false")
        return False

def POPCO(self):
    try:
        c = self.pop()
        self.out += chr(c)
        return True
    except:
        print("POPCO ret false")
        return False

def POPD(self):
    try:
        self.pop()
        return True
    except:
        print("POPD ret false")
        return False

def POPIO(self):
    try:
        n = self.pop()
        self.out += str(n)
        print("just concatenated {} to self.out".format(n))
        return True
    except:
        print("POPIO ret false")
        return False

def PUSHN(self, n):
    try:
        self.push(n)
        return True
    except:
        print("PUSHN ret false")
        return False

def PUT(self):
    try:
        y = self.pop()
        x = self.pop()
        v = self.pop()
        c = chr(v)
        print("put call at x,y = {},{}, grid[y][x] = {}, v = {}, c = '{}'".format(x, y, self.grid[y][x], v, c))
        if c in tokens:
            token = tokens[c]
            token = tuple(list(token) + [v])
        else:
            token = (NOP, v)
        self.grid[y][x] = token
        print("\n".join([str("".join([chr(e[-1]) for e in line])) for line in self.grid]))
        return True
    except:
        print(x, y, v, self.checkbounds(x, y))
        print("PUT ret false")
        return False

def RMOVE(self):
    try:
        d = randrange(0,4)
        self.dmode = d
        return True
    except:
        print("RMOVE ret false")
        return False

def SKIP(self):
    try:
        # advance advances the token index pair and returns a token
        # by calling advance and not using the argument we essentially skip the cell in "front" of the current one
        self.advance()
        return True
    except:
        print("SKIP ret false")
        return False

def SUB(self):
    try:
        a = self.pop()
        b = self.pop()
        self.push(b-a)
        return True
    except:
        print("SUB ret false")
        return False

def SWAP(self):
    try:
        a = self.pop()
        if len(self.stack) == 0:
            b = 0
        else:
            b = self.pop()
        self.push(a)
        self.push(b)
        return True
    except:
        print("SWAP ret false")
        return False

def VIF(self):
    try:
        v = self.pop()
        self.dmode = [2,3][v==0]
        return True
    except:
        print("VIF ret false")
        return False

tokens = {
    "0": (PUSHN,0),
    "1": (PUSHN,1),
    "2": (PUSHN,2),
    "3": (PUSHN,3),
    "4": (PUSHN,4),
    "5": (PUSHN,5),
    "6": (PUSHN,6),
    "7": (PUSHN,7),
    "8": (PUSHN,8),
    "9": (PUSHN,9),
    "+": (ADD,),
    "-": (SUB,),
    "*": (MUL,),
    "/": (DIV,),
    "%": (MOD,),
    "!": (NOT,),
    "`": (GT,),
    ">": (MOVE, 0),
    "<": (MOVE, 1),
    "^": (MOVE, 2),
    "v": (MOVE, 3),
    "?": (RMOVE,),
    "_": (HIF,),
    "|": (VIF,),
    '"': (MODE,),
    ":": (DUP,),
    "\\": (SWAP,),
    "$": (POPD,),
    ".": (POPIO,),
    ",": (POPCO,),
    "#": (SKIP,),
    "p": (PUT,),
    "g": (GET,),
    "@": (EOF,),
    " ": (NOP,)
}

itokens = {
    "PUSHN0" : "0",
    "PUSHN1" : "1",
    "PUSHN2" : "2",
    "PUSHN3" : "3",
    "PUSHN4" : "4",
    "PUSHN5" : "5",
    "PUSHN6" : "6",
    "PUSHN7" : "7",
    "PUSHN8" : "8",
    "PUSHN9" : "9",
    "ADD" : "+",
    "SUB" : "-",
    "MUL" : "*",
    "DIV" : "/",
    "MOD" : "%",
    "NOT" : "!",
    "GT" : "`",
    "MOVE0" : ">",
    "MOVE1" : "<",
    "MOVE2" : "^",
    "MOVE3" : "v",
    "MOVE?" : "?",
    "HIF" : "_",
    "VIF" : "|",
    "MODE" : '"',
    "DUP" : ":",
    "SWAP" : "\\",
    "POPD" : "$",
    "POPIO" : ".",
    "POPCO" : ",",
    "SKIP" : "#",
    "PUT" : "p",
    "GET" : "g",
    "EOF" : "@",
    "NOP" : " "
}

modes = {
    0: "right",
    1: "left",
    2: "up",
    3: "down",
    4: ("normal", "string")
}

class Interpreter(object):
    def __init__(self, code, debug = False):
        self.stack = []
        self.grid = []
        self.debug = True
        self.runTokenizer(code)
        self.smode = False
        self.dmode = 0
        self.x = 0
        self.y = 0
        self.out = ""

    def runTokenizer(self, code):
        # 0000
        # 8421
        self.grid.append([])
        for c in code:
            if c == "\n":
                self.grid.append([])
                continue
            if c in tokens:
                token = tuple(list(tokens[c]) + [ord(c)])
            else:
                token = (NOP, ord(c))
            self.grid[-1].append(token)
            assert callable(token[0]), (token, tokens)

    def run(self):
        debug = self.debug
        rval = True
        token = self.grid[self.y][self.x]
        while rval:
            if self.smode:
                char = token[-1]
                assert isinstance(char, int)
                if debug: print("in smode v={} and chr(v) = {}".format(char, chr(char)))
                if chr(char) == '"':
                    self.smode = False
                else:
                    self.push(char)
            else:
                print("in cmode")
                cmd = token[0]
                char = token[-1]
                if len(token) > 2:
                    args = token[1:-1]
                else:
                    args = []
                rval = cmd(self,*args)
                if char == ord('"'):
                    assert self.smode
            if debug:
                if (token[0].__name__ == "NOP"):
                    print("NOP")
                else:
                    print(chr(char), modes[self.dmode], token[0].__name__, token[1:])
                    print(self.stack)
            if rval is not False:
                token = self.advance()
        if token[0].__name__ != "EOF":
            print(token[0].__name__)
            print("aborted due to error")

    def advance(self):
        if self.dmode == 0:
            # going right
            self.x += 1
        elif self.dmode == 1:
            self.x -= 1
        elif self.dmode == 2:
            self.y -= 1
        elif self.dmode == 3:
            self.y += 1
        else:
            raise RuntimeError("DirectionError")
        self.x, self.y = self.checkbounds(self.x, self.y)
        return self.grid[self.y][self.x]

    def checkbounds(self, x, y):
        Y = len(self.grid)
        X = len(self.grid[y])
        # this will handle "overflows" and negatives beautifully
        return x % X, y % Y

    def push(self, v):
        self.stack.append(v)

    def pop(self):
        return self.stack.pop()

def interpret(code):
    interpreter = Interpreter(code)
    interpreter.run()
    return interpreter.out

def main():
    # >987v>.v
    # v456<  :
    # >321 ^ _@
    # print out 123456789
    # print(interpret('>987v>.v\nv456<  :\n>321 ^ _@'))
    # >25*"!dlroW olleH":v
    #                 v:,_@
    #                 >  ^
    # print out hello world and newline
    # print(interpret('>25*"!dlroW olleH":v\n                v:,_@\n                >  ^'))
    # 08>:1-:v v *_$.@
    #   ^    _$>\:^
    # calculate 8!?
    # [0 8 7 6 5 4 3 2 1 0]
    # print(interpret('08>:1-:v v *_$.@ \n  ^    _$>\:^'))
    # 2>:3g" "-!v\  g30          <
    #  |!`"&":+1_:.:03p>03g+:"&"`|
    #  @               ^  p3\" ":<
    # 2 2345678901234567890123456789012345678

    print(interpret('2>:3g" "-!v\  g30          <\n |!`"&":+1_:.:03p>03g+:"&"`|\n @               ^  p3\\" ":<\n2 2345678901234567890123456789012345678'))
    print("23571113171923293137")

if __name__ == "__main__":
    main()
