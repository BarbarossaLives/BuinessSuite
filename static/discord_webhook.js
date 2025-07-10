export function sendMultiSitePost() {
  // Discord
  const webhook1Checked = document.getElementById('webhook1Check').checked;
  const webhook2Checked = document.getElementById('webhook2Check').checked;
  const webhook1Url = document.getElementById('webhook1Input').value;
  const webhook2Url = document.getElementById('webhook2Input').value;

  // Mastodon
  const mastodonChecked = document.getElementById('mastodonUrlCheck').checked;
  const mastodonUrl = document.getElementById('mastodonUrlInput').value;
  const mastodonToken = document.getElementById('mastodonTokenInput').value;

  // Bluesky
  const blueskyChecked = document.getElementById('blueskyHandleCheck').checked;
  const blueskyHandle = document.getElementById('blueskyHandleInput').value;
  const blueskyPassword = document.getElementById('blueskyPasswordInput').value;

  // Dev.to
  const devtoChecked = document.getElementById('devtoKeyCheck').checked;
  const devtoApiKey = document.getElementById('devtoKeyInput').value;

  // Message fields
  const originalPost = document.getElementById('originalPostInput').value;
  const postText = document.getElementById('postTextArea').value;
  const imagePath = document.getElementById('imagePathInput').value;

  // Add more fields for other sites as needed

  const data = {
    discord: {
      enabled: (webhook1Checked || webhook2Checked),
      webhooks: [webhook1Checked ? webhook1Url : null, webhook2Checked ? webhook2Url : null].filter(Boolean)
    },
    mastodon: {
      enabled: mastodonChecked,
      url: mastodonUrl,
      token: mastodonToken
    },
    devto: {
      enabled: devtoChecked,
      api_key: devtoApiKey
    },
    bluesky: {
      enabled: blueskyChecked,
      handle: blueskyHandle,
      password: blueskyPassword
    },
    message: {
      originalPost,
      postText,
      imagePath
    }
    // Add more site data here
  };

  fetch('/multi-site-post', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  })
  .then(response => response.json())
  .then(data => {
    alert('Post status: ' + JSON.stringify(data));
  })
  .catch(err => {
    alert('Error posting: ' + err);
  });
} 