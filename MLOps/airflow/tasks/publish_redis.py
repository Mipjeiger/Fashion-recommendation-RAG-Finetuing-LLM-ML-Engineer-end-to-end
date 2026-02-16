import redis
import pandas as pd
from pathlib import Path

def publish_features_to_redis(process_date: str):
    try:
        path = Path(f"/tmp/online_features/dt={process_date}")
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(f"Error creating directory: {e}")
                return
            
    except Exception as e:
        print(f"Error checking directory: {e}")
        return
    
    df = pd.read_parquet(path=path)
    r = redis.Redis(host="redis", port=6379, decode_responses=True)
    
    # Iterate through the DataFrame and publish each row as a Redis hash
    for row in df.itertuples(index=False):
        r.hset(
            f"item:{row.item_id}",
            mapping={
                "view_count": row.view_count,
                "dt": process_date
            }
        )