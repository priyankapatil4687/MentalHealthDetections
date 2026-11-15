import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns


def save_stacked_bar(pct_df, title, path, xlabel, ylabel="Share of posts (%)"):
    ax = pct_df.plot(kind="bar", stacked=True, figsize=(8, 5), colormap="viridis")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.legend(title="Label", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def save_heatmap(df, title, path, fmt=".0f", cmap="YlOrRd", xlabel="", ylabel="", annot=None):
    plt.figure(figsize=(8, 5))
    ax = sns.heatmap(df, annot=df if annot is None else annot, fmt=fmt, cmap=cmap, cbar=True)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
