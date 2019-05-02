import json, sys, os
from tripsweb.query import wsd as parse
from TripsIM import matcher
sys.path.insert(0, os.path.abspath('../..'))

if __name__ == '__main__':
    json_form = parse(sys.argv[1], tags=[])[0]
    ruleset = matcher.parse_rule_set("../data/ruleset.json")
    toMatch = matcher.load_list_set([json_form])
    matcher.grade_rules(ruleset, toMatch)
