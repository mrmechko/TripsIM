# IMDocumentation

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


## To-do


## Usage 
If we start with string-formatted logical forms, e.g.
```
((SPEECH-ACT ?x SA_TELL :CONTENT ?!theme) 
 (F ?!theme ?what ?type :AGENT ?f)
 ```
 we need to load it into a set of rules using `load_list_set()`. 

 We are also able to pass a json object into that same function.
 
 Do the same to a TRIPS parse, e.g.
  ```
((ONT::SPEECHACT ONT::V1617693 SA_TELL :CONTENT ONT::V1617530 :LEX ONT::BUY)
 (ONT::F ONT::V1617530 (:* ONT::PURCHASE W::BUY) :AGENT ONT::V1617694 :AFFECTED ONT::V1617576 :BENEFICIARY ONT::V1617534 :TENSE ONT::PRES :LEX ONT::BUY)
 (ONT::IMPRO ONT::V1617694 REFERENTIAL-SEM :PROFORM ONT::SUBJ)
 (ONT::PRO ONT::V1617534 (:* ONT::PERSON W::ME) :PROFORM ONT::ME :LEX ONT::ME :COREF ONT::USER)
 (ONT::A ONT::V1617576 (:* ONT::COMPUTER-TYPE W::LAPTOP) :LEX ONT::LAPTOP)
)
   ```
Then passing the two loaded set to `score()` will give the score of the parse against the rule set.

We are also able to load in a list of rules from a file and test a given parse against that list of rules to find the best match.

The text file storing the list of rules must be formatted as follows:
```
---
# Description of pattern 1
/ Comment 1
/ Comment 2
/ ...
Pattern in logical form using Lisp-like syntax with variables in the format "?x" where x can be whatever you want.
---
# Description of pattern 2
...
```

We can parse a file in this format using the `parse_rule_set()` function which returns a list of tuples that hold (parsed rule, description of rule).

Then we can pass the output from the previous function and a parsed rule into the `grade_rules()` function which will return the description of the highest matching rule as well as the score of that match (1.0 for an exact match).

### Input

## References
Champin, Pierre-Antoine, and Christine Solnon. "Measuring the similarity of labeled graphs." International Conference on Case-Based Reasoning. Springer, Berlin, Heidelberg, 2003.
