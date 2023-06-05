# Streamlit Bluesky Follow Bot Block App

A simple Streamlit web application that demonstrates customizable Bluesky blocking functionality.

## Usage

- The web app is available [here](https://bskyfollowbotblock.streamlit.app/).
- Login with your Bluesky username (full handle, no @ sign) and an app password. You can create an app password [here](https://staging.bsky.app/settings/app-passwords).
- Enter follow limit threshold for blocking.
- Hit block and the app will then automatically block all users on the blacklist that are following an amount of accounts equal to or above the threshold you set.
- The blacklist will be updated over time, but feel free to reach out if you see an account that was missed!