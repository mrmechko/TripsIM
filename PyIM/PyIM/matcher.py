import ontologytools as ont
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
import re

class TripsNode:
    def __init__(self, positionals, kvpairs):
        self.positionals = positionals
        self.kvpairs = kvpairs

    def __repr__(self):
        return "TripsNode<" + repr(self.positionals) + " " + repr(self.kvpairs) + ">"
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
    # TODO: check inheritance
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Term<%s>" % self.value

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        if type(other) is Term:
            return (ont.isAncestor(other, self) or ont.isAncestor(self, other))
        elif type(other) is Variable:
            return True
        return False


class Rule:

    def __init__(self, positionals=None, kvpairs=None, tnode=None):
        if tnode:
            self.positionals = tnode.positionals
            self.kvpairs = tnode.kvpairs
        elif positionals and kvpairs:
            self.positionals = positionals
            self.kvpairs = kvpairs
        else:
            raise NameError("Has to provide either (positional, kvpairs) or a tnode")

    def __repr__(self):
        return "TripsNode<" + repr(self.positionals) + " " + repr(self.kvpairs) + ">"

    def _score_positionals(self, tnode: TripsNode) -> int:  # TODO: missing positionals
        '''
        :param tnode:
        :return: the number of matched positionals
        '''
        j = 0
        last = 0
        sum = 0
        for i in range(len(self.positionals)):
            item = self.positionals[i]
            if item in tnode.positionals[last:]:
                j = tnode.positionals.index(item, last)
                last = j
                sum += 1
        return sum

    def _score_kvpairs(self, tnode: TripsNode) -> int:
        count = 0
        for k, v in self.kvpairs.items():
            if k in tnode.kvpairs and v == tnode.kvpairs[k]:
                count += 1
        return count

    def score(self, tripsnode: TripsNode) -> float:
        p = self._score_positionals(tripsnode)
        kv = self._score_kvpairs(tripsnode)
        return p + kv

    def match_vars(self, tnode: TripsNode, var_term):
        """
        :param tnode:
        :param var_term:
        :return: a dict of matched varaibles and terms {var: term}
        """
        ''' Match variables in positionals '''
        for r, t in zip(self.positionals, tnode.positionals):
            if isinstance(r, Variable):
                if r in var_term:
                    var_term[r].append(t)
                else:
                    var_term[r] = [t]
        ''' Match variable in kvpairs '''
        for k, v in self.kvpairs.items():
            if k in tnode.kvpairs and isinstance(v, Variable):  # TODO: if k not found in tnode.kvpair?
                if v in var_term:
                    var_term[v].append(tnode.kvpairs[k])
                else:
                    var_term[v] = [tnode.kvpairs[k]]
        return var_term

def get_element(e):
    if e[0] == "?":
        return Variable(e)
    return Term(e)


def load_list_set(lf):
    """
    :param lf: string in logical form
        e.g. ((ONT::SPEECHACT ?x ONT::SA_REQUEST :CONTENT ?!theme)(ONT::F ?!theme ?type :force ?f)
        lf might contain several rules
    :return: the list of Rule objects
    """
    rules = re.split(r'\)[^\S\n\t]+\(', lf)
    rules = [rip_parens(x) for x in rules]
    rules = [load_list(x) for x in rules]
    return rules


def load_list(values, typ=TripsNode):
    positionals = []
    kvpair = {}
    tokens = values.strip().split()
    tokens.reverse()
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
    return typ(positionals, kvpair)


def rip_parens(input):
    """
    :param input: string in logical form
    :return: string without parens
    """
    return input.replace('(', ' ').replace(')', ' ')


def score_set(rule_set, tparse):
    """
    :param rule_set:
    :param tparse:
    :return: unnormalized score

    """
    match_score = 0
    var_score = 0
    ''' Match each rule to a tnode '''
    rule_tnode = {}
    ''' Globally match variables to terms. key: variable; value: a list of assignments'''
    var_term = {}
    ''' Find the best matching pairs of rule and tnode'''
    for rule in rule_set:
        rule = Rule(tnode=rule)
        max = 0
        for tnode in tparse:
            if rule.score(tnode) > max:
                rule_tnode[rule] = tnode
    ''' Dealing with variable assignments '''
    for rule, tnode in rule_tnode.items():
        rule.match_vars(tnode, var_term)
        match_score += rule.score(tnode)
    for var, terms in var_term.items():
        max_term, freq = most_common(terms)
        var_score += freq / len(terms)
    return match_score + var_score


def accuracy(rule_set, tparse):
    """
    The actual function that gives the score of a trips parse against a rule set
    :param rule_set:
    :param tparse:
    :return: score (normalized against the score of rule set itself)
    """
    return score_set(rule_set, tparse) / score_set(rule_set, rule_set)


def most_common(list):
    item = max(set(list), key=list.count)
    return item, list.count(item)
