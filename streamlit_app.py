import streamlit as st
import re
import requests
from datetime import datetime
from atproto import Agent

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
    me = ag.get("com.atproto.identity.resolveHandle", handle=apiUser)["did"]
    result = ag.get("app.bsky.graph.getFollowers", actor=me)
    
    for follow in result["followers"]:
        f = ag.get("com.atproto.identity.resolveHandle", handle=follow.get("handle"))["did"]
        follower = ag.get("app.bsky.actor.getProfile", actor=f)
        if follower.get("followsCount") >= followLimit:
            ag.post("com.atproto.repo.createRecord", {
                "repo": me,
                "collection": "app.bsky.graph.block",
                "record": {
                    "$type": "app.bsky.graph.block",
                    "createdAt": datetime.utcnow().isoformat(),
                    "subject": f
                }
            })
            st.write(follower.get("handle") + " BLOCKED!")
        else:
            continue

if __name__ == "__main__":
    main()
