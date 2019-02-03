import json, sys, os
#sys.path.insert(0, os.path.abspath('../..'))
import TripsIM as PyIM
from TripsIM import matcher
import pprint

normal_form = '((ONT::SPEECHACT V137370 SA_TELL :CONTENT V137265)' \
            '(ONT::F V137265 (:* ONT::HAVE-PROPERTY W::BE) :NEUTRAL V137257 :FORMAL V137287 :TENSE ONT::PRES)' \
            '(ONT::THE V137257 (:* ONT::PLANT W::GRASS))' \
            '(ONT::F V137287 (:* ONT::GREEN W::GREEN) :FIGURE V137257 :SCALE ONT::GREEN*1--07--00))'

def lf_equality(a, b):
    assert len(a) == len(b)
    for x in a:
        assert x in b

def test_equality():
    norm1 = matcher.load_list_set(normal_form)
    norm2 = matcher.load_list_set(normal_form)
    for i in range(len(norm1)):
        pprint.pprint(norm1[i])
        print("-")
        pprint.pprint(norm2[i])
        assert norm1[i] == norm2[i]


def test_json():
    # "The grass is green" in logical from trips web parser
    json_form = json.load(open("data/grass.json"))
    norm = matcher.load_list_set(normal_form)
    jsrm = matcher.load_list_set(json_form)
    lf_equality(norm, jsrm)
