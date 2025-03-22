import streamlit as st
import pandas as pd
from news_fetcher import NewsFetcher
import plotly.express as px
from datetime import datetime, timedelta
import time

# Page config and title
st.set_page_config(
    page_title="Twitter Posting Agent",
    page_icon="📰",
    layout="wide"
)

# Initialize the news fetcher
@st.cache_resource
def get_news_fetcher():
    return NewsFetcher()

news_fetcher = get_news_fetcher()

# Sidebar for controls
st.sidebar.title("Twitter Posting Agent")

# Initialize session state variables
if 'user_topics' not in st.session_state:
    st.session_state.user_topics = ["First time run"]

if 'use_custom_topic' not in st.session_state:
    st.session_state.use_custom_topic = False

if 'tweet_news' not in st.session_state:
    st.session_state.tweet_news = False

if 'wiki_facts' not in st.session_state:
    st.session_state.wiki_facts = False

if 'show_tweet' not in st.session_state:
    st.session_state.show_tweet = False

if 'show_news_headlines' not in st.session_state:
    st.session_state.show_news_headlines = False

# Define callback function for the "Start Posting Agent" button
def on_posting_agent_click():
    # Instead of trying to update the checkbox session state directly,
    # we'll set a flag that will be processed in the next rerun
    st.session_state.use_custom_topic = False
    st.session_state.tweet_news = False
    st.session_state.wiki_facts = False

def on_show_tweet_click():
    st.session_state.show_tweet = True

def on_show_news_headlines_click():
    st.session_state.show_news_headlines = True


# Topic selection
topic = st.sidebar.selectbox(
    "Recent topics",
    options=st.session_state.user_topics,
    index=0
)

# Custom topic input - Now the checkbox uses the session state value
use_custom_topic = st.sidebar.checkbox("Use custom topic", value=st.session_state.use_custom_topic, key='use_custom_topic')

if use_custom_topic:
    custom_topic = st.sidebar.text_input("Enter custom topic")
    if custom_topic:
        topic = custom_topic
        # Add the custom topic to session state if it's not already there
        if custom_topic not in st.session_state.user_topics:
            if len(st.session_state.user_topics) == 1 and st.session_state.user_topics[0] == "First time run":
                st.session_state.user_topics = [custom_topic]
            else:
                st.session_state.user_topics.append(custom_topic)

# Latest News enhanced button
tweet_news = st.sidebar.checkbox("Latest News enhanced", value=st.session_state.tweet_news, key='tweet_news')
# No need to manually update: st.session_state.tweet_news = tweet_news

# Wikipedia Facts enhanced button
wiki_facts = st.sidebar.checkbox("Wikipedia Facts enhanced", value=st.session_state.wiki_facts, key='wiki_facts')
# No need to manually update: st.session_state.wiki_facts = wiki_facts

# Show tweet button
show_tweet = st.sidebar.button("Show tweet", on_click=on_show_tweet_click)
# No need to manually update: st.session_state.show_tweet = show_tweet

# Posting Agent start button - using the callback function
posting_agent = st.sidebar.button("Start Posting Agent", on_click=on_posting_agent_click)
if posting_agent:
    st.sidebar.success("Posting Agent started")

# Main content section - Display information based on selections
st.title("Twitter Posting Agent")

if not show_tweet:
    st.info("This agent will create a tweet based on the topic you have selected and the enhancements you have selected.")

if show_tweet:
    if wiki_facts and tweet_news:
        st.header("📰 News and Wikipedia Facts Enhanced Mode")
        st.info("The agent will create tweets based on the latest news headlines and include interesting facts from Wikipedia.")

        st.subheader("The below tweet will be posted:")

        with st.expander("Source of the tweet"):
            st.write("This is like a new page inside the same page!")

        # Here we will display the tweet with both news and wikipedia facts

    # Display different content based on checkbox selections
    elif tweet_news:
        st.header("📰 News Enhanced Mode")
        st.info("The agent will create tweets based on the latest news headlines for the selected topic.")
        
        # Here you would fetch and display actual news headlines
        st.subheader("Latest Headlines that will be used for tweets:")

        with st.expander("Source of the tweet"):
            st.write("This is like a new page inside the same page!")
        
        # Here we will display the tweet with news headlines

    elif wiki_facts:
        st.header("📚 Wikipedia Facts Enhanced Mode")
        st.info("The agent will include interesting facts from Wikipedia in the tweets.")
        
        # Here you would fetch actual Wikipedia facts
        st.subheader("Wikipedia facts that will be used:")

        with st.expander("Source of the tweet"):
            st.write("This is like a new page inside the same page!")
        
        # Here we will display the tweet with wikipedia facts

    else:
        st.header("📰 Default Mode")
        st.info("The agent will create a tweet based on the latest news headlines for the selected topic.")

        # Here we will display the tweet with the default mode

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    "This app helps you create and schedule automated tweets based on your selected topics. "
    "Choose a topic, select enhancement options, and start the posting agent."
)
st.sidebar.markdown("© 2025 Twitter Posting Agent - Design by Aranya Ray")