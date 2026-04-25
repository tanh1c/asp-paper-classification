import pandas as pd


df = pd.read_csv("Stage_1_publcitrain_with_abstract_plus_verified_test.csv")

print(df["Label"].sum())

