import os
import glob
import json
import pandas
import matplotlib.pyplot as plt
import seaborn as sns

fname = "./stats/fuckup-1-meta.csv"
record = pandas.read_csv(fname)

def plotConfidenceAgainstMutation():
    sns.set()
    ax = sns.scatterplot(x="confidence", y="mutation",
                         hue="classname", size=20,
                         data=record, legend=False)
    plt.savefig("confidence_vs_mutation.pdf")

plotConfidenceAgainstMutation()
