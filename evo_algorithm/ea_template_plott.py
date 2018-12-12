import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# TODO
def plot():
    path = "ea_aspect_colors/results/results_uni_color.csv"
    df = pd.read_csv(path)
    print(df)
    plt.title('Einfarbige Bilder')
    plt.xlabel('Konfidenz')
    plt.ylabel('Klassifikation')
    plt.scatter(df["confidence"], df["class"])
    plt.show()


if __name__ == '__main__':
    plot()

