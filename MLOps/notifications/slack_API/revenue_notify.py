from notifications.slack_service import slack
import pandas as pd

def notify_daily_revenue_from_df(df: pd.DataFrame):
    """
    Compute revenue metrics from dataframe and notify to Slack."""
    total_revenue = int((df["price"]) * df["purchase_count"]).sum()
    total_orders = int(df["purchase_count"].sum())

    top_items = (
        df.assign(revenue=df["price"] * df["purchase_count"])
        .sort_values(by="revenue", ascending=False)
        .head(5)
        [["item_id", "subcategory", "brand", "revenue"]]
        .to_dict(orient="records")
    )

    slack.notify_daily_revenue(
        total_revenue=total_revenue,
        total_orders=total_orders,
        top_items=top_items
    )

    def notify_weekly_revenue_from_df(df: pd.DataFrame, week: str = None):
        """
        Compute weekly revenue metrics from dataframe and notify to Slack."""
        total_revenue = int((df["price"]) * df["purchase_count"]).sum()
        total_orders = int(df["purchase_count"].sum())

        top_items = (
            df.assign(revenue=df["price"] * df["purchase_count"])
            .sort_values(by="revenue", ascending=False)
            .head(5)
            [["item_id", "subcategory", "brand", "revenue"]]
            .to_dict(orient="records")
        )

        slack.notify_weekly_revenue(
            week=week,
            total_revenue=total_revenue,
            total_orders=total_orders,
            top_items=top_items
        )