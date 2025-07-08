# mastodon_post.py
import os
import requests

def post_to_mastodon(instance_url, access_token, message, image_path=None):
    if not instance_url or not access_token:
        print("Mastodon URL and token required.")
        return

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    media_ids = []

    # Upload image first (if any)
    if image_path:
        try:
            with open(image_path, 'rb') as f:
                files = {'file': (os.path.basename(image_path), f)}
                media_resp = requests.post(
                    f"{instance_url}/api/v2/media",
                    headers=headers,
                    files=files
                )
                media_resp.raise_for_status()
                media_ids.append(media_resp.json()["id"])
        except Exception as e:
            print(f"Failed to upload media to Mastodon: {e}")

    # Post status update
    payload = {
        "status": message,
        "visibility": "public"
    }
    if media_ids:
        payload["media_ids[]"] = media_ids

    try:
        response = requests.post(
            f"{instance_url}/api/v1/statuses",
            headers=headers,
            data=payload
        )
        response.raise_for_status()
        print("Posted to Mastodon.")
    except Exception as e:
        print(f"Failed to post to Mastodon: {e}")
