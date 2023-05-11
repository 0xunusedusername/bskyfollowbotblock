import streamlit as st
import re
import requests
import time
from datetime import datetime
from atproto import Agent

def read_blacklist_file():
    with open('BLACKLIST.txt', 'r') as file:
        blacklist = [line.strip() for line in file.readlines()]
    return blacklist

BLACKLIST = read_blacklist_file()

ag = Agent()

def main():
    st.set_page_config(page_title="Bluesky Spam Follower Block", initial_sidebar_state="collapsed")

    if not hasattr(st.session_state, "logged_in"):
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        block_page()
    else:
        login_page()

def login_page():
    st.title("Bluesky Spam Follower Block")

    username = st.text_input("Username")
    st.text("Use your full Bluesky handle. Ex: username.bsky.social (no @ sign).")
    password = st.text_input("Password", type="password")
    st.text("This app only accepts an App Password.")

    if st.button("Log In"):
        if not re.match(r"\w{4}-\w{4}-\w{4}-\w{4}", password):
            st.session_state.apiUser = None
            st.session_state.apiPassword = None
            st.warning("Invalid password. Please use an App Password.")
        else:
            st.session_state.apiUser = username
            st.session_state.apiPassword = password
            login_success = authenticate(st.session_state.apiUser, st.session_state.apiPassword)
            if login_success:
                st.session_state.logged_in = True
                st.experimental_rerun()
            else:
                st.error("Invalid username or password.")

def block_page():
    st.title("Block some spammers!")
    st.write(f"User: {st.session_state.apiUser}")
    followLimit = int(st.text_input("Follow Limit:", value=30000))
    st.text("The minimum Follow Limit is 10000 users.")
    if followLimit < 10000:
        st.warning("Follow Limit should be at least 10000.")
    else:
        if st.button("Block"):
            bluesky_block(st.session_state.apiUser, st.session_state.apiPassword, followLimit)

def authenticate(apiUser, apiPassword):
    try:
        ag.login(apiUser, apiPassword)
        return True
    except:
        return False

def bluesky_block(apiUser, apiPassword, followLimit):
    ag.login(apiUser, apiPassword)
    user = ag.get("com.atproto.identity.resolveHandle", handle=apiUser)["did"]

    with st.spinner('Blocking...'):
        output_area = st.empty()
        output = ""
        for did in BLACKLIST:
            userToBlock = ag.get("app.bsky.actor.getProfile", actor=did)
            if userToBlock.get("followsCount") >= followLimit:
                ag.post("com.atproto.repo.createRecord", {
                    "repo": user,
                    "collection": "app.bsky.graph.block",
                    "record": {
                        "$type": "app.bsky.graph.block",
                        "createdAt": datetime.utcnow().isoformat(),
                        "subject": userToBlock
                    }
                })
                output += f"{userToBlock.get('handle')} BLOCKED!\n"
                output_area.text(output)
                time.sleep(0.1)
            else:
                continue

if __name__ == "__main__":
    main()
