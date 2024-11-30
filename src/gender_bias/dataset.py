import pandas as pd

df = pd.read_csv('src/gender_bias/premises.csv')
df['order']=df['sentid'].str.contains('1').astype(int)
df['noun'] = df['sentid'].apply(lambda x: x.split('.')[int(x.split('.')[2])])
