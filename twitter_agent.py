import streamlit as st
import pandas as pd
from news_handler import NewsHandler
from wiki_fetcher import WikiFetcher
import plotly.express as px
from datetime import datetime, timedelta
import time
from tweet_generator import TweetGenerator

# Page config and title
st.set_page_config(
    page_title="Twitter Posting Agent",
    page_icon="📰",
    layout="wide"
)

# Initialize the news fetcher, wiki fetcher, and tweet generator
@st.cache_resource
def get_news_handler():
    return NewsHandler()

@st.cache_resource  
def get_wiki_fetcher():
    return WikiFetcher()

@st.cache_resource
def get_tweet_generator():
    return TweetGenerator()

news_handler = get_news_handler()
wiki_fetcher = get_wiki_fetcher()
tweet_generator = get_tweet_generator()

# Sidebar for controls
st.sidebar.title("Twitter Posting Agent")

# Initialize session state variables
if 'user_topics' not in st.session_state:
    st.session_state.user_topics = ["AI"]  # Set a default topic

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
    st.session_state.use_custom_topic = False
    st.session_state.tweet_news = False
    st.session_state.wiki_facts = False
    if st.session_state.user_topics == []:
        st.sidebar.error("Please select a topic first")
        return
    else:
        st.sidebar.success("Posting agent started")

def on_show_tweet_click():
    st.session_state.show_tweet = True
    if st.session_state.user_topics == []:
        st.sidebar.error("Please select a topic first")
        return
    else:
        st.sidebar.success("Tweet shown")

def on_show_news_headlines_click():
    st.session_state.show_news_headlines = True

def display_detailed_news(topic, count=5):
    with st.spinner(f"Fetching news about {topic}..."):
        articles = news_handler.get_top_headlines(query=topic, count=count)
    
    if articles:
        st.subheader(f"📰 Top Headlines about {topic}")
        
        # Create columns for a more organized layout
        for article in articles:
            with st.container():
                st.markdown(f"### {article['title']}")
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    if 'description' in article and article['description']:
                        st.markdown(f"{article['description']}")
                    
                    # Create a row for metadata
                    source = article.get('source', 'Unknown')
                    published = article.get('published_at', 'Unknown date')
                    
                    st.markdown(f"**Source:** {source} | **Published:** {published}")
                    
                    if 'url' in article and article['url']:
                        st.markdown(f"[Read full article]({article['url']})")
                
                # Add a separator between articles
                st.markdown("---")
    else:
        st.warning(f"No headlines found for '{topic}'")

def display_wiki_facts(topic, count=3, use_expanders=True):
    with st.spinner(f"Fetching Wikipedia facts about {topic}..."):
        facts = wiki_fetcher.get_wiki_facts(query=topic, count=count)
    
    if facts:
        st.subheader(f"📚 Wikipedia Facts about {topic}")
        for i, fact in enumerate(facts, 1):
            if use_expanders:
                with st.expander(f"Fact {i}"):
                    st.write(fact['content'])
                    st.markdown(f"*Source: [{fact['source']}]({fact['url']})*")
            else:
                # No expanders, just display the content directly
                st.markdown(f"**Fact {i}:**")
                st.write(fact['content'])
                st.markdown(f"*Source: [{fact['source']}]({fact['url']})*")
                st.markdown("---")
    else:
        st.warning(f"No Wikipedia facts found for '{topic}'")

# Topic selection
topic = st.sidebar.selectbox(
    "Recent topics",
    options=st.session_state.user_topics,
    index=0
)

# Custom topic input
use_custom_topic = st.sidebar.checkbox("Use custom topic", value=st.session_state.use_custom_topic, key='use_custom_topic')

if use_custom_topic:
    custom_topic = st.sidebar.text_input("Enter custom topic")
    if custom_topic:
        topic = custom_topic
        # Add the custom topic to session state if it's not already there
        if custom_topic not in st.session_state.user_topics:
            if len(st.session_state.user_topics) == 0:
                st.session_state.user_topics = [custom_topic]
            else:
                st.session_state.user_topics.append(custom_topic)

# Latest News enhanced button
tweet_news = st.sidebar.checkbox("Latest News enhanced", value=st.session_state.tweet_news, key='tweet_news')

# Wikipedia Facts enhanced button
wiki_facts = st.sidebar.checkbox("Wikipedia Facts enhanced", value=st.session_state.wiki_facts, key='wiki_facts')

# Show tweet button
show_tweet = st.sidebar.button("Show tweet", on_click=on_show_tweet_click)

# Posting Agent start button
posting_agent = st.sidebar.button("Start Posting Agent", on_click=on_posting_agent_click)

# Main content section
st.title("Twitter Posting Agent")

if not show_tweet:
    st.info("This agent will create a tweet based on the topic you have selected and the enhancements you have selected.")

if show_tweet:
    if wiki_facts and tweet_news:
        st.header("📰 News and Wikipedia Facts Enhanced Mode")
        st.info("The agent will create tweets based on the latest news headlines and include interesting facts from Wikipedia.")

        # Generate the tweet
        with st.spinner("Generating tweet..."):
            tweet_text = tweet_generator.generate_tweet_with_contexts(
                topic,
                include_news=True,
                include_wiki=True,
                news_handler=news_handler,
                wiki_fetcher=wiki_fetcher
            )

        st.subheader("The below tweet will be posted:")
        
        # Display the tweet
        st.markdown(f"""
        <div style="background-color: #f8f9fa; border: 1px solid #e1e8ed; border-radius: 12px; padding: 20px; font-family: sans-serif; color: #000000;">
        {tweet_text}
        </div>
        """, unsafe_allow_html=True)

        with st.expander("News articles"):
            display_detailed_news(topic)
            
        with st.expander("Wikipedia Facts"):
            display_wiki_facts(topic, use_expanders=False)

    # Display different content based on checkbox selections
    elif tweet_news:
        st.header("📰 News Enhanced Mode")
        st.info("The agent will create tweets based on the latest news headlines for the selected topic.")
        
        # Generate the tweet
        with st.spinner("Generating tweet..."):
            tweet_text = tweet_generator.generate_tweet_with_contexts(
                topic,
                include_news=True,
                include_wiki=False,
                news_handler=news_handler,
                wiki_fetcher=False
            )

        st.subheader("The below tweet will be posted:")
        
        # Display the tweet
        st.markdown(f"""
        <div style="background-color: #f8f9fa; border: 1px solid #e1e8ed; border-radius: 12px; padding: 20px; font-family: sans-serif; color: #000000;">
        {tweet_text}
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("Source"):
            display_detailed_news(topic)

    elif wiki_facts:
        st.header("📚 Wikipedia Facts Enhanced Mode")
        st.info("The agent will include interesting facts from Wikipedia in the tweets.")
        
        # Generate the tweet
        with st.spinner("Generating tweet..."):
            tweet_text = tweet_generator.generate_tweet_with_contexts(
                topic,
                include_news=False,
                include_wiki=True,
                news_handler=False,
                wiki_fetcher=wiki_fetcher
            )

        st.subheader("The below tweet will be posted:")
        
        # Display the tweet
        st.markdown(f"""
        <div style="background-color: #f8f9fa; border: 1px solid #e1e8ed; border-radius: 12px; padding: 20px; font-family: sans-serif; color: #000000;">
        {tweet_text}
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("Source"):
            display_wiki_facts(topic, use_expanders=False)

    else:
        st.header("📰 Default Mode")
        st.info("The agent will create a tweet based on the topic you've selected without additional context.")
        
        # Generate the tweet
        with st.spinner("Generating tweet..."):
            tweet_text = tweet_generator.generate_tweet_with_contexts(
                topic,
                include_news=False,
                include_wiki=False,
                news_handler=news_handler,
                wiki_fetcher=wiki_fetcher
            )

        st.subheader("The below tweet will be posted:")
        
        # Display the tweet
        st.markdown(f"""
        <div style="background-color: #f8f9fa; border: 1px solid #e1e8ed; border-radius: 12px; padding: 20px; font-family: sans-serif; color: #000000;">
        {tweet_text}
        </div>
        """, unsafe_allow_html=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    "This app helps you create and schedule automated tweets based on your selected topics. "
    "Choose a topic, select enhancement options, and start the posting agent."
)
st.sidebar.markdown("© 2025 Twitter Posting Agent - Design by Aranya Ray")



