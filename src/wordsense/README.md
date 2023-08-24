## Word-Sense Disambiguation

The data are contained in json format within `dataset.json`.
Each sample contains a lemma and a list of senses, each sense being in turn a periphrastic definition and a list of example phrases.

### Python Interface
To load and process the data in python, set your working directory to match the `src` folder of this repository.

To load the dataset:
```python
from wordsense.dataset import Dataset
from json import load

with open('./wordsense/dataset.json', 'r') as f:
    dataset = Dataset.from_json(load(f))
```

To visually inspect individual samples:
```pycon
>>> from pprint import pprint
>>> pprint(dataset.entries[42])
Entry(lemma='ακτίνα',
      senses=[Sense(definition='κάθε νοητή ή πραγματική ευθεία γραμμή που '
                               'ξεκινά από ένα κέντρο με κατεύθυνση προς '
                               'οποιοδήποτε σημείο γύρω από αυτό',
                    examples=['Ακτίνα δράσης, η μέγιστη απόσταση που μπορεί να '
                              'καλύψει ένα αεροσκάφος χωρίς ανεφοδιασμό, και '
                              'μτφ. ο τομέας δραστηριότητας κάποιου.']),
              Sense(definition='(μαθημ.) το ευθύγραμμο τμήμα που συνδέει το '
                               'κέντρο κύκλου (ή σφαίρας) με οποιοδήποτε '
                               'σημείο της περιφέρειάς του (ή της επιφάνειάς '
                               'της)',
                    examples=['Η ακτίνα του κύκλου ισούται με το μισό της '
                              'διαμέτρου του.']),
              Sense(definition='καθεμία από τις ίδιου μήκους ράβδους, που '
                               'συνδέουν τον άξονα ενός τροχού με τη στεφάνη '
                               'του',
                    examples=['Οι ακτίνες (της ρόδας) του ποδηλάτου.']),
              Sense(definition='γραμμή φωτός που εκπέμπεται από φωτοβόλο σώμα',
                    examples=['Μια ακτίνα φωτός.',
                               'Δέσμη φωτεινών ακτίνων.', 
                               'Οι ακτίνες του ήλιου.']),
              Sense(definition='(επέκτ.) η ίδια η ακτινοβολία',
                    examples=['Υπεριώδεις / υπέρυθρες ακτίνες.',
                              'Ακτίνες Χ / α / β / γ.'])])
>>> pprint(dataset.samples[1312])
Entry(lemma='περικόπτω',
      senses=[Sense(definition='αφαιρώ μέρος ή τμήμα (συνήθ. κάπως αυθαίρετα '
                               'και για να κάνω κτ. μικρότερο)',
                    examples=['Διαμαρτυρήθηκε, γιατί περιέκοψαν από το κείμενό '
                              'του μια ολόκληρη παράγραφο.',
                              'Του ζήτησαν να περικόψει το κείμενό του.']),
              Sense(definition='(ειδικότ.) μειώνω, ελαττώνω χρηματικό ποσό ή '
                               'αφαιρώ από αυτό ένα μέρος',
                    examples=['Τους περιέκοψαν το μισθό κατά 10%.',
                              'Τους περιέκοψαν το 10% του μισθού.',
                              'Αποφάσισαν να περικόψουν τις δαπάνες.'])])
```

Use standard python queries to isolate entries of interest.