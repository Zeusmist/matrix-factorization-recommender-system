import pandas as pd


def create_interaction_matrix():
    # Load data
    mood_action_stats_df = pd.read_csv("data_files/moodactionstats.csv")

    # Assign weights to each type of interaction as per their importance
    weights = {"like": 1, "comment": 2, "share": 3, "gift": 4}

    # Calculate weighted rating for each interaction
    mood_action_stats_df["weighted_rating"] = mood_action_stats_df.apply(
        lambda x: weights.get(x["type"], 0) * x["times"], axis=1
    )

    # Aggregate the weighted ratings for each user-item pair
    interaction_data = (
        mood_action_stats_df.groupby(["from", "userMoodId"])
        .sum()["weighted_rating"]
        .reset_index()
    )

    # Rename columns to match the expected format for LightFM
    interaction_data.rename(
        columns={"from": "userId", "userMoodId": "itemId", "weighted_rating": "rating"},
        inplace=True,
    )

    # Save the transformed data
    interaction_data.to_csv("data_files/user_item_rating.csv", index=False)
