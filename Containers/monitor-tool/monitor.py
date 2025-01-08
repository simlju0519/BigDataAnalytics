import os
from pymongo import MongoClient
import time


def main():
    # Fetch database host and port from environment variables
    db_host = os.getenv("DB_HOST", "localhost")  # Default to 'localhost' if not set
    db_port = os.getenv("DB_PORT", "27017")     # Default to '27017' if not set

    # Build the connection string
    connection_string = f"mongodb://{db_host}:{db_port}"

    # Connect to MongoDB
    client = MongoClient(connection_string)
    db = client.get_database(os.getenv("DB_NAME", "cloneDetector"))  # Default DB name

    print("Connected to the database. Monitoring...")

    all_status_updates = []
    number_of_files = 0
    number_of_files_velocity_lst = [0]

    number_of_chunks = 0
    number_of_chunks_velocity_lst = [0]

    number_of_candidates = 0
    number_of_candidates_velocity_lst = [0]

    number_of_clones = 0
    number_of_clones_velocity_lst = [0]

    try:
        while True:
            print("\n\n\n")

            incoming_status_updates = list(db.statusUpdates.find())

            old_number_of_files = number_of_files
            number_of_files = db.files.count_documents({})
            number_of_files_velocity_lst.append(number_of_files - old_number_of_files)

            old_number_of_chunks = number_of_chunks
            number_of_chunks = db.chunks.count_documents({})
            number_of_chunks_velocity_lst.append(number_of_chunks - old_number_of_chunks)

            old_number_of_candidates = number_of_candidates
            number_of_candidates = db.candidates.count_documents({})
            number_of_candidates_velocity_lst.append(number_of_candidates - old_number_of_candidates)

            old_number_of_clones = number_of_clones
            number_of_clones = db.clones.count_documents({})
            number_of_clones_velocity_lst.append(number_of_clones - old_number_of_clones)

            print("@@@@@@@@@@@@@@@@@@@")
            print("STATUS UPDATE SUMMARY")
            print("----------------------\n")
            print(f"Number of files: {number_of_files}, Velocity: {number_of_files_velocity_lst[-1]}")
            print(f"Number of chunks: {number_of_chunks}, Velocity: {number_of_chunks_velocity_lst[-1]}")
            print(f"Number of candidates: {number_of_candidates}, Velocity: {number_of_candidates_velocity_lst[-1]}")
            print(f"Number of clones: {number_of_clones}, Velocity: {number_of_clones_velocity_lst[-1]}")

            new_status_updates = []
            for update in incoming_status_updates:
                if update not in all_status_updates:
                    new_status_updates.append(update)
                    all_status_updates.append(update)

            print("\n----------------------\n")
            print("STATUS UPDATES\n")
            if not new_status_updates:
                print("No new updates")
            else:
                for update in new_status_updates:
                    print(f"{update['timestamp']} - {update['message']}")

            time.sleep(2)
    except KeyboardInterrupt:
        print("\nExiting monitoring loop...")
        # Add any cleanup or end sequence here if needed
        print("Final statistics:")
        print(f"Total files processed: {number_of_files}")
        print(f"Total chunks processed: {number_of_chunks}")
        print(f"Total candidates processed: {number_of_candidates}")
        print(f"Total clones processed: {number_of_clones}")


if __name__ == "__main__":
    print("Starting the monitor tool...")
    main()
