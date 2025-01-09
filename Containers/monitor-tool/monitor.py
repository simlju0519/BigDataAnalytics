import os
from pymongo import MongoClient

import time
import json

from save_data_to_excel import main as save_data_to_excel

print("Starting monitoring tool...", flush=True)


# Fetch database host and port from environment variables
db_host = os.getenv("DB_HOST", "localhost")  # Default to 'localhost' if not set
db_port = os.getenv("DB_PORT", "27017")     # Default to '27017' if not set
# Build the connection string
connection_string = f"mongodb://{db_host}:{db_port}"
# Connect to MongoDB
client = MongoClient(connection_string)
db = client.get_database(os.getenv("DB_NAME", "cloneDetector"))  # Default DB name

print("Connected to the database.", flush=True)

def main():
    # Example query
    print("Connected to the database. Monitoring...", flush=True)

    all_status_updates = []
    number_of_files_lst = [0]
    number_of_files_velocity_lst = [0]

    number_of_chunks_lst = [0]
    number_of_chunks_velocity_lst = [0]

    number_of_candidates_lst = [0]
    number_of_candidates_velocity_lst = [0]

    number_of_clones_lst = [0]
    number_of_clones_velocity_lst = [0]

    check_timestamps = []

    while True:
        print("\n\n\n")
        
        incoming_status_updates = list(db.statusUpdates.find())
        
        old_number_of_files = number_of_files_lst[-1]
        number_of_files_lst.append(db.files.count_documents({}))
        number_of_files_velocity_lst.append(number_of_files_lst[-1] - old_number_of_files)

        old_number_of_chunks = number_of_chunks_lst[-1]
        number_of_chunks_lst.append(db.chunks.count_documents({}))
        number_of_chunks_velocity_lst.append(number_of_chunks_lst[-1] - old_number_of_chunks)

        old_number_of_candidates = number_of_candidates_lst[-1]
        number_of_candidates_lst.append(db.candidates.count_documents({}))
        number_of_candidates_velocity_lst.append(number_of_candidates_lst[-1] - old_number_of_candidates)
        

        old_number_of_clones = number_of_clones_lst[-1]
        number_of_clones_lst.append(db.clones.count_documents({}))
        number_of_clones_velocity_lst.append(number_of_clones_lst[-1] - old_number_of_clones)


        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", flush=True)
        print("STATUS UPDATE SUMMARY for time: ", time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + f"{time.time() % 1:.9f}"[1:], flush=True)
        check_timestamps.append(time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + f"{time.time() % 1:.9f}"[1:])

        print("--------------------------------------------\n", flush=True)
        print(f"Number of files: {number_of_files_lst[-1]}, Velocity: {number_of_files_velocity_lst[-1]}", flush=True)
        print(f"Number of chunks: {number_of_chunks_lst[-1]}, Velocity: {number_of_chunks_velocity_lst[-1]}", flush=True)
        print(f"Number of candidates: {number_of_candidates_lst[-1]}, Velocity: {number_of_candidates_velocity_lst[-1]}", flush=True)
        print(f"Number of clones: {number_of_clones_lst[-1]}, Velocity: {number_of_clones_velocity_lst[-1]}", flush=True)

        new_status_updates = []
        for update in incoming_status_updates:
            if update not in all_status_updates:
                new_status_updates.append(update)
                all_status_updates.append(update)

        print("\n--------------------------------------------\n", flush=True)
        print("STATUS UPDATES\n", flush=True)
        for update in all_status_updates:
            print(f"{update['timestamp']} - {update['message']}", flush=True)
        
        if new_status_updates:
            print("\n--------------------------------------------\n", flush=True)

            print("NEW STATUS UPDATES\n", flush=True)

            for update in new_status_updates:
                print(f"{update['timestamp']} - {update['message']}", flush=True)
        
        last_update = new_status_updates[-1]['message'] if new_status_updates else ""

        if "stop-monitoring" in last_update:
            print("Stopping monitoring...", flush=True)
            break
            
        time.sleep(5)

    
    print("Monitoring stopped.", flush=True)

    print("Preparting export of statistics to json file...", flush=True)
    
    export_json = {}


    export_json["files"] = {
        "amount": number_of_files_lst[1:],
        "velocity": number_of_files_velocity_lst[1:]
    }

    export_json["chunks"] = {
        "amount": number_of_chunks_lst[1:],
        "velocity": number_of_chunks_velocity_lst[1:]
    }

    export_json["candidates"] = {
        "amount": number_of_candidates_lst[1:],
        "velocity": number_of_candidates_velocity_lst[1:]
    }

    export_json["clones"] = {
        "amount": number_of_clones_lst[1:],
        "velocity": number_of_clones_velocity_lst[1:]
    }


    export_json["timestamps"] = check_timestamps

    prepared_status_updates = []
    for update in all_status_updates:
        prepared_status_updates.append({
            "timestamp": update["timestamp"],
            "message": update["message"]
        })

    export_json["status_updates"] = prepared_status_updates

    # clear the file
    open("statistics.json", "w").close()

    with open("statistics.json", "w") as f:
        json.dump(export_json, f, indent=4)

    print("Exported statistics to json file.", flush=True)


    print("Exporting to a excel file...", flush=True)
    save_data_to_excel()
    print("Exported to excel file.", flush=True)

if "__main__" == __name__:
    time.sleep(2)
    main()