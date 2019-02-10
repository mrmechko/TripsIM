import re
import logging
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
    def __init__(self, positionals, kvpairs, type_word=[]):
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
            term1_val, term2_val = self.value.lower(), other.value.lower()
            if term1_val in indicators or term2_val in indicators:
                return True
            # check that term1 and term2 are both ont types first
            term1 = ont[term1_val]
            term2 = ont[term2_val]
            if not term1 or not term2:
                logging.debug("Type not found:", term1_val, term2_val)
                # somehow they are equal strings and not indicators
                return term1_val == term2_val
            else:
                logging.debug("testing ont types:", term1, term2)
            return term1 == term2 or term1 < term2 or term2 < term1
        elif type(other) is Variable:
            return True
        return False


class Rule:

    def __init__(self, positionals=None, kvpairs=None, type_word=[], tnode=None):
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


def get_element(e):
    if e[0] == "?":
        return Variable(e)
    return Term(e)


def json_to_lisp(js):
    """
    :param js: json object representing logical form
    :return: a string in logical form in lisp format
    """
    lf = ""
    for data in js:
        lf += "("
        for name, entry in data.items():
            if type(entry) == dict:
                indicator, word, typ, roles = entry["indicator"], entry["word"], entry["type"], entry["roles"]
                lf += "(ONT::" + indicator + " " + name
                if word == None:
                    lf += " " + typ
                else:
                    lf += " (:* ONT::" + typ + " W::" + word + ")"
                for role, var in roles.items():
                    if role != "LEX":
                        if var[0] == "#":
                            lf += " :" + role + " " + var[1:]
                        elif var[0] == "?":
                            lf += " :" + role + " " + var
                        else:
                            lf += " :" + role + " ONT::" + var
                lf += ")"
        lf += ")"
    return lf


def load_list_set(lf):
    """
    :param lf: string in logical form or as a json object
        e.g. ((ONT::SPEECHACT ?x ONT::SA_REQUEST :CONTENT ?!theme)(ONT::F ?!theme ?type :force ?f)
        lf might contain several rules
    :return: the list of Rule objects
    TODO: doesn't work with triple quoted string for some reason
    """
    if type(lf) != str:
        lf = json_to_lisp(lf)
    rules = re.split(r'\)[^\S\n\t]*\(', lf)
    rules = [format_rule(x) for x in rules]
    rules = [load_list(x) for x in rules]
    return rules


def load_list(values, typ=TripsNode):
    type_word = []
    kvpair = {}
    values = values.strip()
    part1 = re.split(r':', values)[0]
    part2 = values.replace(part1, '')
    part1_list = part1.split('%')
    positionals = part1_list[0].split()
    if len(part1_list) > 1:
        type_word = part1.split('%')[1].split()
        type_word = [get_element(e) for e in type_word]
    positionals = [get_element(e) for e in positionals]
    part2 = part2.strip().split(':')
    for e in part2:
        if e.split():
            lst = e.split()
            if len(lst) == 2:
                kvpair[get_element(lst[0])] = get_element(lst[1])
            else:
                lst = e.replace('%', '').split()
                kvpair[get_element(lst[0])] = get_element(lst[1] + ' ' + lst[2])
    return typ(positionals, kvpair, type_word)


def format_rule(input):
    """
    :param input: string in logical form
    :return: string without parens
    TODO: Currently simply gets rid of patterns like (:* ONT::PLANT W::GRASS)
    """
    ret = re.sub(r'\([\s\t]*:[\s\t]*\*(.+?)\)', r'% \1 %', input)
    ''' replace (:* with % '''
    # ret = re.sub(r'\([\s\t]*:[\s\t]*\*', '% ', input)
    ret = ret.replace('(', ' ').replace(')', ' ')
    ret = ret.replace('ONT::', '').replace('W::', '')
    return ret


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
        if not unmapped_tnodes:
            raise ValueError('Not enough Tnodes in Trips parse')
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

        map[new_map[0]] = new_map[1]
        max_cand = score_wrt_map(map, rule_set, tparse)
        if current_score >= max_cand:
            map.pop(new_map[0])
            return current_score
        unmapped_rules.remove(new_map[0])
        unmapped_tnodes.remove(new_map[1])
        current_score = max_cand

    var2term, var2node = var_to_node(map)
    return current_score, var2term, var2node


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
    if isinstance(e, Term):
        name2 = e.value
    else:
        name2 = e.name
    for rule in rule_set:
        if isinstance(rule.positionals[1], Term):
            name = rule.positionals[1].value
        else:
            name = rule.positionals[1].name
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
    ''' get element-wise mapping '''
    for rule in rule_set:
        if rule in map:
            element_map[rule_to_element(rule)] = rule_to_element(map[rule])
    ''' translate the rule set '''
    for rule in rule_set:
        if rule not in map:
            break
        temp = Rule(positionals=[], kvpairs={})
        for pos in rule.positionals:
            '''
            Variables that cannot be mapped to a rule and Terms are stored as-is;
            Variables not in current mapping are ignored
            '''
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


def parse_rule_set(fpath):
    """
    Load in and parse a set of rules from a file
    """
    rs = []
    description = ""
    rule = ""
    for line in open(fpath, 'r').readlines():
        if line[0] == '#':
            description = line[2:]
        elif line[0] == '/':
            assert True
        elif line[0] == '-':
            if rule != "":
                rs.append((load_list_set(rule.replace("\n", "")), description.replace("\n", "")))
                rule, description = "", ""
        else:
            rule += line
    return rs


def grade_rules(rs, parse):
    """
    Given a parsed rule set and a given parse, find the rule that best matches the parse
    Currently outputs the score of the parse against every rule, as well as which rule it best matches
    """
    max = 0
    map = {}
    desc = ""
    for t in rs:
        r = t[0]
        d = t[1]
        s = score(r, parse)
        if s[0] > max:
            desc = d
            max = s[0]
            map = s[1]
        print("Score for rule: " + d + " is: " + str(s[0]))
    print("Match with rule: " + desc + " with a score of: " + str(max) + " with mapping: " + str(map))

def get_var_list(rule_set):
    '''
    Get the list of variables of a rule-set
    :param rule_set:
    :return:
    '''
    l = []
    for rule in rule_set:
        l += [p for p in rule.positionals if isinstance(p, Variable) and p not in l]
        l += [v for k, v in rule.kvpairs.items() if isinstance(v, Variable) and v not in l]
    return l


def var_to_node(map):
    '''
    Produce variable-to-term and variable-to-node mapping
    :param map:
    :return:
        var2term - dict
        var2node - dict
    '''
    var2term = {}
    var2node = {}
    if not isinstance(map, dict):
        raise ValueError('Expect input to be dictionary')
    for rule, tnode in map.items():
        var2term[rule_to_element(rule)] = rule_to_element(tnode)
        for k, v in rule.kvpairs.items():
            if k in tnode.kvpairs:
                var2term[v] = tnode.kvpairs[k]
    for k, v in var2term.items():
        var2node[k] = element_to_rule(k, map.keys())

    return var2term, var2node
