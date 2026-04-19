import pandas as pd


df = pd.read_csv("Stage_1_publcitrain_with_abstract_only (1).csv")

print(df["abstract"].isna().sum())

