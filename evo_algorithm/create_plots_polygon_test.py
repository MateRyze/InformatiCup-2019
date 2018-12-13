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

def plotMutationAgainstClassnames():
    sns.set()
    ax = sns.scatterplot(x="mutation", y="classname",
                         hue="classname", size="confidence", sizes=(10, 100),
                         data=record, legend=False)
    plt.savefig("mutation_vs_classnames.pdf")

def plotMutationAgainstEdges():
    sns.set()
    ax = sns.scatterplot(x="mutation", y="edges",
                         hue="classname", size="confidence", sizes=(10, 100),
                         data=record, legend=False)
    plt.show()

def plotEdgeCountAgainstClassnames():
    sns.set()
    ax = sns.scatterplot(x="edges", y="classname",
                         hue="classname", size="confidence", sizes=(10, 100),
                         data=record, legend=False)
    plt.savefig("edgecount_vs_classnames.pdf")


#plotConfidenceAgainstMutation()
#plotMutationAgainstClassnames()
plotMutationAgainstEdges()
#plotEdgeCountAgainstClassnames()
