import re

matcher = re.compile(r"[+-]?\d?[a-z]+")
digitmatcher = re.compile(r"[+-]?\d?")
vmatcher = re.compile(r"[a-z]+")

def simplify(poly):
    print(poly)
    matches = list(re.findall(matcher, poly))
    print(matches)
    groupings = ["".join(sorted(e)) for e in matches]
    print(groupings)
    exprdict = {}
    for g in groupings:
        d = digitmatcher.match(g)
        print(d)
        if d is None or d.group(0) == '':
            d = "1"
        else:
            d = d.group(0)
        print("d1",d)
        if d == "+":
            d = "1"
        elif d == "-":
            d = "-1"
        print("g", g)
        print("d2", d)
        vs = vmatcher.search(g).group(0)
        print("vs1", vs)
        print("vs2", vmatcher.search(g))
        exprdict[vs] = exprdict.get(vs, 0) + int(d)
    print(exprdict)
    l = list(exprdict.items())
    l = [e for e in l if e[1] != 0]
    l.sort(key=lambda e: e[0])
    l.sort(key=lambda e: len(e[0]))
    print(l)
    s = ""
    d = l[0][1]
    v = l[0][0]
    if d == 1:
        d = ""
    if d == -1:
        d = "-"
    s += str(d) + v
    for e in l[1:]:
        print(e)
        d = e[1]
        v = e[0]
        if d == 1:
            d = '+'
        elif d > 1:
            d = '+' + str(d)
        elif d == -1:
            d = '-'
        elif d < -1:
            d = str(d)
        else:
            continue
        s += d + v
    return s

# '4a+b-ab+4ac'
# '4a+b-ab+4ac'

print(simplify('-8fk+5kv-4yk+7kf-qk+yqv-3vqy+4ky+4kf+yvqkf'),'3fk-kq+5kv-2qvy+fkqvy')

# print(simplify("dc+dcba"),  "cd+abcd")

# print(simplify("2xy-yx"), "xy")

# print(simplify("-a+5ab+3a-c-2a"), "-c+5ab")

# print(simplify("-abc+3a+2ac"), "3a+2ac-abc")

# print(simplify("xyz-xz"), "-xz+xyz")

# print(simplify("a+ca-ab"), "a-ab+ac")

# print(simplify("xzy+zby"), "byz+xyz")

# print(simplify("-y+x"), "x-y")

# print(simplify("y-x"), "-x+y")
