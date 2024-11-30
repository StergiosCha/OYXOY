import pandas as pd 
import numpy as np
import spacy

def load_premises():
    df = pd.read_csv('src/gender_bias/premises.csv')
    df['order']=df['sentid'].str.contains('1').astype(int)
    df['np_0'] = df['sentid'].apply(lambda x: x.split('.')[0])
    df['np_1'] = df['sentid'].apply(lambda x: x.split('.')[1])

    df['nouns'] = df['sentid'].apply(lambda x: " ".join(x.split('.')[:2]))
    df['nouns_shift'] = df['nouns'].shift(1)
    df['group'] = ((df['nouns_shift'] == df['nouns'])==False)*range(len(df))
    df['group'] = df['group'].replace(0,np.nan).bfill().fillna(0)

    nlp = spacy.load("el_core_news_lg")
    df['pronoun'] = df['sentence'].apply(lambda x: [token.text for token in nlp(x) if token.pos_=='PRON'])
    return df[df.columns.difference(['nouns','nouns_shift'])]