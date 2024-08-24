import pandas as pd
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))

from experiments.inference.data import load_data as inference_load_data
from experiments.metaphor.data import load_file as metaphor_load_file , filter_metaphors
from experiments.disambiguation.data import load_file as disambiguation_load_file, process_data_wo_tokenization as disambiguation_process_data
from experiments.disambiguation.batching import Sampler
from experiments.llms.icl import FinetunedXNLIBasedICL
from experiments.llms.prompts import *
from random import seed, sample
from pathlib import Path


class DisambiguationPromptHandler:
    def __init__(self, method, n_shots):
        self.method = method
        entries = disambiguation_load_file('src/wordsense/dataset.json').entries
        definitions, examples = disambiguation_process_data()
        seed(1312)
        test_definitions = sample(list(range(len(definitions))), int(0.1 * len(definitions)))
        examples = sample(examples, len(examples))
        split1, split2 = int(0.6 * len(examples)), int(0.8 * len(examples))
        train, dev, test = examples[:split1], examples[split1:split2], examples[split2:]
        out_of_dist = [(ex, entry_id, sense_id) for (ex, entry_id, sense_id) in train if entry_id in test_definitions]
        test = [*test, *out_of_dist]
        train = [(ex, entry_id, sense_id) for (ex, entry_id, sense_id) in train if entry_id not in test_definitions]
        in_dist = {entry_id for _, entry_id, _ in train}
        test_in = [(ex, entry_id, sense_id) for ex, entry_id, sense_id in test if entry_id in in_dist]
        test_out = [(ex, entry_id, sense_id) for ex, entry_id, sense_id in test if entry_id not in in_dist]
        print(f'In: {len(test_in)}, Out: {len(test_out)}')

        self.train_sampler = Sampler(definitions, sorted(train, key=lambda x: x[1]))
        self.dev_sampler = Sampler(definitions, sorted(dev, key=lambda x: x[1]))
        self.test_in_sampler = Sampler(definitions, sorted(test_in, key=lambda x: x[1]))
        self.test_out_sampler = Sampler(definitions, sorted(test_out, key=lambda x: x[1]))

    

class SenseSelectionPromptHandler(DisambiguationPromptHandler):
    def __init__(self, method, n_shots):

        super().__init__(method, n_shots)
        self.train = self._sampler_to_data(self.train_sampler).to_dict('records')
        self.dev = self._sampler_to_data(self.dev_sampler).to_dict('records')
        self.test_in = self._sampler_to_data(self.test_in_sampler).to_dict('records')
        self.test_out = self._sampler_to_data(self.test_out_sampler).to_dict('records')
        self.test_sets = {'iv':self.test_in, 'oov':self.test_out}

    def _sampler_to_data(self, sampler):
        examples = pd.DataFrame(sampler.examples, columns=['example','sample_id', 'def_id'])
        definitions = pd.Series(sampler.definitions, name='definitions').reset_index()
        data = examples.merge(definitions, left_on='sample_id', right_on='index')[['example', 'definitions', 'def_id']]
        return data

    def _get_prompts(self):
        if self.method == 'zero_shot_ss':
            return zero_shot_ss_system, zero_shot_ss_user
        elif self.method =='zero_shot_ss_gr':
            return zero_shot_ss_system_gr, zero_shot_ss_user_gr
        elif self.method =='zero_shot_ss_en':
            return zero_shot_ss_system_en, zero_shot_ss_user_en
        assert self.method in METHODS['sense-selection'], f"Prompt should be one of {METHODS['sense-selection']}"
    

    def get_messages(self, sample, sample_idx, n_shots=None):
        prompt_sys, prompt_usr = self._get_prompts()
        messages = [
            {"role": "system", "content": prompt_sys},
            {"role": "user", "content": prompt_usr.format(sample['example'][0][sample['example'][1].index(True)], " ".join(sample['example'][0]), "".join([f'{ii+1}. {definition} ' for ii,definition in enumerate(sample['definitions'])]))},
        ] 
        return messages

    def get_chats(self):
        train_sample_messages = []
        for sample in self.train:
            messages = self.get_messages(sample, None)
            messages.append({'role':'assistant', 'content': str(sample['def_id']+1) })
            train_sample_messages.append(messages)
        
        dev_sample_messages = []
        for sample in self.dev:
            messages = self.get_messages(sample, None)
            messages.append({'role':'assistant', 'content': str(sample['def_id']+1) })
            dev_sample_messages.append(messages)

        return {"train": {"chat": train_sample_messages}, "dev":{"chat": dev_sample_messages}}


class WordInContextPromptHandler(DisambiguationPromptHandler):
    def __init__(self, method, n_shots):

        super().__init__(method, n_shots)
        self.train = self._sampler_to_data(self.train_sampler).to_dict('records')
        self.dev = self._sampler_to_data(self.dev_sampler).to_dict('records')
        self.test_in = self._sampler_to_data(self.test_in_sampler).to_dict('records')
        self.test_out = self._sampler_to_data(self.test_out_sampler).to_dict('records')
        self.test_sets = {'iv':self.test_in, 'oov':self.test_out}


    def _sampler_to_data(self, sampler):
        examples = pd.DataFrame(sampler.examples, columns=['example','sample_id', 'def_id'])
        example_pairs = examples.merge(examples, on='sample_id')
        example_pairs = example_pairs.loc[(example_pairs.example_x != example_pairs.example_y)]
        example_pairs['example_union'] = example_pairs.apply(lambda row: set(row.example_x[0] + row.example_y[0]), axis=1)
        example_pairs.drop_duplicates('example_union', inplace=True)
        example_pairs['target'] = example_pairs.apply(lambda row: row.def_id_x==row.def_id_y, axis=1)
        example_pairs = example_pairs[['example_x','example_y', 'target']]
        return example_pairs

    def _get_prompts(self):
        if self.method == 'zero_shot_wic':
            return zero_shot_wic_system, zero_shot_wic_user
        assert self.method in METHODS['word-in-context'], f"Prompt should be one of {METHODS['word-in-context']}"
    

    def get_messages(self, sample, sample_idx, n_shots=None):
        prompt_sys, prompt_usr = self._get_prompts()
        messages = [
            {"role": "system", "content": prompt_sys},
            {"role": "user", "content": prompt_usr.format(
                sample['example_x'][0][sample['example_x'][1].index(True)], 
                sample['example_y'][0][sample['example_y'][1].index(True)], 
                " ".join(sample['example_x'][0]),
                " ".join(sample['example_y'][0])
                )
            },
        ] 
        return messages

    def get_chats(self):
        train_sample_messages = []
        for sample in self.train:
            messages = self.get_messages(sample, None)
            messages.append({'role':'assistant', 'content': 'yes' if sample['target'] else 'no' })
            train_sample_messages.append(messages)
        
        dev_sample_messages = []
        for sample in self.dev:
            messages = self.get_messages(sample, None)
            messages.append({'role':'assistant', 'content': 'yes' if sample['target'] else 'no' })
            dev_sample_messages.append(messages)

        return {"train": {"chat": train_sample_messages}, "dev":{"chat": dev_sample_messages}}

class InferencePromptHandler:
    def __init__(self, method, n_shots):
        self.dev, self.test = inference_load_data()
        self.method = method
        self.icl = None
        self.n_shots = n_shots
        if 'few_shot' in method:
            self.icl = FinetunedXNLIBasedICL(self.dev, self.test)
        self.test_sets = {'test':self.test}
    
    def _get_prompts(self):
        if self.method=='zero_shot_nli_label':
            return zero_shot_nli_label_system, zero_shot_nli_label_user
        elif self.method=='zero_shot_nli_tags':
            return zero_shot_nli_tags_system, zero_shot_nli_label_user
        elif self.method=='few_shot_nli_label':
            return few_shot_nli_label_system + "\n".join([f"{ii}. "+"premise: {}\nhypothesis: {}\nAnswer: entailment" for ii in range(self.n_shots)]), zero_shot_nli_label_user
        else:
            assert self.method in METHODS['inference'], f"Prompt should be one of {METHODS['inference']}"
    

    def get_messages(self, sample, sample_idx):
        prompt_sys, prompt_usr = self._get_prompts()
        if 'zero_shot' in self.method:
            messages = [
                {"role": "system", "content": prompt_sys},
                {"role": "user", "content": prompt_usr.format(sample.premise, sample.hypothesis)},
            ]
        else:
            # few-shot 
            assert self.n_shots is not None, "n_shots should not be none"
            examples = self.icl.get_examples_based_on_finetuned_mnli_xnli(self.n_shots, sample_idx)
            messages = [
                {"role": "system", "content": prompt_sys.format(*([text for example in examples for text in [example.premise, example.hypothesis]]))},
                {"role": "user", "content": prompt_usr.format(sample.premise, sample.hypothesis)},
            ]
        return messages

    def get_chats(self):
        dev_sample_messages = []
        for sample in self.dev:
            messages = self.get_messages(sample, None)
            messages.append({'role':'assistant', 'content': ' '.join([repr(label).lower() if repr(label)!='Unknown' else 'neutral' for label in sample.labels]) })
            dev_sample_messages.append(messages)

        return {"train": {"chat": dev_sample_messages}}

class MetaphorPromptHandler:
    def __init__(self, method, n_shots):
        entries = metaphor_load_file('src/wordsense/dataset.json')
        data = filter_metaphors(entries.entries)
        seed(1312)
        data = sample(data, len(data))
        oov_split = int(len(data) * 0.95)
        iv_entries, oov_entries = data[:oov_split], data[oov_split:]
        iv_examples = [(m, True) for ms, _ in iv_entries for m in ms] + [(n, False) for _, ns in iv_entries for n in ns]
        split1, split2 = int(len(iv_examples) * 0.6), int(len(iv_examples) * 0.8)
        self.train_initial, self.dev, self.test = iv_examples[:split1], iv_examples[split1:split2], iv_examples[split2:]
        self.oov_examples = [(m, True) for ms, _ in oov_entries for m in ms] + [(n, False) for _, ns in oov_entries for n in ns]
        print(len(self.train_initial), len(self.dev), len(self.test), len(self.oov_examples))
        self.train =  self.train_initial + self.dev
        self.method = method
        self.test_sets = {'iv' :self.test, 'oov':self.oov_examples}
        self.n_shots = n_shots
    
    def _get_prompts(self):
        if self.method=='zero_shot_metaphor':
            return zero_shot_metaphor_system, zero_shot_metaphor_user
        elif self.method=='few_shot_metaphor':
            return few_shot_metaphor_system + "\n".join([f"{ii}. "+"sentence: {}\nAnswer: {}" for ii in range(self.n_shots)]), zero_shot_metaphor_user
        else:
            assert self.method in METHODS['metaphor'], f"Prompt should be one of {METHODS['metaphor']}"
    
    def get_messages(self, sample, sample_idx=None, n_shots=None):
        prompt_sys, prompt_usr = self._get_prompts()
        if 'zero_shot' in self.method:
            messages = [
                {"role": "system", "content": prompt_sys},
                {"role": "user", "content": prompt_usr.format(sample[0])},
            ]
        else:
            examples = pd.DataFrame(self.train, columns=['sentence', 'label']).groupby('label').agg(lambda df: df.head(self.n_shots//2)).explode('sentence')
            samples_list = [[example.sentence, 'yes' if example.name else 'no'] for ii, example in examples.iterrows()]
            
            messages = [
                {"role": "system", "content": prompt_sys.format(*([el for sample in samples_list for el in sample]))},
                {"role": "user", "content": prompt_usr.format(sample[0])},
            ]
        
        return messages
    
    def get_chats(self):
        train_sample_messages = []
        for sample in self.train_initial:
            messages = self.get_messages(sample)
            messages.append({'role':'assistant', 'content': 'yes' if sample[1] else 'no'})
            train_sample_messages.append(messages)

        dev_sample_messages = []
        for sample in self.dev:
            messages = self.get_messages(sample)
            messages.append({'role':'assistant', 'content': 'yes' if sample[1] else 'no'})
            dev_sample_messages.append(messages)

        return {"train": {"chat": train_sample_messages}, "dev":{"chat": dev_sample_messages}}


class PromptHandlerSelector:
    def __init__(self, dataset):
        self.dataset = dataset

    def create(self,*args, **kwargs):
        if self.dataset == 'inference':
            return InferencePromptHandler(*args, **kwargs)
        elif self.dataset == 'sense-selection':
            return SenseSelectionPromptHandler(*args, **kwargs)
        elif self.dataset == 'word-in-context':
            return WordInContextPromptHandler(*args, **kwargs)
        elif self.dataset == 'metaphor':
            return MetaphorPromptHandler(*args, **kwargs)
        else:
            assert 1==0