import json
import pandas as pd
from datetime import datetime

def main():
    print("Importing from statistics.json...", flush=True)

    # Load the JSON file
    with open("statistics.json", "r") as file:
        statistics = json.load(file)

    print("Statistics imported.", flush=True)

    # Prepare timestamps and calculate time differences
    timestamps = statistics.get("timestamps", [])
    start_time = datetime.fromisoformat(timestamps[0]) if timestamps else None

    # Calculate elapsed time in seconds
    elapsed_time = []
    if start_time:
        for ts in timestamps:
            current_time = datetime.fromisoformat(ts)
            elapsed_time.append((current_time - start_time).total_seconds())

    # Create DataFrames for each category
    dataframes = {}
    for category, data in statistics.items():
        if category in ["timestamps", "status_updates"]:
            continue  # Skip global timestamps and status updates

        if isinstance(data, dict):
            # Extract amount and velocity
            amount = data.get("amount", [])
            velocity = data.get("velocity", [])
            
            # Ensure all arrays are the same length
            max_len = max(len(amount), len(velocity), len(timestamps))
            amount += [None] * (max_len - len(amount))
            velocity += [None] * (max_len - len(velocity))
            elapsed_time += [None] * (max_len - len(elapsed_time))
            
            # Create a DataFrame
            df = pd.DataFrame({
                "amount": amount,
                "velocity": velocity,
                "elapsed_time_seconds": elapsed_time
            })
            dataframes[category] = df

    # Export each DataFrame to a separate sheet in an Excel file
    print("Exporting to statistics.xlsx...", flush=True)
    with pd.ExcelWriter("statistics.xlsx") as writer:
        for category, df in dataframes.items():
            df.to_excel(writer, sheet_name=category, index=False)

    print("Exported to statistics.xlsx", flush=True)



if "__main__" == __name__:
    main()