from notifications.slack_service import slack
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder

def notify_weekly_learning_from_df(df: pd.DataFrame, week: str = None):
    """Mine association rules from dataframe and notify to Slack."""

    # Build transactions: what items are bought together per subcategory
    transactions = (
        df[df["purchase_count"] > 0]
        .groupby("item_id")["subcategory"]
        .apply(list)
        .tolist()
    )

    te = TransactionEncoder()
    te_arr = te.fit(transactions).transform(transactions)
    df_enc = pd.DataFrame(te_arr, columns=te.columns_)

    freq_items = apriori(df_enc, min_support=0.01, use_colnames=True)
    rules = association_rules(freq_items, metric="confidence", min_threshold=0.5)
    rules = rules.sort_values(by="confidence", ascending=False).head(5)

    learnings = []
    for _, rule in rules.iterrows():
        antecedent = ",".join(list(rule["antecedents"]))
        consequent = ",".join(list(rule["consequents"]))

        # Get a sample item for context
        sample = df[df["subcategory"] == antecedent].iloc[0] if antecedent in df["subcategory"].values else None

        learnings.append({
            "insight": f"Users who bought {antecedent} also tend to buy {consequent}",
            "item_id": sample["item_id"] if sample is not None else "N/A",
            "category": sample["category"] if sample is not None else "N/A",
            "subcategory": antecedent,
            "brand": sample["brand"] if sample is not None else "N/A",
            "support": f"{rule['support']*100:.1f}%",
            "confidence": f"{rule['confidence']*100:.1f}%"
        })

    # Notify to Slack
    slack.notify_weekly_learnings(learnings=learnings, week=week)