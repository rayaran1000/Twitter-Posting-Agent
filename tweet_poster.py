from tweepy import Client
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import streamlit as st

class TweetPoster:
    """
    Class responsible for posting tweets to Twitter.
    """
    def __init__(self):
        """Initialize the TweetPoster with Twitter client."""
        load_dotenv()  # Load environment variables
        
        # For tweepy, you need consumer keys and access tokens for posting tweets
        # Bearer token alone is only for reading data
        self.twitter = Client(
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_SECRET")
        )
        
        # Initialize the scheduler or get it from session state
        if 'scheduler' not in st.session_state:
            print("Creating new scheduler")
            st.session_state.scheduler = BackgroundScheduler()
            st.session_state.scheduler.start()
        
        self.scheduler = st.session_state.scheduler

    def post_tweet_manually(self, tweet_text):
        """
        Post a tweet to Twitter immediately.
        
        Args:
            tweet_text (str): The text of the tweet to post
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            Exception: Various exceptions based on Twitter API errors
        """
        if not tweet_text:
            print("Cannot post empty tweet")
            return False
            
        if len(tweet_text) > 280:
            print(f"Tweet is too long ({len(tweet_text)} chars). Truncating...")
            tweet_text = tweet_text[:277] + "..."
        
        try:
            response = self.twitter.create_tweet(text=tweet_text)
            
            # Log success
            print(f"Tweet posted successfully: '{tweet_text}'")
            print(f"Twitter API response: {response}")
            
            return True
            
        except Exception as e:
            print(f"Failed to post tweet: {str(e)}")
            return False

    def schedule_recurring_tweets(self, tweet_generator_func, interval_hours=2):
        """
        Schedule tweets to be posted at regular intervals using a generator function.
        
        Args:
            tweet_generator_func: A function that generates tweet content
            interval_hours: How often to post tweets (in hours)
            
        Returns:
            tuple: (job_id, success_boolean)
        """
        try:
            # Add a job that will run at the specified interval
            job = self.scheduler.add_job(
                self._recurring_tweet_job,
                'interval',
                hours=0.01,
                args=[tweet_generator_func, interval_hours]
            )
            
            print(f"Recurring tweets scheduled every {interval_hours} hours")
            return job.id, True
            
        except Exception as e:
            print(f"Failed to schedule recurring tweets: {str(e)}")
            return None, False
    
    def _recurring_tweet_job(self, tweet_generator_func, interval_hours):
        """
        Internal method called by the scheduler for recurring tweets.
        
        Args:
            tweet_generator_func: Function that generates tweet content
            interval_hours: The interval in hours between tweets
        """
        try:
            # Generate a new tweet
            tweet_text = tweet_generator_func()
            
            # Post it
            return self.post_tweet_manually(tweet_text)
            
        except Exception as e:
            print(f"Error in recurring tweet job: {str(e)}")
            return False

    def stop_scheduler(self, job_id):
        """
        Stop a scheduled job by its ID.
        
        Args:
            job_id: The ID of the job to stop
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.scheduler.remove_job(job_id)
            print(f"Stopped scheduler job: {job_id}")
            return True
        except Exception as e:
            print(f"Failed to stop scheduler job: {str(e)}")
            return False
        
        