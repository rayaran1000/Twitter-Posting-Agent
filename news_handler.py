import requests
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

class NewsHandler:

    def __init__(self):
        # Initialize MediaStack API key
        self.mediastack_api_key = os.getenv("MEDIASTACK_API_KEY")
        if not self.mediastack_api_key:
            raise ValueError("MEDIASTACK_API_KEY must be set in your .env file")
            
        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in your .env file")
            
        self.supabase = create_client(supabase_url, supabase_key)
    
    def get_top_headlines(self, query="AI", count=10, save_to_db=True, max_age_hours=24):
        """Fetch top headlines and optionally save them to Supabase.
        First checks if recent headlines exist in Supabase before calling the API.
        """
        try:
            # Check if we have recent headlines in Supabase first
            stored_headlines = self.fetch_stored_headlines(query=query, limit=count)
            
            # Check if headlines are recent enough
            current_time = datetime.now(timezone.utc)
            recent_headlines = []
            
            for headline in stored_headlines:
                try:
                    # Parse the timestamp from collected_at field
                    if 'collected_at' in headline:
                        # If collected_at is already a datetime object
                        if isinstance(headline['collected_at'], datetime):
                            headline_time = headline['collected_at']
                            if headline_time.tzinfo is None:
                                # Add timezone if naive
                                headline_time = headline_time.replace(tzinfo=timezone.utc)
                        # If it's a string, parse it
                        else:
                            headline_time = datetime.fromisoformat(headline['collected_at'].replace('Z', '+00:00'))
                        
                        age_hours = (current_time - headline_time).total_seconds() / 3600
                        
                        if age_hours <= max_age_hours:
                            recent_headlines.append(headline)
                except (ValueError, KeyError) as e:
                    print(f"Error parsing timestamp for headline: {e}")
                    continue
            
            # If we have enough recent stored headlines, return those
            if len(recent_headlines) >= count:
                print(f"Using {len(recent_headlines)} cached headlines from Supabase (less than {max_age_hours} hours old)")
                return recent_headlines
            
            # Otherwise, fetch new headlines from MediaStack API
            print(f"No recent cached headlines found for '{query}', fetching from MediaStack API")
            
            # MediaStack API endpoint
            url = "http://api.mediastack.com/v1/news"
            
            # Parameters for the API request
            params = {
                "access_key": self.mediastack_api_key,
                "keywords": query,
                "limit": count,
                "languages": "en",
                "sort": "published_desc"  # Get the most recent news first
            }
            
            # Make the API request
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            # Parse the response
            data = response.json()
            
            if 'data' in data and data['data']:
                articles = []
                
                for item in data['data']:
                    article = {
                        'title': item.get('title', ''),
                        'source': item.get('source', ''),
                        'url': item.get('url', ''),
                        'description': item.get('description', ''),
                        'published_at': item.get('published_at', '')
                    }
                    
                    articles.append(article)
                
                if save_to_db and articles:
                    self._save_headlines_to_supabase(articles, query)
                
                return articles
            else:
                print("No data returned from MediaStack API")
                return []
                
        except Exception as e:
            print(f"Error fetching headlines: {str(e)}")
            return []
    
    def _save_headlines_to_supabase(self, articles, query):
        """Save headlines to Supabase."""
        current_time = datetime.now(timezone.utc).isoformat()
        
        for article in articles:
            try:
                self.supabase.table('headlines').insert({
                    'title': article['title'],
                    'query': query,
                    'source': article['source'],
                    'url': article['url'],
                    'description': article.get('description', ''),
                    'published_at': article['published_at'],
                    'collected_at': current_time
                }).execute()
            except Exception as e:
                print(f"Error saving headline to Supabase: {str(e)}")
        
    def fetch_stored_headlines(self, query=None, limit=10):
        """Fetch headlines from Supabase."""
        try:
            if query:
                response = self.supabase.table('headlines').select('*').eq('query', query).limit(limit).execute()
            else:
                response = self.supabase.table('headlines').select('*').limit(limit).execute()
            
            return response.data
        except Exception as e:
            print(f"Error fetching stored headlines: {str(e)}")
            return []
    
    def get_news_context(self, query="AI", count=10, include_description=True):
        """
        Get news headlines and details formatted as context for LLMs.
        
        Args:
            query: The search query for headlines
            count: Number of headlines to return
            include_description: Whether to include the article description
            
        Returns:
            String: Formatted context for LLM consumption
        """
        try:
            # Fetch headlines first (using cached if available)
            articles = self.get_top_headlines(query=query, count=count)
            
            if not articles:
                return f"I couldn't find any recent news about {query}."
            
            # Format the articles into context
            context = f"Recent News Headlines about {query}:\n\n"
            
            # Select a random article from the available ones
            import random
            if articles:
                random_article = random.choice(articles)
                
                # Add headline with source and date
                context += f"1. {random_article['title']}\n"
                
                # Add source and date
                source = random_article.get('source', 'Unknown source')
                published = random_article.get('published_at', 'Unknown date')
                context += f"   Source: {source} | Published: {published}\n"
                
                # Add description if available and requested
                if include_description and 'description' in random_article and random_article['description']:
                    # Clean up the description - remove excess newlines and spaces
                    description = random_article['description'].replace('\n', ' ').strip()
                    context += f"   Summary: {description}\n"
                
                # Add URL if available
                if 'url' in random_article and random_article['url']:
                    context += f"   URL: {random_article['url']}\n"
            
            return context
        except Exception as e:
            print(f"Error generating news context: {str(e)}")
            return f"There was an error retrieving news about {query}."
    
    
    

