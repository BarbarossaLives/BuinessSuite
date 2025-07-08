# poster.py
import requests
import os

def post_to_discord(kofi_url, comment, webhooks, image_path=None):
    print("got to post to discord function")
    if not kofi_url:
        print("No Ko-fi URL provided. Aborting.")
        return

    message = f"Check out my latest post on Ko-fi!\n{kofi_url}"
    print(message)


    if comment:
        message += f"\n\n{comment}"
        print("Updated Message: " + message)

    for url in webhooks:
        if url.strip():
            data = {"content": message}
            files = None

            if image_path:
                try:
                    with open(image_path, 'rb') as f:
                        files = {"file": (os.path.basename(image_path), f)}
                        response = requests.post(url, data=data, files=files)
                except Exception as e:
                    print(f"Failed to upload image to Discord: {e}")
            else:
                try:
                    response = requests.post(url, data=data)
                except Exception as e:
                    print(f"Failed to post message to Discord: {e}")
