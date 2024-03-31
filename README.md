# Daylio to Markdown
**With automated tagging**
*(Daylio to Obsidian)*

> [!TIP] TL;DR
>
> If you just want to use this right away with default settings, then do this:
>
> ```
> git clone https://github.com/Geronimoes/daylio-to-markdown.git
> cd daylio-to-markdown
> pip install -r requirements.txt
> mv .env.ready_to_go .env
> ```
>
> Then install python if you haven't already, save your Daylio CSV export to ./daylio-exports, and run:
>
> ```bash
> python folder_watcher.py
> ```
>
> Your markdown files should now be in ./md

## Intro

This repository contains a set of Python scripts to process and convert Daylio CSV exports into Markdown files, compatible with Obsidian flavored markdown syntax. The scripts are designed to extract relevant information from the CSV files, such as the date, mood, activities, and notes, and generate Markdown files with a YAML frontmatter for each entry. It (optionally) automatically adds predefined tags based on the full-text note, note title, or activities contents of your Daylio entries.

By default, **only Daylio entries that contain text notes** are converted. At present, to convert *all* Daylio entries regardless of whether a text note was added, you'd need to adjust the script yourself. I may add this as an optional flag/setting in the future.

I wrote these scripts for my own use, mainly because I take most of my notes in Obsidian, but since Daylio works better for me to 'force' myself to add at least one short note each day, I wanted a way to easily integrate these into my Obsidian workflow. 

I'm sharing them in case anyone else finds them helpful too. I don't really plan to maintain this repository very intensively, though. However, I'm happy to think along if you run into any issues with this, and may update/expand/fix the scripts from time to time. I have only tested it on a Ubuntu system, so your mileage may vary.

### Default formatting of markdown exports
All Daylio entries *that contain a text note* are parsed by these scripts, the rest is skipped. A single character as text note is enough to be included though.

The markdown output filenames are formatted as follows:

`{YYMMDDHHmm} - Daylio note.md`

For example: `2403312109 - Daylio note.md` for a Daylio entry that was made on 31 March 2024 at 21:09 (9:09pm). This is currently hardcoded but you can change the script if you like.

The Obsidian-compatible markdown output formatting is currently hardcoded to the following format (you can edit `process_daylio_exports.py` if you want to change this):

```markdown
---
title: Daylio Note for {weekday}, {YYYY-MM-DD} at {HH:mm} *
aliases: ****
created: {YYYY-MM-DDTHH:mm:00+01:00} **
tags:
  - {any and all activities / factors selected in Daylio, as separate tags}
  - {any and all keywords set in tracked_keywords.txt as separate tags, no duplicates}
mood: {mood entry} ***
modified: ****
---

{note text content as recorded in Daylio}

```

\* = I'm using 24h time notation, so e.g. 21:30, *not* 9:30pm. To change this, you'd have to edit the script at the moment.
\*\* = Example of this format: `2024-03-31T17:21:00+01:00`. Daylio doesn't record seconds, nor timezone. I use both of these in my regular Obsidian notes, however (and other plugins there expect this formatting), so currently the part of the 'created' YAML key that says ':00+01:00' is hardcoded into the script, as is the 'T' between date and time. The '+01:00' represents (my) timezone. These should be fairly easy to change in the script if you prefer, though. I might change all of this into configurable settings at some point.
\*\*\* = The word/string that was selected in Daylio to indicate the 'mood' for this entry. For example, by default 🙂 is 'good'. This can be configured in Daylio though, I believe.
\*\*\*\* = 'aliases' and 'modified' are left blank. I personally use these when working on notes further, after export. You can easily remove / change them in the script if you prefer.

## Features

- Processes Daylio CSV exports and generates Markdown files with YAML frontmatter
- Supports adding Daylio 'activities' / factors as tags in the YAML frontmatter
- Searching for specified custom keywords in the full text of the Daylio 'note', 'note title', or 'activities' fields to add these as custom YAML frontmatter tags. This is upper/lowercase agnostic, though tags can be specified also in terms of capitalization
- Supports multiple tags added to the frontmatter per activity/keyword and/or multiple keywords to the same tag (all set in the specified `tracked_keywords.txt`), such as:
  - Multiple keywords to same tag;
    ```
    Jack:Friends
    Jill:Friends
    Billy:Friends
    ```
  - Single keywords to multiple tags;
    ```
    Jack # will create a tag 'jack' (lowercase unless specified)
    Jack:Friends
    Jack:Colleagues
    ```
  - Combined / alternate uses;
    ```
    Jack:Jack # will create a tag 'Jack' (capitalized as specified on the right-hand side)
    Jack:Friends
    Jack:Colleagues
    Friends:Friends
    Party:Friends
    Party:Events
    ...
    ```
- Skips entries that have already been processed (Daylio CSV exports contain all historical entries by default, so this is to prevent duplicate files)
- Moves processed CSV files to a separate folder with a timestamp (to a 'processed' subdirectory that is created inside the watch folder you specify in the .env file)
- Optionally transfers processed files to a remote server via SFTP (currently credentials and settings are stored in an **unencrypted plaintext** .env file)

### What this **doesn't** (yet) do:

- Transfer / include Daylio image attachments (these are not exported with the CSV by Daylio)
- Delete *anything* in the markdown output/target directory, not even entries you may have removed from Daylio. This is by design, as - if you're like me - you may have edited the output markdown files further in Obsidian, VS Code, or whatever you may use

## Prerequisites

- [Python 3.x](https://www.python.org/downloads/)
- Required Python packages: pandas (to work with csv data), python-dotenv (to read the .env file for your configuration), paramiko (for SFTP transfer)

## Setup

1. Clone this repository:

```
git clone https://github.com/Geronimoes/daylio-to-markdown.git
cd daylio-to-markdown 
```

2. Install the required Python packages by running `pip install -r requirements.txt`:

```bash
pip install -r requirements.txt
```

*or:*

```bash
pip install python-dotenv
pip install pandas
pip install paramiko
``` 

3. Create a `.env` file in the project directory and configure the necessary environment variables (see the `.env.example` file for reference):

```bash
cp .env.example .env
nano .env # Or any other editor you prefer instead of nano
```

The paths in the `.env` file can be either absolute or relative to the script directory. Absolute paths are recommended for better portability.

4. (Optional) If you want to track specific keywords in your Daylio notes and add them as tags, create a `tracked_keywords.txt` file and add your keywords (see the `tracked_keywords.txt.example` file for reference).

```bash
cp tracked_keywords.txt.example tracked_keywords.txt
nano tracked_keywords.txt # Add your keywords here as per the included instructions
```

## Usage

1. Place your Daylio CSV export files in the `WATCH_FOLDER` directory specified in the `.env` file.

To export your Daylio entries as a CSV file, follow these steps:
- Open the Daylio app on your device
- Tap the three dots in the bottom right corner
- Select "Export entries"
- Choose "CSV (table)"
- Save the CSV file to the `WATCH_FOLDER` directory specified in your `.env` file

2. Run the `folder_watcher.py` script to start monitoring the folder for new CSV files.

```bash
python folder_watcher.py
```

*or* (depending on your Python configuration):

```bash
python3 folder_watcher.py
```

By default, the script will process any new CSV files and then exit. To **run the script continuously or on a schedule**, you can set up a cron job (which is what I do) or a systemd service (untested).

For example, to run the script every 5 minutes using cron, you can add the following line to your crontab (replace `/path/to/daylio-to-markdown` with the actual path to your project directory, and `python` with `python3` as per your configuration):

```
*/5 * * * * cd /path/to/daylio-to-markdown && python folder_watcher.py
```

Alternatively, you can create a systemd service file (e.g., `daylio.service`) with the following content:

```
[Unit]
Description=Daylio to Markdown Converter
After=network.target

[Service]
ExecStart=/usr/bin/python /path/to/daylio-to-markdown/folder_watcher.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Then, copy the `daylio.service` file to `/etc/systemd/system/`, start the service, and enable it to run on system startup:

```bash
sudo cp daylio.service /etc/systemd/system/
sudo systemctl start daylio
sudo systemctl enable daylio
```

3. The script will process any new CSV files, generate Markdown files in the `EXPORT_FOLDER` directory, and move the processed CSV files to a `processed` subdirectory renamed with a timestamp to avoid duplicates.
4. (Optional) If the `TRANSFER_ENABLED` option is set to `true` in the `.env` file, the processed files will be transferred to the specified remote server via Sftp. This feature is currently a little hit or miss in my testing, but I don't use it often enough to be bothered to look into the details just yet.

## Configuration

The following environment variables can be set in the `.env` file:

- `WATCH_FOLDER`: The path to the folder where Daylio CSV export files are placed.
- `EXPORT_FOLDER`: The path to the folder where the generated Markdown files will be saved. **Make sure to create this directory before running the script**, e.g. `mkdir md`.
- `PROCESSED_ENTRIES_FILE`: The path to the `processed_entries.txt` file that stores the list of processed entries in order to avoid creating duplicates.
- `TRACKED_KEYWORDS_FILE`: The path to the `tracked_keywords.txt` file containing the list of keywords / tags to be added as tags in the YAML frontmatter.
- `REMOTE_HOST`: The hostname or IP address of the remote server for SFTP transfer (optional).
- `REMOTE_USERNAME`: The username for the remote server (optional).
- `REMOTE_PASSWORD`: The password for the remote server (optional).
- `REMOTE_PATH`: The path on the remote server where the files will be transferred (optional).
- `TRANSFER_ENABLED`: A boolean value (`true` or `false`) to enable or disable SFTP transfer (optional, defaults to `false`).

## Example Files

- `.env.example`: An example `.env` file with placeholders for the required environment variables.
- `tracked_keywords.txt.example`: An example `tracked_keywords.txt` file with sample keywords.

## How I use it

1. Export from Daylio every now and then
2. Run the script to process the new CSV exports
3. The processed Markdown files are exported to my Obsidian vault directory on my home server (but you can use this on a local machine just fine)
4. Syncthing picks up the new files from there and syncs them to all of my other devices

## Contributing

Of course! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request. As mentioned, I wrote this just for my own use. I'm happy if there is anyone else who finds a good use for this!
