import json 
import pandas as pd 

def load_data():
    with open('src/nli/paraphrase.json', 'rb') as f:
        data = json.load(f)
        return pd.DataFrame.from_dict(data)