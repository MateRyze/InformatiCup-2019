import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def plot():
    path = "results_contrast_color.csv"
    df = pd.read_csv(path)
    print(df)
    plt.title('Einfarbige Bilder')
    plt.xlabel('Konfidenz')
    plt.ylabel('Kontrast')
    plt.scatter(df["confidence"], df["contrast"])
    plt.show()


if __name__ == '__main__':
    plot()
