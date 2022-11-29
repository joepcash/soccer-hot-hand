import pandas as pd
import os
import numpy as np
import ast


class Shots:

    def __init__(self):
        self.shots = pd.DataFrame(columns=["tags", "playerId", "matchId", "eventSec"])

    def load_shots(self):
        for file in os.listdir("data/"):
            if file.startswith("events_"):
                new_shots = pd.read_csv("data/" + file).loc[:, ["tags", "playerId", "matchId", "eventName", "eventSec"]]
                new_shots = new_shots.loc[new_shots["eventName"] == "Shot"].drop(columns=["eventName"])
                self.shots = pd.concat([self.shots, new_shots])

        return self

    def load_matches(self):
        if self.shots.empty:
            raise Exception("Shots dataframe must not be empty.")

        matches = pd.DataFrame(columns=["dateutc", "duration", "wyId"])
        for file in os.listdir("data/"):
            if file.startswith("matches_"):
                new_matches = pd.read_csv("data/" + file).loc[:, ["dateutc", "duration", "wyId"]]
                matches = pd.concat([matches, new_matches])

        self.shots = self.shots.merge(matches, how="left", left_on="matchId", right_on="wyId")
        self.shots = self.shots.sort_values(by=["dateutc", "eventSec"]).reset_index()

        return self

    def find_goals(self):
        self.shots["goal"] = self.shots["tags"].apply(lambda l: any([d["id"] == 101 for d in ast.literal_eval(l)]))

        return self

    def calc_shots_since_last_goal(self):
        self.shots["shots_since_goal"] = np.nan
        players = self.shots["playerId"].unique()

        for player in players:
            players_shots = self.shots[self.shots["playerId"] == player]
            idxs_before_first_goal = \
                players_shots[players_shots.where(players_shots["goal"]).ffill().isnull()]["playerId"].dropna().index
            self.shots = self.shots.drop(index=idxs_before_first_goal)
            players_shots = players_shots.drop(index=idxs_before_first_goal)

            if players_shots.empty:
                continue

            cs = (~players_shots["goal"]).cumsum()
            players_shots["shots_since_goal"] = cs - cs.where(players_shots["goal"]).ffill().fillna(1).astype(int)
            players_shots["shots_since_goal"] = players_shots["shots_since_goal"].shift(1)
            self.shots = self.shots.drop(index=players_shots.index[0])
            players_shots = players_shots.drop(index=players_shots.index[0])

            self.shots.loc[self.shots["playerId"] == player, "shots_since_goal"] = players_shots["shots_since_goal"]

        return self

    def save_shots_to_file(self):
        self.shots.to_csv("data/shots.csv", index=False)