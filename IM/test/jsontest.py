import json, sys, os
sys.path.insert(0, os.path.abspath('../..'))
import IM.PyIM as PyIM
from IM.PyIM import matcher

if __name__ == '__main__':
    # "The grass is green" in logical from trips web parser
    normal_form = '((ONT::SPEECHACT V137370 SA_TELL :CONTENT V137265)' \
                '(ONT::F V137265 (:* ONT::HAVE-PROPERTY W::BE) :NEUTRAL V137257 :FORMAL V137287 :TENSE ONT::PRES)' \
                '(ONT::THE V137257 (:* ONT::PLANT W::GRASS))' \
                '(ONT::F V137287 (:* ONT::GREEN W::GREEN) :FIGURE V137257 :SCALE ONT::GREEN*1--07--00))'
    json_form = json.load(open("../data/grass.json"))
    normal_form = matcher.load_list_set(normal_form)
    json_form = matcher.load_list_set(json_form)
    print(normal_form)
    print(json_form)
    print(str(normal_form) == str(json_form))