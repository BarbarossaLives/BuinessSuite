# bluesky_post.py

from atproto import Client, models

def post_to_bluesky(handle, password, message, image_path=None):
    """
    Post a message to Bluesky using the atproto library.
    :param handle: Bluesky handle (e.g. @user.bsky.social)
    :param password: Bluesky app password
    :param message: The text to post
    :param image_path: Optional path to an image (not yet implemented)
    """
    client = Client()
    try:
        client.login(handle, password)
    except Exception as e:
        print(f"[Bluesky] Login failed: {e}")
        raise

    # Image upload is possible, but requires extra steps. For now, just post text.
    try:
        client.send_post(text=message)
        print(f"[Bluesky] Successfully posted: {message}")
    except Exception as e:
        print(f"[Bluesky] Failed to post: {e}")
        raise

    if image_path:
        print("[Bluesky] Image posting is not yet implemented in this function.") 