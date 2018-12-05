import sys, os

sys.path.insert(0, os.path.abspath('../..'))
import IM.PyIM as PyIM
from IM.PyIM import matcher

if __name__ == '__main__':

    ''' Test: 
    match rule-set to itself 
    should always get score = 1 '''

    def parse_rule_set(fpath):
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
                    rs.append((matcher.load_list_set(rule.replace("\n", "")), description.replace("\n", "")))
                    rule, description = "", ""
            else:
                rule += line
        return rs

    def grade_rules(rs, parse):
        max = 0
        desc = ""
        for t in rs:
            r = t[0]
            d = t[1]
            s = matcher.score(r, parse)
            if s > max:
                desc = d
                max = s
            print("Score for rule: " + d + " is: " + str(s)) 
        print("Match with rule: " + desc + " with a score of: " + str(max))
        

    rule_set = '((ONT::SPEECHACT ?speechact SA_TELL :CONTENT ?content)' \
               '(ONT::F ?content (:* ONT::HAVE-PROPERTY ?word-content) :NEUTRAL ?neutral :FORMAL ?formal :TENSE ONT::PRES)' \
               '(ONT::THE ?neutral (:* ONT::PLANT ?word-neutral))' \
               '(ONT::F ?formal (:* ONT::COLOR-VAL ?word-formal) :FIGURE ?neutral))'
    rule_set = matcher.load_list_set(rule_set)
    print(matcher.score(rule_set, rule_set))


    rule_set = '((ONT::SPEECHACT ?speechact SA_TELL :CONTENT ?content)' \
               '(ONT::F ?content (:* ONT::HAVE-PROPERTY ?word-content) :NEUTRAL ?neutral :FORMAL ?formal :TENSE ONT::PRES)' \
               '(ONT::THE ?neutral (:* ONT::PLANT ?word-neutral))' \
               '(ONT::F ?formal (:* ONT::COLOR-VAL ?word-formal) :FIGURE ?neutral))'
    parse = '((ONT::SPEECHACT V137370 SA_TELL :CONTENT V137265)' \
            '(ONT::F V137265 (:* ONT::HAVE-PROPERTY W::BE) :NEUTRAL V137257 :FORMAL V137287 :TENSE ONT::PRES)' \
            '(ONT::THE V137257 (:* ONT::PLANT W::GRASS))' \
            '(ONT::F V137287 (:* ONT::GREEN W::GREEN) :FIGURE V137257 :SCALE ONT::GREEN*1--07--00))'
    rule_set = matcher.load_list_set(rule_set)
    parse = matcher.load_list_set(parse)
    print(matcher.score(rule_set, parse))

    # Should match with first template in rule set
    parse2 = '((ONT::SPEECHACT ONT::V40122 SA_TELL :CONTENT ONT::V39968)' \
             '(ONT::F ONT::V39968 (:* ONT::WANT W::WANT) :EXPERIENCER ONT::V39953 :FORMAL ONT::V40003 :TENSE ONT::PRES)' \
             '(ONT::PRO ONT::V39953 (:* ONT::PERSON W::I) :PROFORM ONT::I)' \
             '(ONT::F ONT::V40003 (:* ONT::PURCHASE W::BUY) :AGENT ONT::V39953 :AFFECTED ONT::V40050 :VFORM ONT::BASE)' \
             '(ONT::A ONT::V40050 (:* ONT::COMPUTER W::COMPUTER)))'

    # Should match with fifth template in rule set
    parse3 =    '((ONT::SPEECHACT ONT::V40598 SA_YN-QUESTION :CONTENT ONT::V40347)' \
                '(ONT::F ONT::V40347 (:* ONT::KNOW W::KNOW) :EXPERIENCER ONT::V40332 :NEUTRAL ONT::V40369 :TENSE ONT::PRES :MODALITY (:* DO DO))' \
                '(ONT::PRO ONT::V40332 (:* ONT::PERSON W::YOU) :PROFORM ONT::YOU)' \
                '(ONT::THE ONT::V40369 (:* ONT::MALE-PERSON W::MAN) :ASSOC-WITH ONT::V40366)' \
                '(ONT::KIND ONT::V40366 (:* ONT::BAGELS-BISCUITS W::MUFFIN)))'
    grade_rules(parse_rule_set("ruleset.txt"), matcher.load_list_set(parse2))
    grade_rules(parse_rule_set("ruleset.txt"), matcher.load_list_set(parse3))
