# linkedin_post.py

import webbrowser
from urllib.parse import quote
import pyperclip


def build_linkedin_message(kofi_url, comment):
    message = f"Check out my latest post on Ko-fi!\n{kofi_url}"
    if comment:
        message += f"\n\n{comment}"
    return message


def share_on_linkedin(kofi_url, comment):
    message = build_linkedin_message(kofi_url, comment)

    # Copy to clipboard
    try:
        pyperclip.copy(message)
        print("Copied LinkedIn message to clipboard.")
    except Exception as e:
        print(f"Clipboard error: {e}")

    # Open LinkedIn share dialog
    encoded_url = quote(kofi_url, safe='')
    webbrowser.open(f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}")
