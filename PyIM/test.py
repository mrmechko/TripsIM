import PyIM.matcher as matcher

if __name__ == '__main__':
    rule_set1 = '((ONT::1 ONT::2 :CONTENT ?!theme) ' \
                '(ONT::F ?!theme ?type :force ?f)'
    rule_set1 = matcher.load_list_set(rule_set1)
    parse1 = '((ONT::1 ONT::3 :CONTENT some-content) ' \
             '(ONT::F something some-content :force some-force :AGENT some-agent)'
    parse1 = matcher.load_list_set(parse1)
    print(matcher.accuracy(rule_set1, parse1))