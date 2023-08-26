## NLI

The novel data are contained in json format within `gold.json`.
The FraCaS-adaped data are contained within `FraCaS.json`.
Each sample contains a premise, a hypothesis, a non-empty set of relevant linguistic tags and a non-empty set of possible inference labels.
For FraCaS, the hypothesis can consist of multiple sentences.

### Python Interface
To load and process the data in python, set your working directory to match the `src` folder of this repository.

To load the dataset:
```python
from nli.dataset import Dataset
from json import load

with open('./nli/gold.json', 'r') as f:
    dataset = Dataset.from_json(load(f))
```

To visually inspect individual samples:
```pycon
>>> from pprint import pprint
>>> pprint(dataset.samples[769])
Sample(premise='Στην Ελένη αρέσουν όλα τα εξωτικά φρούτα.',
       hypothesis='Το μάγκο δε αρέσει της Ελένης.',
       tags={Lexical Entailment:Lexical Semantics:Hypernymy,
             Predicate-Argument Structure:Alternations,
             Logic:Single Negation,
             Logic:Quantification:Universal},
       labels={Contradiction})
>>> pprint(dataset.samples[528])
Sample(premise='Ο Ωρίωνας είναι αστέρι στο τένις.',
       hypothesis='Ο Ωρίωνας είναι αστέρι.',
       tags={Predicate-Argument Structure:Intersectivity:Non-Intersective,
             Common Sense/Knowledge},
       labels={Contradiction, Unknown})
```

Use standard python queries to isolate samples of interest.