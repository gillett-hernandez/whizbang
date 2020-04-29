# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'

# %%


class Node:
    @classmethod
    def register_global(cls, list):
        cls.registry = list

    def __init__(self):
        self.registry.append(self)
        self.id = len(self.registry) - 1
        # inputs is a list of tuples of indices into the global registry and output ids (i.e. input id 0 links to node X's output 2).
        # should be initialized to Nones, indicating no connection
        self.inputs = []
        self.defaults = []
        # outputs is a list that contains the actual output data. initialized to Nones. will only populate with data when the node is visited by a Interpreter.
        self.outputs = []
        self.visited = False

    def connect_input(self, input_id, input_tuple):
        # input is of type Tuple[int, int]
        # where the first member is the node id and the second member is the output id (0 indexed)
        self.inputs[input_id] = input_tuple

    def visit(self, visitor):

        if isinstance(visitor, Compiler):
            print(f"{self} being visited by compiler")
            # each of the entries in inputs is a list of instructions that will assemble that respective input
            if self.visited:
                print(f"{self} already visited, so just assigning load instruction")
                self.outputs = [
                    [(ops.LOAD, f"{self.id}.{i}")] for i in range(len(self.outputs))
                ]
                return
            inputs = []
            for input_idx, tup in enumerate(self.inputs):
                if tup is None:
                    # broken connection, abort or use default value.
                    raise RuntimeError("broken connection. default not found")
                    # if self.defaults[input_idx] is None:
                    #     raise RuntimeError("broken connection. default not found")
                    # else:
                    #     inputs.append(self.defaults[input_idx])
                else:
                    node_id, output_id = tup
                    assert node_id is not None and output_id is not None, locals()
                    self.registry[node_id].visit(visitor)
                    output = self.registry[node_id].outputs[output_id]
                    assert output is not None, locals()
                    inputs.append(output)
            # now inputs contains all the data necessary for this node to execute
            self.execute(visitor, inputs)
            # then we want to save all the outputs as new variables
            for i, output in enumerate(self.outputs):
                if output is not None:
                    output.extend([(ops.STORE, f"{self.id}.{i}")])
                    self.outputs[i] = output
        elif isinstance(visitor, Interpreter):
            if self.visited:
                return
            inputs = []
            for input_idx, tup in enumerate(self.inputs):
                if tup is None:
                    # broken connection, abort or use default value.
                    if self.defaults[input_idx] is None:
                        raise RuntimeError("broken connection. default not found")
                    else:
                        inputs.append(self.defaults[input_idx])
                else:
                    node_id, output_id = tup
                    assert node_id is not None and output_id is not None, locals()
                    self.registry[node_id].visit(visitor)
                    output = self.registry[node_id].outputs[output_id]
                    assert output is not None, locals()
                    inputs.append(output)
            # now inputs contains all the data necessary for this node to execute
            self.execute(visitor, inputs)
        elif isinstance(visitor, Resetter):
            # reset outputs
            for input_idx, tup in enumerate(self.inputs):
                if tup is None:
                    # broken connection, abort or use default value.
                    if self.defaults[input_idx] is None:
                        raise RuntimeError("broken connection. default not found")
                    else:
                        inputs.append(self.defaults[input_idx])
                else:
                    node_id, output_id = tup
                    assert node_id is not None and output_id is not None, locals()
                    self.registry[node_id].visit(visitor)
                    output = self.registry[node_id].outputs[output_id]
            self.outputs = [None for e in self.outputs]
            self.visited = False
            return
        self.visited = True
        return

    def execute(self, visitor, inputs):
        pass


# %%
def test_global_list():
    global_list = []
    Node.register_global(global_list)
    n1 = Node()
    n2 = Node()
    assert len(global_list) == 2


test_global_list()


# %%
class Interpreter:
    def execute(self, root: Node):
        root.visit(Resetter())
        root.visit(self)
        return root.outputs


# %%
class Resetter:
    pass


# %%
from enum import Enum, auto


class ops(Enum):
    CONST = auto()
    PUSH = auto()
    POP = auto()
    POP_R = auto()
    MOV = auto()
    MOV_T = auto()
    ADD = auto()
    PRINT = auto()
    STORE = auto()
    LOAD = auto()

    def __repr__(self):
        return str(self)


# %%
class Compiler:
    AVAILABLE_REGISTERS = 4
    debug = True

    def compile(self, root: Node):
        root.visit(Resetter())
        root.visit(self)
        return root

    def compile_and_execute(self, root: Node):
        root = self.compile(root)
        instructions = root.outputs[0]
        instructions = self.assign_and_clean_registers(instructions)
        instructions = self.optimize(instructions)
        self.execute(instructions)

    def assign_and_clean_registers(self, instructions):
        # iterate over instructions and
        # 1. find and fix up subsections where a load occurs right after a store with a var that is only used once
        # 2. count and analyze all the variables needed to determine if usages can fit in all registers.
        needed_variables = []
        for instruction in instructions:
            if instruction[0] == ops.LOAD:
                needed_variables.append(instruction[1])
        i = 0
        while i < len(instructions):
            instruction = instructions[i]
            if instruction[0] == ops.STORE and instruction[1] not in needed_variables:
                del instructions[i]
                continue  # next iteration
            i += 1
        if self.debug:
            print(needed_variables)
        return instructions

    def optimize(self, instructions):
        # mut instructions
        # optimize root node
        mutators = []

        def mutator(asm):
            i = 0
            while i + 1 < len(asm):
                if (asm[i], asm[i + 1]) in [("PO", "PU"), ("PU", "PO")]:
                    del asm[i : i + 2]
                i += 1
            return asm

        mutators.append(mutator)
        last_hash = None
        while last_hash != hash(tuple(instructions)):
            last_hash = hash(tuple(instructions))
            for mutator in mutators:
                instructions = mutator(instructions)

        return instructions

    def execute(self, instructions):
        # instructions is a list of `ops`

        if self.debug:
            print(instructions)
        reg = [None for i in range(self.AVAILABLE_REGISTERS)]
        variables = {}
        tmp = None
        stack = []
        for instruction in instructions:
            if instruction[0] == ops.CONST:
                tmp = instruction[1]
            elif instruction[0] == ops.PUSH:
                stack.append(tmp)
            elif instruction[0] == ops.POP:
                tmp = stack.pop()
            elif instruction[0] == ops.POP_R:
                idx = instruction[1]
                reg[idx] = stack.pop()
            elif instruction[0] == ops.MOV:
                idx = instruction[1]
                reg[idx] = tmp
            elif instruction[0] == ops.MOV_T:
                idx = instruction[1]
                tmp = reg[idx]
            elif instruction[0] == ops.STORE:
                variables[instruction[1]] = tmp
            elif instruction[0] == ops.LOAD:
                tmp = variables[instruction[1]]
            elif instruction[0] == ops.ADD:
                tmp += reg[0]
            elif instruction[0] == ops.PRINT:
                print(tmp)
        print("============================")
        print(
            f"stack is {stack}, tmp is {tmp}, variables is {variables}, registers is {reg}"
        )


# %% [markdown]
# ## Instructions
# while in Compilation mode (i.e. when being visited by a Compiler), if an instruction has an output it should leave its output in the `tmp` register, and not push unless necessary.

# %%
class Const(Node):
    # in interpreter mode, sets the output value to a constant
    # in compiler mode, pushes a constant value onto the stack
    def __init__(self, value):
        super().__init__()
        # inputs is a list of tuples of indices into the global registry and output ids (i.e. input id 0 links to node X's output 2).
        # should be initialized to Nones, indicating no connection
        self.inputs = []
        self.defaults = []
        # outputs is a list that contains the actual output data. initialized to Nones. will only populate with data when the node is visited by a Interpreter.
        self.value = value
        self.outputs = [None]

    def execute(self, visitor, inputs):
        if isinstance(visitor, Interpreter):
            self.outputs[0] = self.value
        elif isinstance(visitor, Compiler):
            self.outputs[0] = [(ops.CONST, self.value)]


# %%
class Add(Node):
    def __init__(self):
        super().__init__()
        # inputs is a list of tuples of indices into the global registry and output ids (i.e. input id 0 links to node X's output 2).
        # should be initialized to Nones, indicating no connection
        self.inputs = [None, None]
        self.defaults = [None, None]
        # outputs is a list that contains the actual output data. initialized to Nones. will only populate with data when the node is visited by a Interpreter.
        self.outputs = [None]

    def execute(self, visitor, inputs):
        if isinstance(visitor, Interpreter):
            self.outputs[0] = inputs[0] + inputs[1]
        elif isinstance(visitor, Compiler):
            assert isinstance(inputs[0], list) and isinstance(inputs[1], list), inputs
            instructions = []
            instructions.extend(inputs[0])
            # the following PUSH instructions might be unnecessary
            instructions.append((ops.PUSH,))
            instructions.extend(inputs[1])
            instructions.append((ops.POP_R, 0))
            instructions.append((ops.ADD,))
            self.outputs[0] = instructions


# %%
class Print(Node):
    # takes a input and prints it
    def __init__(self):
        super().__init__()
        self.inputs = [None]
        self.defaults = [None]
        self.outputs = [None]

    def execute(self, visitor, inputs):
        if isinstance(visitor, Interpreter):
            print(inputs[0])
            self.outputs[0] = inputs[0]
        elif isinstance(visitor, Compiler):
            instructions = []
            instructions.extend(inputs[0])
            instructions.append((ops.PRINT,))
            self.outputs[0] = instructions


# %%
def construct_root():
    nodes = []
    Node.register_global(nodes)

    idx1 = Const(1.0).id
    idx2 = Const(1.0).id
    node = Add()
    node.connect_input(0, (idx1, 0))
    node.connect_input(1, (idx2, 0))

    idx1 = Const(1.0).id
    idx2 = node.id
    node = Add()
    node.connect_input(0, (idx1, 0))
    node.connect_input(1, (idx2, 0))

    idx1 = node.id
    idx2 = node.id
    node = Add()
    node.connect_input(0, (idx1, 0))
    node.connect_input(1, (idx2, 0))

    idx1 = node.id
    node = Print()
    node.connect_input(0, (idx1, 0))

    return node


# %%
def test_compiler(root):

    compiler = Compiler()
    print(root.registry)
    root = compiler.compile(root)
    compiler.execute(root.outputs[0])


def test_compiler_opt(root):

    compiler = Compiler()
    print(root.registry)
    outputs = compiler.compile_and_execute(root)


# %%


def test_interpreter(root):
    executor = Interpreter()
    print(root.registry)
    executor.execute(root)


# %%

node = construct_root()
test_interpreter(node)


# %%

node = construct_root()
test_compiler(node)


# %%

node = construct_root()
test_compiler_opt(node)


# %%
