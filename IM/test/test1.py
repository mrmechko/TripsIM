import sys, os
sys.path.insert(0, os.path.abspath('../..'))
import IM.PyIM as PyIM
from IM.PyIM import matcher

if __name__ == '__main__':
    rule_set1 = '((SPEECH-ACT ?x SA_TELL :CONTENT ?!theme) ' \
                '(F ?!theme ?what ?type :AGENT ?f)'
    rule_set1 = PyIM.matcher.load_list_set(rule_set1)
    card_rule = matcher.cardinality(rule_set1)
    parse1 = '''
        (SPEECH-ACT V1182287 SA_TELL :CONTENT V1182124 :LEX BUY) \
        (F V1182124 :AGENT V1182288 :AFFECTED V1182170 :BENEFICIARY V1182128 :TENSE PRES :LEX BUY) \
        (IMPRO V1182288 REFERENTIAL-SEM :PROFORM SUBJ) \
        (PRO V1182128 (:* PERSON W::ME) :PROFORM ME :LEX ME :COREF USER) \
        (A V1182170 (:* COMPUTER-TYPE W::LAPTOP) :LEX LAPTOP)'''
    parse1 = matcher.load_list_set(parse1)
    map1 = {matcher.get_element('?x'):matcher.get_element('V1182287'), matcher.get_element('?!theme'):matcher.get_element('V1182124')}
    map1 = {rule_set1[0]:parse1[0], rule_set1[1]:parse1[1]}
    print(matcher.score_wrt_map(map1, rule_set1, parse1))
    print(matcher.score(rule_set1, parse1))
    print(matcher.score(rule_set1, rule_set1))
