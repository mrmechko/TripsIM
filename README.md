# IMDocumentation

<!-- toc -->
- [Matcher](#matcher)
    * [Data structure](#data-structure)
    * [Matching routine](#matching-routine)
- [Usage](#usage)
    * [Input](#input)
- [References](#references)
## Matcher

### Data structure

### Matching routine

The matching function referenced [Champin, Pierre-Antoine, and Christine Solnon](https://perso.liris.cnrs.fr/pierre-antoine.champin/publis/iccbr2003a.pdf).
The basic idea of matching this kind of labeled (both vertices and edges), directed graph is:
1. Define a scoring function that evaluates similarity between two graphs given a mapping.
2. Use a greedy approach to find the best pair to add to the existing mapping, one at a time until 
all the nodes are mapped or the score cannot be improved (best pair means adding it to the mapping improves the score
by the largest margin).

## Usage 
If we start with string-formatted logical forms, e.g.
```
((SPEECH-ACT ?x SA_TELL :CONTENT ?!theme) 
 (F ?!theme ?what ?type :AGENT ?f)
 ```
 we need to load it into a set of rules using `load_list_set()`.
 
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

### Input

## References
Champin, Pierre-Antoine, and Christine Solnon. "Measuring the similarity of labeled graphs." International Conference on Case-Based Reasoning. Springer, Berlin, Heidelberg, 2003.