import os, subprocess, datetime
from time import sleep, perf_counter
from pathlib import Path

current_dir = Path(__file__).parent
current_dir = os.path.normpath(current_dir)
os.chdir(current_dir)

app = "app.py"
timeframes = ["24hr", "7d", "30d", "all"]
debug = False


def run_times(delay=12):
    now = datetime.datetime.now()
    current_run = (
        datetime.datetime.now().strftime("%I:%M:%S")
        + {0: " AM", 1: " PM"}[now.hour > 12]
    )
    next_run = now + datetime.timedelta(hours=delay)
    next_run = next_run.strftime("%I:%M:%S") + {0: " AM", 1: " PM"}[next_run.hour > 12]
    times = [current_run, next_run]
    return times


def file_to_list(file):
    try:
        with open(file, "r") as f:
            users = f.read().splitlines()
        for user in users:
            if " " in user:
                warn = f"Error: {file} contains spaces. Please remove them."
                raise Exception(warn)
        return users
    except FileNotFoundError:
        with open(file, "w") as f:
            f.write("usernames separated by a new line\n")
            f.write("example:\nuser1\nuser2\nuser3")
        print(f"{file} not found. Created {file} with example content.")
        input("Press enter to exit...")
        exit()


def human_time(seconds):
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    hours = int(hours)
    minutes = int(minutes)
    seconds = float("{:.2f}".format(seconds))

    if hours:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds} seconds"


def main():
    usernames = file_to_list("users.txt")  # list of usernames
    delay = 6  # in hours

    if debug:
        # put debug code here
        input("Press enter to continue...")

    while True:
        s1 = perf_counter()
        for time in timeframes:
            for user in usernames:
                subprocess.run(["python", app, user, time])
        os.system("cls")
        s2 = perf_counter()

        print(f"Scraped {len(usernames)} users.")
        print(f"Users: {', '.join(usernames)}")
        print(f"Timeframes: {', '.join(timeframes)}")
        print(f"Finished In: {human_time(s2 - s1)}\n")

        print(f"Current Time:   {run_times(delay=delay)[0]}")
        print(f"Next Run:       {run_times(delay=delay)[1]}")
        print(f"Sleeping for {delay} hours...")
        sleep(60 * 60 * delay)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting...")
        sleep(1)
    except Exception as e:
        print(e)
        input("Press enter to exit...")
