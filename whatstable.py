import zipfile
import re
import pandas as pd
from io import BytesIO

def extract_data_from_txt_file_in_archive(zip_path: BytesIO | str) -> list[str] | None:
    """
    Finds the first .txt file in a zip archive and returns the content of the file as list.

    Args:
        zip_path (str): The file path to the .zip file.

    Returns:
        list[str]: A list of strings, where each string is a line from the .txt file, or None if not found or an error occurs.
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Find the filename of the first .txt file in the archive
            txt_filename = next((filename for filename in zip_ref.namelist() if filename.endswith('.txt')), None)
            
            if txt_filename:
                # Read, decode, and clean each line in one go, from bytes to strings
                with zip_ref.open(txt_filename) as txt_file:
                    return [line.decode('utf-8').replace('\u200e', '') for line in txt_file.readlines()]
            else:
                print("Error: No .txt file found in the zip archive.")
                return None    
        
    except FileNotFoundError:
        print(f"Error: The file '{zip_path}' was not found.")
        return None
    
    except zipfile.BadZipFile:
        print(f"Error: The file '{zip_path}' is not a valid zip file.")
        return None


def parse_chat_to_dataframe(chat_lines: list[str]) -> pd.DataFrame:
    """
    Parses a list of WhatsApp chat lines into a Pandas DataFrame.
    """
    # This will be used to extract the full data for each line of message
    apple_chat_pattern = re.compile(r'^\[(\d{2}/\d{2}/\d{4}, \d{2}:\d{2}:\d{2})\] ([^:]+): (.+)')
    android_chat_pattern = re.compile(r"^(\d{1,2}/\d{1,2}/\d{2}, \d{1,2}:\d{2}\s[AP]M) - ([^:]+): (.+)")


    apple_no_message = re.compile(r'^\[(\d{2}/\d{2}/\d{4}, \d{2}:\d{2}:\d{2})\] ([^:]+):\s*$')
    android_no_message = re.compile(r"^(\d{1,2}/\d{1,2}/\d{2}, \d{1,2}:\d{2}\s[AP]M) - ([^:]+):\s*$")

    discovered_pattern = "Apple" if apple_chat_pattern.match(chat_lines[0]) else "Android"

    system_message_pattern = re.compile(r"^(\d{1,2}/\d{1,2}/\d{2}, \d{1,2}:\d{2}\s?[AP]M) - ([^:]+)$")

    if discovered_pattern == "Apple":
        chat_pattern = apple_chat_pattern
        edge_case_pattern = apple_no_message
    else:
        chat_pattern = android_chat_pattern
        edge_case_pattern = android_no_message
    
    # This will be the correctly extracted data
    parsed_data = []
    
    for chat in chat_lines:
        match = chat_pattern.match(chat)
        # If the line is a complete chat message (the chat pattern matches)
        if match:
            parsed_data.append({
                'DateTime': match.group(1),
                'Sender': match.group(2).strip(),
                'Message': match.group(3).strip()
            })

        # Else, it's not a complete chat message
        else:
            # If it's a chat with no message, ignore
            if edge_case_pattern.match(chat):
                    pass
            # If it has messages, check if it's a SYSTEM MESSAGE
            elif system_message_pattern.match(chat):
                match = system_message_pattern.match(chat)
                if match:
                    parsed_data.append({
                    'DateTime': match.group(1),
                    'Sender': "SYSTEM MESSAGE",
                    'Message': match.group(2).strip()
                })
             # If it's not a SYSTEM MESSAGE, then just append the message to the previous message if previous message exists
            elif parsed_data:
                parsed_data[-1]["Message"] += f"\n{chat.strip()}"
            # Else add it to the table with no DateTime and Author
            else:
                parsed_data.append({
                    'DateTime': None,
                    'Sender': None,
                    'Message': chat.strip()
                })


    df = pd.DataFrame(parsed_data)
    if not df.empty:
        if discovered_pattern == "Apple":
            df['DateTime'] = pd.to_datetime(df['DateTime'], format='%d/%m/%Y, %H:%M:%S', errors='coerce')
        else:
            df['DateTime'] = pd.to_datetime(df['DateTime'], format='%m/%d/%y, %I:%M %p', errors='coerce')

    return df
