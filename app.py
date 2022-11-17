import os, yt_dlp, sys, cursor
import traceback
from datetime import datetime
from time import perf_counter, sleep
from pathlib import Path

cursor.hide()

current_dir = Path(__file__).parent
current_dir = os.path.normpath(current_dir)
os.chdir(current_dir)

downloaded = 0

# user settings
retries = 10
log_file_size_kb = 200
timeframe_default = "24hr"
root = "root/"
name_format = "clips/%(upload_date)s-%(id)s.%(ext)s"

# dev settings
format_to_download = "bv*+ba/b"
timestring = "%Y-%m-%d %I:%M:%S.%f"
timeframe_options = ["24hr", "7d", "30d", "all"]
output_dir = os.path.join(root, "{username}", "twitch-clips")
outtmpl = os.path.normpath(os.path.join(output_dir, name_format))
download_archive = os.path.normpath(os.path.join(output_dir, "history.txt"))


def countdown(seconds):
    for i in range(seconds, 0, -1):
        print(f"Exiting in {i} seconds...   ", end="\r")
        if i == 1:
            print("                         ", end="\r")
        sleep(1)


def write_log(username, type, msg):
    if "%f" in timestring:
        now = datetime.now().strftime(timestring)[:-3]
    else:
        now = datetime.now().strftime(timestring)

    log_dir = output_dir.format(username=username)
    log_type = "{type}.log".format(type=type)

    log = os.path.join(log_dir, log_type)
    log = os.path.normpath(log)
    if os.path.exists(log):
        if os.path.getsize(log) > log_file_size_kb * 1024:
            os.remove(log)

    with open(log, "a") as f:
        f.write(f"{now} {msg}\n")


def scrape_clips(username, timeframe="24hr"):
    url = f"https://www.twitch.tv/{username}/clips?filter=clips&range={timeframe}"
    abs_output = os.path.abspath(outtmpl.format(username=username))
    abs_archive = os.path.abspath(download_archive.format(username=username))
    print(f"Scraping: {url}")
    print(f"Output:   {abs_output}")
    print(f"History:  {abs_archive}\n")

    if not os.path.exists(output_dir.format(username=username)):
        os.makedirs(output_dir.format(username=username))

    class MyLogger(object):
        def debug(self, msg):
            if "downloading video " not in msg.lower():
                write_log(username, "debug", msg)

            if "graphql page " in msg.lower():
                print(
                    "["
                    + "-" * int((perf_counter() % 10) * 10 / 10)
                    + " " * int((10 - (perf_counter() % 10)) * 10 / 10)
                    + "] crawling pages...",
                    end="\r",
                )

            pass

        def warning(self, msg):
            write_log(username, "warning", msg)
            pass

        def error(self, msg):
            write_log(username, "error", msg)
            pass

    def my_hook(d):
        filename = os.path.normpath(d["filename"])
        filename = os.path.basename(filename)

        if d["status"] == "downloading":
            status_string = f"Downloaded: {filename}: {d['_percent_str']}"
            status_string += " " * 50
            print(status_string, end="\r")

        if d["status"] == "finished":
            global downloaded
            downloaded += 1

            status_string = f"Downloaded: {filename}: {d['_percent_str']}"
            status_string += " " * 50
            print(status_string)

    ydl_opts = {
        "logger": MyLogger(),
        "progress_hooks": [my_hook],
        "ignoreerrors": True,
        "restrictfilenames": True,
        "retries": retries,
        "format": format_to_download,
        "download_archive": download_archive.format(username=username),
        "outtmpl": outtmpl.format(username=username),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def main():
    title = "Twitch Clips Downloader"
    os.system("cls")
    os.system("title " + title)

    if len(sys.argv) == 1:
        username = input("Target (twitch username): ")
        tf_opts = ", ".join(timeframe_options)
        timeframe = input(f"Timeframe ({tf_opts}): ")
    elif len(sys.argv) == 2:
        username = sys.argv[1]
        print(f"Timeframe defaulting to {timeframe_default}")
        timeframe = timeframe_default
    elif len(sys.argv) == 3:
        username = sys.argv[1]
        timeframe = sys.argv[2]

    if timeframe not in timeframe_options:
        print(f"Invalid timeframe, defaulting to {timeframe_default}")
        timeframe = "24hr"

    username = username.lower()
    username = username.strip()

    scrape_clips(username=username, timeframe=timeframe)

    if downloaded > 0:
        print(f"\nDownloaded {downloaded} new clips." + " " * 50)
        print(f"Format: {outtmpl.format(username=username)}\n")
        countdown(10)
    else:
        print("No new clips found." + " " * 50)
        countdown(5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting..." + " " * 50)
        sys.exit(0)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        input("Press enter to exit..." + " " * 50)
        sys.exit(1)
    finally:
        cursor.show()
