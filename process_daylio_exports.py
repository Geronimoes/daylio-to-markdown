import os
import re
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

def process_daylio_exports(csv_file_path):
    print(f"Processing Daylio CSV export at: {csv_file_path}")
    # Load the configuration from the .env file
    load_dotenv()
    export_folder = os.getenv('EXPORT_FOLDER') # Where the markdown files will be saved
    processed_entries_file = os.getenv('PROCESSED_ENTRIES_FILE') # Where the processed entries are saved (processed_entries.txt)
    tracked_keywords_file = os.getenv('TRACKED_KEYWORDS_FILE') # Where the tracked keywords are saved (tracked_keywords.txt)
    processed_folder = os.path.join(os.getenv('WATCH_FOLDER'), 'processed') # Where the processed Daylio CSV export files will be moved to after processing

    # Create the processed folder if it doesn't exist
    os.makedirs(processed_folder, exist_ok=True)

    # Read the processed entries from the file
    processed_entries = set()
    if os.path.exists(processed_entries_file): # Check if the processed_entries.txt file exists
        with open(processed_entries_file, 'r') as file:
            processed_entries = set(file.read().splitlines())
    print(f"Loaded {len(processed_entries)} previously processed entries.") # Print the number of already processed entries according to the processed_entries.txt file

    # Read the tracked keywords from the file
    tracked_keywords = {}
    with open(tracked_keywords_file, 'r') as file:
        for line in file:
            line = line.strip()
            if ':' in line:
                keyword, tag = line.split(':', 1)
                keyword = keyword.lower()
                if keyword not in tracked_keywords:
                    tracked_keywords[keyword] = set()
                tracked_keywords[keyword].add(tag.strip())
            else:
                keyword = line.lower()
                if keyword not in tracked_keywords:
                    tracked_keywords[keyword] = set()
                tracked_keywords[keyword].add(keyword.strip())
    # Print the tracked keywords
    print(f"Loaded {len(tracked_keywords)} tracked keywords from tracked_keywords.txt as set in .env:")
    for keyword, tags in tracked_keywords.items():
        print(f"  {keyword}: {', '.join(tags)}") # Print each keyword and its associated tags

    # Read the CSV file using pandas
    df = pd.read_csv(csv_file_path)

    # Print the number of entries loaded
    print(f"Loaded {len(df)} Daylio entries that contain text notes from the exported CSV file.")

    # Process each entry
    print("Processing new entries...")
    for _, entry in df.iterrows():
        # Check if the entry has a note and has not been processed before
        if pd.notna(entry['note']) and f"{entry['full_date']}T{entry['time']}" not in processed_entries: # Check if the entry has a note and has not been processed before using the full date and time as a unique identifier, listed in processed_entries.txt file which is set in .env
            # Format the YAML frontmatter
            frontmatter = f"---\n" # Start the YAML frontmatter
            frontmatter += f"title: Daylio Note for {entry['weekday']}, {entry['full_date']} at {entry['time']}\n" # Add the title to the 'title' yaml key
            frontmatter += f"aliases: \n" # Start the 'aliases' yaml key, in case I want to further classify these later
            frontmatter += f"created: {entry['full_date']}T{entry['time']}:00+01:00\n" # Add the created date to the 'created' yaml key using the following format: YYYY-MM-DDTHH:MM:SS+01:00 (seconds and timezone are not recorded by Daylio, but are added for consitency with Obsidian's format)
            frontmatter += f"tags:\n" # Start the 'tags' yaml key

            # Add activities as tags
            if pd.notna(entry['activities']):
                activities = str(entry['activities']).split(' | ')
                for activity in activities:
                    frontmatter += f"  - {activity.strip().replace(' ', '_')}\n" # Replace spaces with underscores so that they are treated as complete tags in Obsidian

            # Search for tracked keywords in the note, note_title, or activities
            content = str(entry['note']) + str(entry['note_title']) + str(entry['activities'])
            found_tags = set()
            for keyword, tags in tracked_keywords.items():
                if re.search(r'\b' + re.escape(keyword) + r'\b', content, re.IGNORECASE):
                    found_tags.update(tags)
            for tag in found_tags:
                frontmatter += f"  - {tag}\n" # Add the found tags to the 'tags' yaml key

            frontmatter += f"mood: {entry['mood']}\n" # Add the mood value to the 'mood' yaml key
            frontmatter += f"modified: \n" # Add the modified date to the 'modified' yaml key
            frontmatter += f"---\n\n" # End the YAML frontmatter and add a newline
            frontmatter += f"{entry['note']}\n" # Add the note content

            # Generate the markdown filename
            filename = f"{entry['full_date'][2:].replace('-', '')}{entry['time'].replace(':', '')} - Daylio note.md" # Remove dashes and colons from the date and time and remove the first two characters (century) from the date to shorten the filename
            file_path = os.path.join(export_folder, filename)

            # Save the markdown file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(frontmatter)

            # Add the entry to the processed entries set
            processed_entries.add(f"{entry['full_date']}T{entry['time']}") # Add the entry's full date and time to the processed entries set

            print(f"Created: {filename}") # Print the filename of the created markdown file

    # Save the updated processed entries to the file
    with open(processed_entries_file, 'w') as file:
        file.write('\n'.join(processed_entries))
    print(f"Current total of unique Daylio text notes that have been processed: {len(processed_entries)}") # Print the number of processed entries saved to the processed_entries.txt file

    # Move the processed CSV file to the processed folder with a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") # Get the current timestamp, formatted as YYYYMMDD_HHMMSS
    processed_csv_filename = f"{os.path.splitext(os.path.basename(csv_file_path))[0]}_{timestamp}.csv" # Create a new filename with the timestamp
    processed_csv_path = os.path.join(processed_folder, processed_csv_filename) # Create the full path to the processed CSV file
    os.rename(csv_file_path, processed_csv_path) # Move the processed CSV file to the processed folder with the new filename
    print(f"Moved and renamed processed CSV file to: {processed_csv_path}") # Print the path to the moved processed CSV file