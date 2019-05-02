# IMDocumentation

[![Build Status](https://travis-ci.com/mrmechko/TripsIM.svg?branch=package)](https://travis-ci.com/mrmechko/TripsIM)

<!-- toc -->
- [Matcher](#matcher)
    * [Data structure](#data-structure)
    * [Matching routine](#matching-routine)
- [To-do](#to-do)
- [Usage](#usage)
    * [Input](#input)
- [References](#references)
## Matcher

### Data structure

Tripsnode and Rule have the same structure:
* positionals: a list of elements
* type_word: the pair (type, word) as in `(:* ONT::PLANT W::GRASS)`
* kvpairs: the dictionary of {role: element}

If the `(type word)` pattern appears in the kvpairs, e.g. `:role (:* type word)`, 
currently it is recorded as `{role: "type word"}` in the TripsNode. 
The design concerning type-word pairs will possibly need modification.

### Matching routine

The matching function referenced [Champin, Pierre-Antoine, and Christine Solnon](https://perso.liris.cnrs.fr/pierre-antoine.champin/publis/iccbr2003a.pdf).
The basic idea of matching this kind of labeled (both vertices and edges), directed graph is:
1. Define a scoring function that evaluates similarity between two graphs given a mapping.
2. Use a greedy approach to find the best pair to add to the existing mapping, one at a time until 
all the nodes are mapped or the score cannot be improved (best pair means adding it to the mapping improves the score
by the largest margin).

### Heuristics
The goodness of fit between a Trips parse `P` and a rule set `R`' with respect to a mapping is evaluated as:
` sum (intersection(p, r))/ sum (cardinality(r)) for each mapped pair (p, r)`,
where the intersection is the number of matches among positionals and kvpairs for each, 
and the cardinality is `kvpairs.length + positionals.length`.


## Usage 
The script test/trips_web_interface.py will use the ruleset in data/ruleset.json and match it against the output of trips-web of the given command line argument.
Example usage: `trips_web_interface.py "John wants candy."`
```
Score for rule: !x wants !y is: 1.0
Score for rule: Does !x exist? is: 0.8888888888888888
Score for rule: Does !x know !y? is: 0.9
Score for rule: !x is !y is: 0.875
Score for rule: !x eats !y is: 0.75
```

The matcher should be used in conjunction with trips-web in order to get logical form in json format (https://github.com/mrmechko/trips-web)
The matcher takes in a logical form in json format, and matches that against a list of rules also in json format.
Below is an example of how the sentence "Grass is green" would be formatted in json. 
```
[
  {
    "V59225": {
      "id": "V59225",
      "indicator": "SPEECHACT",
      "type": "SA_TELL",
      "word": null,
      "roles": {
        "CONTENT": "#V59158",
        "LEX": "IS"
      },
      "start": 0,
      "end": 13
    },
    "V59158": {
      "id": "V59158",
      "indicator": "F",
      "type": "HAVE-PROPERTY",
      "word": "BE",
      "roles": {
        "NEUTRAL": "#V59149",
        "FORMAL": "#V59172",
        "TENSE": "PRES",
        "LEX": "IS"
      },
      "start": 0,
      "end": 13
    },
    "V59149": {
      "id": "V59149",
      "indicator": "THE",
      "type": "GEOGRAPHIC-REGION",
      "word": "GRASS",
      "roles": {
        "NAME-OF": "GRASS",
        "LEX": "GRASS"
      },
      "start": 0,
      "end": 6
    },
    "V59172": {
      "id": "V59172",
      "indicator": "F",
      "type": "GREEN",
      "word": "GREEN",
      "roles": {
        "FIGURE": "#V59149",
        "SCALE": "GREEN*1--07--00",
        "LEX": "GREEN"
      },
      "start": 9,
      "end": 13
    },
    "root": "#V59225"
  }
]
```
 We load in a given parse by running the `load_list_set()` function on the json object.

 We can also load in an entire ruleset by running `parse_rule_set()` on a json formatted ruleset. 

Then you are able to pass the ruleset and parse into `score(ruleset, parse)` which will give the score of the parse against the rule set.

The ruleset is a json object which holds a objects with information about the description of the rule, an example of the rule (which should always match 1.0 against that rule), and the rulse itself.
```
{
    "description": "!x is !y",
    "example": "The block is red",
    "rule": [
        {
          "V41613": {
            "id": "V41613",
            "indicator": "SPEECHACT",
            "type": "SA_TELL",
            "word": null,
            "roles": {
                  "CONTENT": "#V41534",
              "LEX": "ARE"
            }
          },
          "V41534": {
            "id": "V41534",
            "indicator": "F",
            "type": "HAVE-PROPERTY",
            "word": "BE",
            "roles": {
              "NEUTRAL": "?x",
              "FORMAL": "?y",
              "TENSE": "PRES",
              "LEX": "ARE"
            }
          },
          "root": "V41613"
        }
     ]
},
```
The above rule matches anything of the form "!x is !y", it has the example of "The block is red", and the rule is specified as having a NEUTRAL of ?x and a FORMAL of ?y.

The best way to create a rule and add it to the ruleset is to take an existing parse (output by trips-web) and replace those elements that you want to be variables with names starting with '?' ('?theme', '?x', '?person').

We can parse a file in this format using the `parse_rule_set()` function which returns a list of tuples that hold (parsed rule, description of rule).

Then we can pass the output from the previous function and a parsed rule into the `grade_rules()` function which will return the description of the highest matching rule as well as the score of that match (1.0 for an exact match).

## References
Champin, Pierre-Antoine, and Christine Solnon. "Measuring the similarity of labeled graphs." International Conference on Case-Based Reasoning. Springer, Berlin, Heidelberg, 2003.
