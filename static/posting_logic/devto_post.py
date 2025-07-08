# devto_post.py
import requests
import os

def post_to_devto(api_key, kofi_url, comment=None, image_path=None):
    if not api_key or not kofi_url:
        print("Dev.to API key and Ko-fi URL required.")
        return

    title = "New Ko-fi Post!"
    markdown_body = f"Check out my latest post on [Ko-fi]({kofi_url})"

    if comment:
        markdown_body += f"\n\n{comment}"

    if image_path and os.path.exists(image_path):
        image_url = os.path.basename(image_path)
        markdown_body += f"\n\n![image]({image_url})"

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }

    post_data = {
        "article": {
            "title": title,
            "published": True,
            "body_markdown": markdown_body,
            "tags": ["kofi", "update", "project"]  # You can let the user pick tags later
        }
    }

    try:
        response = requests.post("https://dev.to/api/articles", json=post_data, headers=headers)
        response.raise_for_status()
        print("Posted to Dev.to.")
    except Exception as e:
        print(f"Failed to post to Dev.to: {e}")
