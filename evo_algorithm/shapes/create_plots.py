import os
import glob
import json
import pandas
import matplotlib.pyplot as plt
import seaborn as sns

recordFilenames = glob.glob(os.path.join("stats", "*-meta.csv"))
records = []

for fname in recordFilenames:
    record = pandas.read_csv(fname)
    metadata = [
        json.loads(record["metadata"][i].replace("'", "\"")) for i in range(len(record))
    ]
    polygon_count = [
        len(x["polygons"]) for x in metadata
    ]
    record["polygon_count"] = polygon_count
    records.append(record)

df = pandas.concat(records)

def plotConfidenceAgainstPolygonCount():
    sns.set()
    ax = sns.scatterplot(x="confidence", y="polygon_count",
                         hue="classname", size=20,
                         data=df, legend=False)
    plt.savefig("confidence-polycount.pdf")

def plotBackgroundsAgainstClassnames():
    sns.set()
    ax = sns.scatterplot(x="polygon_count", y="classname",
                         hue="classname", size="confidence", sizes=(10, 100),
                         data=df, legend=False)
    plt.show()
    plt.savefig("backgrounds-classnames.pdf")

plotConfidenceAgainstPolygonCount()
plotBackgroundsAgainstClassnames()
