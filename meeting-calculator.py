import csv
from datetime import datetime, timedelta
import os.path
import pandas as pd

MEETING_DATA_FILE = "meeting_data.csv"

def is_valid_time(time_str):
    try:
        datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False

def add_meeting():
    current_date = datetime.now().date()
    date_str = current_date.strftime("%Y-%m-%d")

    start_time = input("Enter the start time in 24-hour format (HH:MM): ")
    end_time = input("Enter the end time in 24-hour format (HH:MM): ")

    if not is_valid_time(start_time) or not is_valid_time(end_time):
        print("Invalid time format. Please enter the time in 24-hour format (HH:MM).")
        return

    df = pd.read_csv(MEETING_DATA_FILE)

    if "Date" not in df.columns:
        df["Date"] = ""

    existing_rows = df[(df["Date"] == date_str) & (df["Start Time"] == start_time) & (df["End Time"] == end_time)]
    if not existing_rows.empty:
        print("This meeting session already exists.")
        return

    df["Duration"] = pd.to_datetime(df["End Time"]) - pd.to_datetime(df["Start Time"])
    df["Duration"] = df["Duration"].apply(lambda x: x.total_seconds() / 60)
    df["Duration"] = df["Duration"].apply(int)

    new_row = {"Date": date_str, "Start Time": start_time, "End Time": end_time}
    df = df.append(new_row, ignore_index=True)

    df["Duration"] = df["Duration"].apply(lambda x: pd.to_timedelta(x, unit="m"))

    df.to_csv(MEETING_DATA_FILE, index=False)

    meeting_count = len(df)

    duration = pd.to_datetime(end_time) - pd.to_datetime(start_time)
    duration_str = str(duration)
    print(f"Meeting Session successfully added. The duration of the meeting is {duration_str}. This is meeting {meeting_count} of the day.")
    print()

    # No need to include the return statement here





def calculate_total_time():
    current_date = datetime.now().date()
    total_time = timedelta()
    meeting_exists = False

    if os.path.exists(MEETING_DATA_FILE) and os.path.getsize(MEETING_DATA_FILE) > 0:
        with open(MEETING_DATA_FILE, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 4:
                    date_str, start_time, end_time, duration_str = row
                    meeting_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    duration = timedelta(seconds=float(duration_str))
                    if meeting_date == current_date:
                        total_time += duration
                        meeting_exists = True

    if meeting_exists:
        hours = total_time.seconds // 3600
        minutes = (total_time.seconds % 3600) // 60

        print(f"Total meeting time for {current_date}: {hours} hours and {minutes} minutes")
    else:
        print("No meeting data found for the current date.")

def list_todays_meetings():
    current_date = datetime.now().date()
    date_str = current_date.strftime("%Y-%m-%d")

    meetings = []

    if os.path.exists(MEETING_DATA_FILE) and os.path.getsize(MEETING_DATA_FILE) > 0:
        with open(MEETING_DATA_FILE, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 4:
                    date, start_time, end_time, duration_str = row
                    if date == date_str:
                        meetings.append([date, start_time, end_time, duration_str])

    if not meetings:
        print("No meetings found for today.")
        return

    df = pd.DataFrame(meetings, columns=["Date", "Start Time", "End Time", "Duration"])
    df["Duration"] = pd.to_timedelta(df["Duration"])
    df["Duration"] = df["Duration"].apply(lambda x: x.total_seconds() / 60)

    total_duration = df["Duration"].sum()

    df["Duration"] = pd.to_timedelta(df["Duration"], unit="m")

    print("Today's Meetings:")
    print(df)
    print(f"\nTotal meeting duration for today: {total_duration} minutes")

    delete_row = input("Enter the row number to delete (or enter '0' to cancel): ")

    if delete_row.isdigit():
        delete_row = int(delete_row)
        if delete_row == 0:
            return
        if delete_row > 0 and delete_row <= len(df):
            row_to_delete = df.iloc[delete_row - 1]
            print("\nDeleting the following meeting:")
            print(row_to_delete)
            confirmation = input("Are you sure you want to delete this meeting? (y/n): ")
            if confirmation.lower() == "y":
                df = df.drop(index=delete_row - 1)
                df.reset_index(drop=True, inplace=True)
                df.to_csv(MEETING_DATA_FILE, index=False)
                print("Meeting deleted successfully.")
        else:
            print("Invalid row number. Please enter a valid row number.")
    else:
        print("Invalid input. Please enter a valid row number.")

    print()


def export_meetings(start_date, end_date=None):
    meetings = []
    meeting_exists = False

    if os.path.exists(MEETING_DATA_FILE) and os.path.getsize(MEETING_DATA_FILE) > 0:
        with open(MEETING_DATA_FILE, "r") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) == 4:
                    date_str, start_time, end_time, duration_str = row
                    meeting_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    if not end_date:
                        if meeting_date == start_date:
                            meetings.append(row)
                            meeting_exists = True
                    else:
                        if start_date <= meeting_date <= end_date:
                            meetings.append(row)
                            meeting_exists = True

    if meeting_exists:
        if not end_date:
            filename = f"meetings_{start_date}.txt"
        else:
            filename = f"meetings_{start_date}_to_{end_date}.txt"

        with open(filename, "w") as file:
            file.write("Meetings:\n")
            for meeting in meetings:
                date_str, start_time, end_time, duration_str = meeting
                file.write(f"Date: {date_str}, Start Time: {start_time}, End Time: {end_time}, Duration: {duration_str}\n")

        print(f"Meetings exported successfully to {filename}")
    else:
        print("No meeting data found within the specified date range.")

def main():
    print("Meeting Time Tracker")
    print("--------------------")

    while True:
        print("\n1. Add meeting")
        print("2. Calculate total meeting time for today")
        print("3. List today's meetings")
        print("4. Export today's meetings to text file")
        print("5. Export meetings within a date range to text file")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == "1":
            add_meeting()
        elif choice == "2":
            calculate_total_time()
        elif choice == "3":
            list_todays_meetings()
        elif choice == "4":
            export_meetings(datetime.now().date())
        elif choice == "5":
            start_date = input("Enter the start date (YYYY-MM-DD): ")
            end_date = input("Enter the end date (YYYY-MM-DD): ")
            export_meetings(datetime.strptime(start_date, "%Y-%m-%d").date(), datetime.strptime(end_date, "%Y-%m-%d").date())
        elif choice == "6":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
