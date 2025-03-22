import os
from dotenv import load_dotenv
from datetime import datetime, timezone
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from supabase import create_client

load_dotenv()

class WikiFetcher:
    def __init__(self):
        # Initialize Wikipedia API wrapper
        self.wikipedia = WikipediaAPIWrapper(top_k_results=10)
        self.wikipedia_tool = WikipediaQueryRun(api_wrapper=self.wikipedia)
        
        # Initialize Supabase client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in your .env file")
            
        self.supabase = create_client(supabase_url, supabase_key)
        
    def get_wiki_facts(self, query, count=10, save_to_db=True, max_age_hours=168):  # Default 7 days cache
        """
        Fetch facts from Wikipedia about a specific topic.
        First checks if facts exist in Supabase before calling the API.
        
        Args:
            query: The search query for Wikipedia
            count: Number of facts to return
            save_to_db: Whether to save new facts to the database
            max_age_hours: Maximum age of cached facts in hours
        """
        try:
            # Check if we have recent facts in Supabase first
            stored_facts = self.fetch_stored_facts(query=query, limit=count)
            
            # Check if facts are recent enough
            current_time = datetime.now(timezone.utc)
            recent_facts = []
            
            for fact in stored_facts:
                try:
                    # Parse the timestamp from collected_at field
                    if 'collected_at' in fact:
                        # If collected_at is already a datetime object
                        if isinstance(fact['collected_at'], datetime):
                            fact_time = fact['collected_at']
                            if fact_time.tzinfo is None:
                                # Add timezone if naive
                                fact_time = fact_time.replace(tzinfo=timezone.utc)
                        # If it's a string, parse it
                        else:
                            fact_time = datetime.fromisoformat(fact['collected_at'].replace('Z', '+00:00'))
                        
                        age_hours = (current_time - fact_time).total_seconds() / 3600
                        
                        if age_hours <= max_age_hours:
                            recent_facts.append(fact)
                except (ValueError, KeyError) as e:
                    print(f"Error parsing timestamp for fact: {e}")
                    continue
            
            # If we have enough recent stored facts, return those
            if len(recent_facts) >= count:
                print(f"Using {len(recent_facts)} cached facts from Supabase (less than {max_age_hours} hours old)")
                return recent_facts
            
            # Otherwise, fetch new facts from Wikipedia API
            print(f"No recent cached facts found for '{query}', fetching from Wikipedia")
            
            # Use LangChain's Wikipedia tool to fetch information
            wiki_result = self.wikipedia_tool.invoke(query)
            
            if wiki_result:
                # Process wiki results into digestible facts
                processed_facts = self._process_wiki_results(wiki_result, query, count)
                
                if save_to_db and processed_facts:
                    self._save_facts_to_supabase(processed_facts, query)
                
                return processed_facts
            else:
                print(f"No Wikipedia information found for '{query}'")
                return []
                
        except Exception as e:
            print(f"Error fetching Wikipedia facts: {str(e)}")
            return []
            
    def _process_wiki_results(self, wiki_text, query, count=10):
        """
        Process Wikipedia results into digestible facts.
        """
        try:
            # Split the text into paragraphs
            paragraphs = wiki_text.split("\n\n")
            
            # Filter out empty paragraphs and those that are too short
            paragraphs = [p for p in paragraphs if len(p) > 50]
            
            facts = []
            for i, paragraph in enumerate(paragraphs):
                if i >= count:
                    break
                    
                # Create a fact dictionary
                fact = {
                    'content': paragraph.strip(),
                    'topic': query,
                    'source': 'Wikipedia',
                    'url': f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}",
                }
                
                facts.append(fact)
                
            return facts
        except Exception as e:
            print(f"Error processing Wikipedia results: {str(e)}")
            return []
            
    def _save_facts_to_supabase(self, facts, query):
        """Save facts to Supabase."""
        current_time = datetime.now(timezone.utc).isoformat()
        
        for fact in facts:
            try:
                self.supabase.table('wiki_facts').insert({
                    'content': fact['content'],
                    'topic': query,
                    'source': fact['source'],
                    'url': fact['url'],
                    'collected_at': current_time
                }).execute()
            except Exception as e:
                print(f"Error saving fact to Supabase: {str(e)}")
        
    def fetch_stored_facts(self, query=None, limit=10):
        """Fetch facts from Supabase."""
        try:
            if query:
                response = self.supabase.table('wiki_facts').select('*').eq('topic', query).limit(limit).execute()
            else:
                response = self.supabase.table('wiki_facts').select('*').limit(limit).execute()
            
            return response.data
        except Exception as e:
            print(f"Error fetching stored facts: {str(e)}")
            return []

    def get_wiki_context(self, query, count=10, max_length=500):
        """
        Get Wikipedia facts formatted as context for LLMs.
        
        Args:
            query: The search query for Wikipedia
            count: Number of facts to return (will fetch this many but only return one random fact)
            max_length: Maximum length of each fact in characters
            
        Returns:
            String: Formatted context for LLM consumption with a single random fact
        """
        try:
            # Fetch facts first (using cached if available)
            facts = self.get_wiki_facts(query=query, count=count)
            
            if not facts:
                return f"I couldn't find any Wikipedia information about {query}."
            
            # Format the facts into context
            context = f"Wikipedia Information about {query}:\n\n"
            
            # Select a random fact from the available ones
            import random
            random_fact = random.choice(facts)
            
            # Get content and truncate if necessary
            content = random_fact['content']
            if len(content) > max_length:
                content = content[:max_length] + "..."
            
            # Add fact with source
            context += f"Fact: {content}\n"
            
            # Add source and URL
            source = random_fact.get('source', 'Wikipedia')
            url = random_fact.get('url', f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}")
            context += f"Source: {source} | URL: {url}\n\n"
            
            return context
        except Exception as e:
            print(f"Error generating Wikipedia context: {str(e)}")
            return f"There was an error retrieving Wikipedia information about {query}."

if __name__ == "__main__":
    # Test the WikiFetcher
    wiki_fetcher = WikiFetcher()
    
    # Test topics
    test_topics = ["Artificial Intelligence", "Climate Change", "Space Exploration"]
    
    for topic in test_topics:
        print(f"\nFetching facts about: {topic}")
        facts = wiki_fetcher.get_wiki_facts(topic, count=2)
        
        if facts:
            for i, fact in enumerate(facts, 1):
                print(f"\nFact {i}:")
                print(f"Content: {fact['content'][:150]}...")
                print(f"Source: {fact['source']}")
                print(f"URL: {fact['url']}")
        else:
            print(f"No facts found for {topic}")
