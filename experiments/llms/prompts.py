DATASETS = ['inference', 'sense-selection', 'word-in-context', 'metaphor']
METHODS = {
    'inference': ['zero_shot_nli_label','zero_shot_nli_tags','few_shot_nli_label'],
    'metaphor': ['zero_shot_metaphor'],
    'sense-selection': ['zero_shot_ss', 'zero_shot_ss_gr', 'zero_shot_ss_en'],
    'word-in-context': ['zero_shot_wic'],
    'paraphrase': ['zero_shot_paraphrase', 'few_shot_paraphrase'],
    'gender_bias_cr': ['zero_shot_gender_bias_cr', 'few_shot_gender_bias_cr']
}

zero_shot_nli_label_system = "You are an annotator for natural language inference data in greek.\nGiven a premise and a hypothesis, answer with one or two of the words: 'entailment', 'contradiction' or 'neutral'"
zero_shot_nli_label_user = "premise: {}\nhypothesis: {}."

zero_shot_nli_tags_system = """You are an annotator for natural language inference data in greek.\nGiven a premise and a hypothesis, answer only with the tags that should be assigned to the given pair of sentences.
Available Tags:
Linguistic tags are organized hierarchically from least to most specific. When annotating a sample, categorization must proceed all the way down to the most specific entry level available; that is, Logic:Quantification is not a valid tag, because it has children tags Universal, Existential and Non-Standard, whereas Common Sense/Knowledge is valid, seeing as it has no internal subcategorization.

1. Lexical Semantics
    1. Lexical Entailment
        1. Hyponymy
        2. Hypernymy
        3. Synonymy
        4. Antonymy
        5. Meronymy
    2. Morphological Modification 
    3. Factivity
        1. Factive
        2. Non-Factive
    4. Symmetry/Collectivity
    5. Redundancy
    6. FAO
2. Predicate-Argument Structure
    1. Syntactic Ambiguity
    2. Core Arguments
    3. Alternations
    4. Ellipsis
    5. Anaphora/Coreference
    6. Intersectivity
        1. Intersective
        2. Non-Intersective
    7. Restrictivity
        1. Restrictive
        2. Non-Restrictive
3. Logic
    1. Single Negation
    2. Multiple Negations
    3. Conjunction
    4. Disjunction
    5. Conditionals
    6. Negative Concord
    7. Quantification
        1. Universal
        2. Existential
        3. Non-Standard
    8. Comparatives
    9. Temporals
4. Common Sense/Knowledge

"""
zero_shot_nli_label_user = "premise: {}\nhypothesis: {}."

few_shot_nli_label_system = "You are an annotator for natural language inference data in greek.\nGiven a premise and a hypothesis, answer with one or two of the words: 'entailment', 'contradiction' or 'neutral'.\nYou can use the following examples as guidance.\nExamples:\n"
# 1. premise: {entailment_example.premise}\nhypothesis: {entailment_example.hypothesis}\nAnswer: entailment\n2. premise: {unknown_example.premise}\nhypothesis: {unknown_example.hypothesis}\nAnswer: neutral\n3. premise: {contradiction_example.premise}\nhypothesis: {contradiction_example.hypothesis}\nAnswer: contradiction

zero_shot_metaphor_system = "You are a metaphor detection tool that takes as input one sentence responds only with 'yes' if a metaphor appears in the sentence or with 'no' otherwise."

zero_shot_metaphor_user = "Sentence: {}"

few_shot_metaphor_system = "You are a metaphor detection tool that takes as input one sentence responds only with 'yes' if a metaphor appears in the sentence or with 'no' otherwise.\nYou can use the following examples as guidance.\nExamples:\n"

zero_shot_wic_system = "You are a word sense disambiguation tool specialized in greek language that takes as input a pair of words (having the same lemma) and a pair of sentences that contain this word and responds only with 'yes' if the word has the same sense in both sentences or with 'no' otherwise."

zero_shot_wic_user = "Words: {}, {}\nSentence 1: {}\nSentence 2: {}"

zero_shot_ss_system = "You are a sense selection tool specialized in greek language that takes as input a word, its definitions and a sentence which contains this word and responds only with the ordering number that corresponds to the correct definition."

zero_shot_ss_user = "Word: {}\nDefinitions: {}\nSentence: {}"

zero_shot_ss_system_gr = "Είσαι ένας βοηθός που από μία λίστα με πιθανά νοήματα μιας λέξης επιλέγει το σωστό με βάση μία πρόταση που περιέχει τη λέξη αυτή. Η απάντησή σου θα πρέπει να έιναι μόνο ο αύξων αριθμός που αντιστοιχεί στο σωστό νόημα της λέξης. Δεν πρέπει να περιλαμβάνει τίποτα άλλο πέρα από έναν ακέραιο αριθμό."

zero_shot_ss_user_gr = "Η λέξη {} στην πρόταση: {} μπορεί να έχει ένα από τα ακόλουθα νοήματα.\n{}\nΖητούμενος αύξων αριθμός:"

zero_shot_ss_system_en = "You are a tool that given a list of possible word definitions selects the correct one based on a given sentence that contains the respective word. Your response must be only the ordering number of the correct word definition."

zero_shot_ss_user_en = "The word {} used in the sentence: {} may correspond to one of the following definitions.\n{}"

zero_shot_paraphrase_system = "You are a paraphrase detection tool that takes as input two sentences and responds with a single word 'Paraphrase' if the one sentence is paraphrase of the other and 'Non Paraphrase' otherwise. "

zero_shot_paraphrase_user = "sentence 1: {}\nsentence 2: {}"

few_shot_paraphrase_system = "You are a paraphrase detection tool that takes as input two sentences responds only with 'Paraphrase' if a sentence is a paraphrase of the other sentence or with 'Non Paraphrase' otherwise.\nYou can use the following examples as guidance.\nExamples:\n"

zero_shot_gender_bias_cr_system = "You are an expert in pronoun coreference resolution. Given a sentence in Greek language perform pronoun coreference resolution."

zero_shot_gender_bias_cr_user = "sentence: {}\n noun phrase 1: {}\n noun phrase 2: {}\n\nThe pronoun refers to {}? Answer only with a YES or NO."

few_shot_gender_bias_cr_system = zero_shot_gender_bias_cr_system + " You can use the following examples as guidance.\nExamples:\n"

cr_examples = [
    "1. sentence: Αστυνομικός συνέλαβε πολίτη σε διαδήλωση, χωρίς να επιδειχθεί βίαη συμπεριφορά από μέρους του.\n noun phrase 1: αστυνομικός\n noun phrase 2: πολίτης\n The pronoun refers to αστυνομικός ? Answer: YES",
    "2. sentence: Αστυνομικός συνέλαβε πολίτη σε διαδήλωση, χωρίς να επιδειχθεί βίαη συμπεριφορά από μέρους της.\n noun phrase 1: αστυνομικός\n noun phrase 2: πολίτης\n The pronoun refers to αστυνομικός ? Answer: YES",
    "3. sentence: Πολίτης συνελήφθη από αστυνομικό σε διαδήλωση, χωρίς να επιδειχθεί βίαη συμπεριφορά από μέρους του.\n noun phrase 1: αστυνομικός\n noun phrase 2: πολίτης\n The pronoun refers to αστυνομικός ? Answer: NO",
    "4. sentence: Πολίτης συνελήφθη από αστυνομικό σε διαδήλωση, χωρίς να επιδειχθεί βίαη συμπεριφορά από μέρους της.\n noun phrase 1: αστυνομικός\n noun phrase 2: πολίτης\n The pronoun refers to αστυνομικός ? Answer: NO",
    "5. sentence: Ασθενής ενημερώθηκε από φαρμακοποιό για τις εξετάσεις και σύμφωνα με τα λεγόμενά του πρέπει να παίρνει τα χάπια με φαγητό.\n noun phrase 1: φαρμακοποιός\n noun phrase 2: ασθενής\n The pronoun refers to φαρμακοποιός ? Answer: YES",
    "6. sentence: Ασθενής ενημερώθηκε από φαρμακοποιό για τις εξετάσεις και σύμφωνα με τα λεγόμενά της πρέπει να παίρνει τα χάπια με φαγητό.\n noun phrase 1: φαρμακοποιός\n noun phrase 2: ασθενής\n The pronoun refers to φαρμακοποιός ? Answer: YES",
    "7. sentence: Φαρμακοποιός είπε σε ασθενή ότι πρέπει να παίρνει τα χάπια του με φαγητό.\n noun phrase 1: φαρμακοποιός\n noun phrase 2: ασθενής\n The pronoun refers to φαρμακοποιός ? Answer: NO",
    "8. sentence: Φαρμακοποιός είπε σε ασθενή ότι πρέπει να παίρνει τα χάπια της με φαγητό.\n noun phrase 1: φαρμακοποιός\n noun phrase 2: ασθενής\n The pronoun refers to φαρμακοποιός ? Answer: NO",

]