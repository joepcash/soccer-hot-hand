import argparse
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt

from shots import Shots


def process_shots():
    shots = Shots().load_shots().load_matches().find_goals().calc_shots_since_last_goal()
    shots.save_shots_to_file()


def plot_hot_hand():
    shots = pd.read_csv("data/shots.csv")
    total_shots = shots[["shots_since_goal", "goal"]].groupby(by=["shots_since_goal"]).count()
    total_goals = shots[["shots_since_goal", "goal"]].groupby(by=["shots_since_goal"]).sum()
    percent_goals = 100 * total_goals/total_shots
    percent_goals["Shots since last goal"] = percent_goals.index.astype(int)
    percent_goals = percent_goals.rename(columns={"goal": "% scored"})

    font = {'weight': 'normal', 'size': 15}
    matplotlib.rc('font', **font)
    sns.barplot(percent_goals.loc[total_shots["goal"] > 100], x="Shots since last goal", y="% scored", width=1.0,
                errorbar="sd", color="red")
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', type=str, dest='operation', help="The operation you want to run",
                        choices=[
                            "process-shots",
                            "plot-hot-hand"
                        ])
    args = parser.parse_args()

    if args.operation == 'process-shots':
        process_shots()
    elif args.operation == "plot-hot-hand":
        plot_hot_hand()
