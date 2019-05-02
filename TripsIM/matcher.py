import re, json
from typing import List, Dict
from pytrips.ontology import load

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

ont = load()


class TripsNode:
    def __init__(self, positionals, kvpairs, type_word=None):
        self.positionals = positionals
        self.kvpairs = kvpairs
        self.type_word = type_word

    def __repr__(self):
        return "TripsNode<\n\ttype:" + str(self.type_word) + '\n\tpositionals:' + repr(
            self.positionals) + "\n\tkvpairs:" + repr(self.kvpairs) + ">\n"

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        if type(other) is not type(self):
            return False
        for t, u in zip(self.positionals, other.positionals):
            if t != u:
                return False
        if self.type_word != other.type_word:
            return False
        if len(self.kvpairs) != len(other.kvpairs):
            return False
        for x, y in self.kvpairs.items():
            if x not in other.kvpairs:
                return False
            if other.kvpairs[x] != y:
                return False
        return True


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
            return self.name.lower() == other.name.lower()
        if type(other) is Term:
            return True
        return False


indicators = ["speechact", "f", "pro", "pro-set"]


class Term(Element):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Term<%s>" % self.value

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        if type(other) is Term:
            term1, term2 = self.value.lower(), other.value.lower()
            if term1 in indicators or term2 in indicators:
                return True
            if str(ont[term1]) == "None":
                return str(ont[term2]) == "None"
            if str(ont[term2]) == "None":
                return str(ont[term1]) == "None"
            return ont[term1] == ont[term2] or ont[term1] < ont[term2] or ont[term2] < ont[term1]
        elif type(other) is Variable:
            return True
        return False


class Rule:

    def __init__(self, positionals: List = None,
                 kvpairs: Dict[Element, Element] = None,
                 type_word: List = None,
                 tnode: TripsNode = None) -> None:
        if tnode:
            self.positionals = tnode.positionals
            self.kvpairs = tnode.kvpairs
            self.type_word = tnode.type_word
        else:
            self.positionals = positionals
            self.kvpairs = kvpairs
            self.type_word = type_word

    def __repr__(self):
        return "Rule<\n\ttype:" + str(self.type_word) + '\n\tpositionals:' + repr(
            self.positionals) + "\n\tkvpairs:" + repr(self.kvpairs) + ">\n"
        # return '<' + str(self.positionals) + '>\n'

    def _score_positionals(self, tnode: TripsNode) -> int:
        """
        :param tnode:
        :return: number of positionals in Rule that have matches in tnode.positionals
        """
        sum = 0
        pos = tnode.positionals.copy()
        for p in self.positionals:
            if p in pos:
                pos.remove(p)
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


def get_element(elem: str) -> Element:
    if elem[0] == "?":
        return Variable(elem)
    return Term(elem)


def load_list_set(lf: str) -> List[TripsNode]:
    """
    :param lf: logical form as a json object
    :return: the list of Rule objects
    """
    rules = []
    for r in lf:
        for name, tnode in r.items():
            if name != "root":
                type_word = [get_element(tnode["type"])]
                if tnode["word"] is not None:
                    type_word.append(get_element(tnode["word"]))
                positionals = [get_element(tnode["indicator"]), get_element(tnode["id"])]
                kvpair = {}
                for k, v in tnode["roles"].items():
                    if k != "LEX":
                        kvpair[get_element(k)] = get_element(v.replace('#', ''))
                rules.append(TripsNode(positionals, kvpair, type_word))
    return rules


def score_wrt_map(map_: Dict[Rule, TripsNode], rule_set: List[Rule]):
    """
    Score a pair (rule_set, tparse) with respect to a rule-to-tnode mapping
    :param map_: dict{ rule: tnode}
    :param rule_set:
    :param tparse:
    :return: score
    """
    intersection = 0
    mapped_rule_set, new_map = element_mapping(map_, rule_set)
    for rule in mapped_rule_set:
        if new_map[rule] in map_:
            intersection += rule.score(map_[new_map[rule]])

    return intersection / cardinality(rule_set)


def score(rule_set: List[Rule], tparse: List[TripsNode]):
    """
    Find the highest-scoring mapping between rules and tnodes
    by greedily finding the pair (rule: tnode) that improve the score by largest number
    and add it to the mapping.

    The function should always return 1 for input rule_set == tparse.
    :param rule_set:
    :param tparse:
    :return: the score of tparse against rule_set
    """
    map_, current_score = {}, 0
    unmapped_tnodes = [tnode for tnode in tparse]
    unmapped_rules = [rule for rule in rule_set]
    while unmapped_rules:
        new_map, max_, candidates = (), 0, []
        if not unmapped_tnodes:
            raise ValueError('Not enough Tnodes in Trips parse')
        for rule in unmapped_rules:
            for tnode in unmapped_tnodes:
                map_[rule] = tnode
                rule_score = score_wrt_map(map_, rule_set)
                map_.pop(rule)
                if rule_score > max_:
                    max_, candidates = rule_score, [(rule, tnode)]
                if rule_score == max_:
                    candidates.append((rule, tnode))

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

        map_[new_map[0]] = new_map[1]
        max_cand = score_wrt_map(map_, rule_set)
        if current_score >= max_cand:
            map_.pop(new_map[0])
            return current_score
        unmapped_rules.remove(new_map[0])
        unmapped_tnodes.remove(new_map[1])
        current_score = max_cand

    var2term, var2node = var_to_node(map_)
    return current_score, var2term, var2node


def cardinality(rule_set: List[Rule]):
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

def rule_to_element(rule: Rule):
    return rule.positionals[1]

def element_to_rule(elem, rule_set):
    '''
    Find the rule corresponding to element e
    If e is seen in the rule set but has no corresponding rule, return None
    If e is not seen in the rule set, raise error
    :param e:
    :param rule_set:
    :return:
    '''
    if isinstance(elem, Term):
        name2 = elem.value
    else:
        name2 = elem.name
    
    for rule in rule_set:
        positionals = rule_to_element(rule)
        if isinstance(positionals, Term):
            name = positionals.value
        else:
            name = positionals.name
        if name == name2:
            return rule
    for rule in rule_set:
        if elem in rule.positionals or elem in rule.kvpairs.values():
            return None
    raise ValueError('Element {} not in rule set'.format(elem))


def element_mapping(map_: Dict[Rule, TripsNode], rule_set: List[Rule]):
    """
    Translate the rule_set using the mapping
    :param map_:
    :param rule_set:
    :return:
        mapped rule set
        a map between original and new rule set: {rule: new rule}
    """
    element_map, mapped_rule_set, new_map = {}, [], {}
    ''' get element-wise mapping '''
    for rule in rule_set:
        if rule in map_:
            element_map[rule_to_element(rule)] = rule_to_element(map_[rule])
    ''' translate the rule set '''
    for rule in rule_set:
        if rule not in map_:
            break
        new_rule = Rule(positionals=[], kvpairs={})
        for pos in rule.positionals:
            '''
            Variables that cannot be mapped to a rule and Terms are stored as-is;
            Variables not in current mapping are ignored
            '''
            if isinstance(pos, Term) or not element_to_rule(pos, rule_set):
                new_rule.positionals.append(pos)
            elif pos in element_map:
                new_rule.positionals.append(element_map[pos])

        for k, v in rule.kvpairs.items():
            if isinstance(v, Term) or not element_to_rule(v, rule_set):
                new_rule.kvpairs[k] = v
            elif v in element_map:
                new_rule.kvpairs[k] = element_map[v]
                
        mapped_rule_set.append(new_rule)
        new_map[new_rule] = rule
    return mapped_rule_set, new_map


def parse_rule_set(fpath):
    """
    Load in and parse a set of rules from a file
    """
    js, ruleset = json.load(open(fpath, 'r')), []
    for entry in js:
        ruleset.append((load_list_set(entry["rule"]), entry["description"]))
    return ruleset #list of (list_set, description)


def grade_rules(ruleset, parse):
    """
    Given a parsed rule set and a given parse, find the rule that best matches the parse
    Currently outputs the score of the parse against every rule, as well as which rule it best matches
    """
    max_score, mapping = 0, {}
    desc = ""
    for t in ruleset:
        rule = t[0]
        description, rule_score = t[1], score(rule, parse)
        if rule_score[0] > max_score:
            desc = description
            max_score = rule_score[0]
            mapping = rule_score[1]
        print("Score for rule: " + description + " is: " + str(rule_score[0]))
    print("Match with rule: " + desc + " with a score of: " + str(max_score) + " with mapping: " + str(mapping))


def get_var_list(rule_set: List[Rule]) -> List[Variable]:
    '''
    Get the list of variables of a rule-set
    :param rule_set:
    :return:
    '''
    var_list = []  # type: List[Variable]
    for rule in rule_set:
        var_list += [p for p in rule.positionals if isinstance(p, Variable) and p not in var_list]
        var_list += [v for k, v in rule.kvpairs.items() if isinstance(v, Variable) and v not in var_list]
    return var_list


def var_to_node(map_: Dict[Rule, TripsNode]) -> (Dict[Variable, Term], Dict[Variable, TripsNode]):
    '''
    Produce variable-to-term and variable-to-node mapping
    :param map_:
    :return:
        var2term - dict
        var2node - dict
    '''
    var2term, var2node = {}, {}
    if not isinstance(map_, dict):
        raise ValueError('Expect input to be dictionary')
    for rule, tnode in map_.items():
        var2term[rule_to_element(rule)] = rule_to_element(tnode)
        for k, v in rule.kvpairs.items():
            if k in tnode.kvpairs and isinstance(v, Variable):
                var2term[v] = tnode.kvpairs[k]
    for k, v in var2term.items():
        var2node[k] = element_to_rule(k, map_.keys())

    return var2term, var2node
