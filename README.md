# OYXOY
*A modern NLP Test Suite for Modern Greek*



---

## About
The repository aims to serve as a community meeting point for the collective development, testing, and distribution of 
datasets for the evaluation of Greek NLP systems. 
Contributions and feedback are highly encouraged.

## Datasets
The repository currently contains two gold-standard datasets, described in our paper *"OYXOY: A Modern NLP Test Suite 
for Modern Greek"* ([abs/23909.07009](https://arxiv.org/abs/2309.07009)).

### Natural Language Inference (NLI)

A collection of 1763 sentence pairs, each pair associated with a set of entailment labels and linguistic tags.
The labels describe all the possible inferential relations (of `Neutral`, `Entailment` and `Contradiction`) that hold
between premise and hypothesis, accounting for all possible semantic readings (if more than one is available).
The tags provide a rough characterization of each sentence pair depending on the set of linguistic phenomena it 
exhibits, allowing for a finer-grained error analysis and evaluation.
Of the 1763 pairs, 1049 are novel and 713 are converted from the Greek FraCaS.
All pairs and their annotations are written and checked by human experts.

### WordSense
A structured subset of the Dictionary of Modern Greek focusing on word polysemy.
The dataset specifies a number of senses for each word.
Each sense consists of a periphrastic definition (in natural language) and a collection of example phrases or sentences
for that particular word-sense.
In total, it specifies 6896 senses (and definitions) for 2326 entries, justified by 14416 examples. 
The dataset is extrapolated by machine translation using ChatGPT, fine-tuned on a small set of examples.
All the translated entries are human-verified and faithful to the source dictionary.

## Project Structure
Each dataset is provided in the form of json files. 
To assist in processing the files, we provide optional python interfaces in the form of independent modules, located
under **/src/**.

* **/src** :: the source folder -- copy its contents to your working directory
    * **/src/nli/** :: python module for the NLI dataset
    * **/src/wordsense/** :: python module for the WordSense dataset
* **/README.md** :: this file

Browse to the subdirectory of interest and inspect the README file within for more info.

## Requirements
`Python >= 3.10` if using the Python interfaces

# Citing

If you use either the NLI or the Wordsense dataset or any of the associated tasks in your academic work, please
cite:
```
@misc{kogkalidis2023oyxoy,
      title={OYXOY: A Modern NLP Test Suite for Modern Greek}, 
      author={Konstantinos Kogkalidis and Stergios Chatzikyriakidis and Eirini Chrysovalantou Giannikouri and Vassiliki Katsouli and Christina Klironomou and Christina Koula and Dimitris Papadakis and Thelka Pasparaki and Erofili Psaltaki and Efthymia Sakellariou and Hara Soupiona},
      year={2023},
      eprint={2309.07009},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```
---

**Feel free to explore and utilize these datasets for your projects. Contributions are welcome!**