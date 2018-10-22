"""
A trips node is defined as a list of strings with some number of positionals
followed by a sequence of key-value pairs.  A trips parse is a list of nodes.

A rule is a list of strings with the same number of positionals followed by
a sequence of key-value pairs.  Any value in a rule may be replaced by a variable.
A rule is satisfied by a trips node if all non-variable values are equal in both
lists and there are suitable assignments for variable values.

A rule set is a list of rules.  A rule set is satisfied by a trips parse if
there is a one-to-one mapping from the rules to the nodes where all variable assignments
are consistent.
"""


class TripsNode:
    def __init__(self, positionals, kvpairs):
        self.positionals = positionals
        self.kvpairs = kvpairs

    def __repr__(self):
        return "Positionals: " + str(self.positionals) + "\nKey-value pairs: " + str(self.kvpairs)


class Element:
    def match(self, other) -> bool:
        return self == other

class Variable(Element):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "Variable<%s>" % self.name

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        if type(other) is Variable:
            return self.name == other.name
        if type(other) is Term:
            return True
        return False

class Term(Element):
    #TODO: check inheritance
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Term<%s>" % self.value

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        if type(other) is Term:
            return self.value == other.value
        elif type(other) is Variable:
            return True
        return False

class Rule:
    def __init__(self, positionals, kvpairs):
            self.positionals = positionals
            self.kvpairs = kvpairs

    def _score_positionals(self, tnode : TripsNode) -> int: #TODO: missing positionals
        return sum([r.match(t) for r, t in zip(self.positionals, tnode.positionals)])

    def _score_kvpairs(self, tnode: TripsNode) -> int:
        count = 0
        for k, v in self.kvpairs.items():
            if k in tnode.kvpairs and v == tnode.kvpairs[k]:
                count += 1
        return count


    def score(self, tripsnode : TripsNode) -> int:
        # positionals
        #if len(self.positionals) != len(tripsnode.positionals): #TODO
        #    return False
        p = self._score_positionals(tripsnode)
        kv= self._score_kvpairs(tripsnode)

        return p + kv

def get_element(e):
    if e[0] == "?":
        return Variable(e)
    return Term(e)

def load_list(values, typ=TripsNode):
    positionals = []
    kvpair = {}
    tokens = values.strip().replace('(', '').replace(')', '').split()
    state = 0
    while tokens:
        t = tokens.pop()
        if not state:
            if t[0] == ":":
                state = 1
            else:
                positionals.append(get_element(t))
        if state == 1:
            if t[0] == ":":
                if not tokens:
                    raise ValueError("Not enough values")
                value = tokens.pop()
                kvpair[get_element(t)] = get_element(value)
                positionals.append(get_element(value))
    return (positionals, kvpair)