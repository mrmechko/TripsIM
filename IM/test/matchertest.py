import sys, os

sys.path.insert(0, os.path.abspath('../..'))
import IM.PyIM as PyIM
from IM.PyIM import matcher

if __name__ == '__main__':

    ''' Test: 
    match rule-set to itself 
    should always get score = 1 '''

    rule_set = '((ONT::SPEECHACT ?speechact SA_TELL :CONTENT ?content)' \
               '(ONT::F ?content (:* ONT::HAVE-PROPERTY ?word-content) :NEUTRAL ?neutral :FORMAL ?formal :TENSE ONT::PRES)' \
               '(ONT::THE ?neutral (:* ONT::PLANT ?word-neutral))' \
               '(ONT::F ?formal (:* ONT::COLOR-VAL ?word-formal) :FIGURE ?neutral))'
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
