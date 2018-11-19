import re
import IM.PyIM.ontologytools as ont

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
            return self.value == other.value or ont.isAncestor(other, self) or ont.isAncestor(self, other)
        elif type(other) is Variable:
            return True
        return False


class Rule:

    def __init__(self, positionals=None, kvpairs=None, tnode=None):
        if tnode:
            self.positionals = tnode.positionals
            self.kvpairs = tnode.kvpairs
        else:
            self.positionals = positionals
            self.kvpairs = kvpairs

    def __repr__(self):
        return "TripsNode<" + repr(self.positionals) + " " + repr(self.kvpairs) + ">"

    def _score_positionals(self, tnode: TripsNode) -> int:  # TODO: missing positionals
        """
        :param tnode:
        :return: number of positionals in Rule that have matches in tnode.positionals
        """
        j = 0
        last = 0
        sum = 0
        for i in range(len(self.positionals)):
            item = self.positionals[i]
            if item in tnode.positionals[last:]:
                j = tnode.positionals.index(item, last)
                last = j + 1
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
    TODO: doesn't work with triple quoted string for some reason
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


def score_wrt_map(map, rule_set, tparse):
    """
    Score a pair (rule_set, tparse) with respect to a rule-to-tnode mapping
    :param map: dict{ rule: tnode}
    :param rule_set:
    :param tparse:
    :return: score
    """
    intersection = 0
    mapped_rule_set, new_map = element_mapping(map, rule_set)
    for rule in mapped_rule_set:
        if new_map[rule] in map:
            intersection += rule.score(map[new_map[rule]])
    score = intersection / cardinality(rule_set)
    return score


def score(rule_set, tparse):
    """
    Find the highest-scoring mapping between rules and tnodes
    by greedily finding the pair (rule: tnode) that improve the score by largest number
    and add it to the mapping.

    The function should always return 1 for input rule_set == tparse.
    :param rule_set:
    :param tparse:
    :return: the score of tparse against rule_set
    """
    map = {}
    current_score = 0
    unmapped_tnodes = [tnode for tnode in tparse]
    unmapped_rules = [rule for rule in rule_set]
    while unmapped_rules:
        new_map = ()
        max = 0
        candidates = []
        for rule in unmapped_rules:
            for tnode in unmapped_tnodes:
                map[rule] = tnode
                sc = score_wrt_map(map, rule_set, tparse)
                map.pop(rule)
                if sc > max:
                    max = sc
                    candidates = [(rule, tnode)]
                if sc == max:
                    candidates.append((rule, tnode))
        print('candidates:', candidates)
        max_cand = 0
        for rule, tnode in candidates:
            cand_score = 0
            rule_node = rule_to_element(rule)
            ''' potential outcoming edges '''
            cand_score += len([k for k, v in rule.kvpairs.items() if k in tnode.kvpairs])
            ''' potential incoming edges '''
            for rule2 in rule_set:
                cand_score += len([k for k, v in rule2.kvpairs.items() if v == rule_node and k in tnode.kvpairs])
            if cand_score >= max_cand:
                max_cand = cand_score
                new_map = (rule, tnode)
        print('new map: ', new_map)
        map[new_map[0]] = new_map[1]
        max_cand = score_wrt_map(map, rule_set, tparse)
        if current_score >= max_cand:
            map.pop(new_map[0])
            return current_score
        unmapped_rules.remove(new_map[0])
        unmapped_tnodes.remove(new_map[1])
        current_score = max_cand
    return current_score


def cardinality(rule_set):
    """
    Used for normalizing scores
    :param rule_set:
    :return: the number of all positionals and kvpairs in rule_set
    """
    card = 0
    for rule in rule_set:
        card += len([pos for pos in rule.positionals])
        card += len([k for k in rule.kvpairs])
    return card


def element_to_rule(e, rule_set):
    '''
    Find the rule corresponding to element e
    If e is seen in the rule set but has no corresponding rule, return None
    If e is not seen in the rule set, raise error
    :param e:
    :param rule_set:
    :return:
    '''
    for rule in rule_set:
        if isinstance(rule.positionals[1], Term):
            name = rule.positionals[1].value
        else:
            name = rule.positionals[1].name

        if isinstance(e, Term):
            name2 = e.value
        else:
            name2 = e.name
        if name == name2:
            return rule
    for rule in rule_set:
        if e in rule.positionals or e in rule.kvpairs.values():
            return None
    raise ValueError('Element {} not in rule set'.format(e))


def rule_to_element(rule):
    return rule.positionals[1]


def element_mapping(map, rule_set):
    """
    Translate the rule_set using the mapping
    :param map:
    :param rule_set:
    :return:
        mapped rule set
        a map between original and new rule set: {rule: new rule}
    """
    element_map = {}
    mapped_rule_set = []
    new_map = {}
    for rule in rule_set:
        if rule in map:
            element_map[rule_to_element(rule)] = rule_to_element(map[rule])
    for rule in rule_set:
        if rule not in map:
            break
        temp = Rule(positionals=[], kvpairs={})
        for pos in rule.positionals:
            if isinstance(pos, Term) or not element_to_rule(pos, rule_set):
                temp.positionals.append(pos)
            elif pos in element_map:
                temp.positionals.append(element_map[pos])
        for k, v in rule.kvpairs.items():
            if isinstance(v, Term) or not element_to_rule(v, rule_set):
                temp.kvpairs[k] = v
            elif v in element_map:
                temp.kvpairs[k] = element_map[v]
        mapped_rule_set.append(temp)
        new_map[temp] = rule
    return mapped_rule_set, new_map
