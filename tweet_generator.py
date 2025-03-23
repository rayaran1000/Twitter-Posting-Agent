import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

load_dotenv()

class TweetGenerator:
    def __init__(self):
        """Initialize the TweetGenerator with ChatGroq LLM."""
        # Get API key from environment variables
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY must be set in your .env file")
        
        # Initialize ChatGroq
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        self.groq = ChatGroq(
            groq_api_key=self.groq_api_key,
            model_name="llama3-70b-8192",  # You can change this to your preferred model
            temperature=0.7,
            callback_manager=callback_manager,
            streaming=False
        )
    
    def generate_tweet(self, topic, news_context=None, wiki_context=None):
        """
        Generate a tweet based on the provided topic and optional contexts.
        
        Args:
            topic: The main topic for the tweet
            news_context: Optional context from news articles
            wiki_context: Optional context from Wikipedia
            
        Returns:
            String: The generated tweet
        """
        system_message = """You are a professional social media manager who specializes in creating 
        engaging tweets that get high engagement. Your tweets are informative, relevant, and 
        include appropriate hashtags. Keep tweets under 280 characters."""
        
        # Build the human message based on available contexts
        if news_context and wiki_context:
            # Both news and wiki contexts available
            human_message = f"""Create an engaging tweet about {topic} that combines recent news with 
            interesting facts. The tweet should be informative yet conversational.
            
            Here's some recent news on the topic:
            {news_context}
            
            Here are some interesting facts:
            {wiki_context}
            
            Make the tweet sound natural and include 1-3 relevant hashtags. 
            Keep it under 280 characters. Only return the tweet text.
            """
        elif news_context:
            # Only news context available
            human_message = f"""Create an engaging tweet about {topic} based on recent news.
            
            Here's some recent news on the topic:
            {news_context}
            
            Make the tweet sound informative and timely. Include 1-2 relevant hashtags.
            Keep it under 280 characters. Only return the tweet text.
            """
        elif wiki_context:
            # Only wiki context available
            human_message = f"""Create an engaging tweet about {topic} that shares an interesting fact.
            
            Here are some facts about the topic:
            {wiki_context}
            
            Make the tweet sound interesting and educational. Include 1-2 relevant hashtags.
            Keep it under 280 characters. Only return the tweet text.
            """
        else:
            # No context, default mode
            human_message = f"""Create an engaging tweet about {topic}.
            
            Your tweet should be conversational, interesting, and include 1-2 relevant hashtags.
            Keep it under 280 characters. Only return the tweet text.
            """
        
        # Send messages to ChatGroq
        try:
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=human_message)
            ]
            
            response = self.groq.invoke(messages)
            tweet = response.content.strip()
            
            # Ensure tweet is within character limit
            if len(tweet) > 280:
                tweet = tweet[:277] + "..."
                
            return tweet
        
        except Exception as e:
            print(f"Error generating tweet: {str(e)}")
            return f"Unable to generate tweet about {topic}. Please try again."

    def generate_tweet_with_contexts(self, topic, include_news=False, include_wiki=False, 
                                    news_handler=None, wiki_fetcher=None):
        """
        Convenience method that fetches contexts and generates a tweet.
        """
        if not topic:
            return "Please provide a topic to tweet about."
        
        news_context = None
        wiki_context = None
        
        # Fetch news context if requested
        if include_news and news_handler:
            try:
                news_context = news_handler.get_news_context(query=topic, count=3)
            except Exception as e:
                print(f"Error fetching news context: {str(e)}")
                news_context = f"Unable to retrieve news about {topic}."
        
        # Fetch wiki context if requested
        if include_wiki and wiki_fetcher:
            try:
                wiki_context = wiki_fetcher.get_wiki_context(query=topic, count=2)
            except Exception as e:
                print(f"Error fetching wiki context: {str(e)}")
                wiki_context = f"Unable to retrieve Wikipedia information about {topic}."
        
        # Generate the tweet
        return self.generate_tweet(topic, news_context, wiki_context)

    def generate_tweet_with_document(self, topic, document_context, tweet_style="Informative"):
        """
        Generate a tweet based on document content.
        
        Args:
            topic: The main topic for the tweet
            document_context: Text extracted from the document
            tweet_style: Style of the tweet (Informative, Engaging, Professional, Conversational)
            
        Returns:
            String: The generated tweet
        """
        # Define style-specific tone and characteristics
        style_instructions = {
            "Informative": "Focus on facts and information. Be clear and educational. Include specific insights from the document.",
            "Engaging": "Be attention-grabbing and use compelling language. Ask questions or use strong statements that encourage interaction.",
            "Professional": "Maintain a formal, business-appropriate tone. Focus on industry relevance and value propositions.",
            "Conversational": "Use a friendly, casual tone as if speaking directly to a friend. Use more personal language and potentially first-person perspective."
        }
        
        # Get the specific style instruction, defaulting to Informative
        style_instruction = style_instructions.get(tweet_style, style_instructions["Informative"])
        
        system_message = f"""You are a professional social media manager who specializes in creating 
        engaging tweets that get high engagement. Your tweets are informative, relevant, and 
        include appropriate hashtags. Keep tweets under 280 characters.
        
        For this tweet, use a {tweet_style} style. {style_instruction}"""
        
        human_message = f"""Create an engaging tweet about "{topic}" based on the following document content.
        
        {document_context}
        
        The tweet should highlight key insights related to "{topic}" from the document excerpts.
        Include 1-2 relevant hashtags.
        Keep it under 280 characters. Only return the tweet text.
        """
        
        try:
            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=human_message)
            ]
            
            response = self.groq.invoke(messages)
            tweet = response.content.strip()
            
            # Ensure tweet is within character limit
            if len(tweet) > 280:
                tweet = tweet[:277] + "..."
                
            return tweet
        
        except Exception as e:
            print(f"Error generating document-based tweet: {str(e)}")
            return f"Unable to generate tweet about {topic}. Please try again."


if __name__ == "__main__":
    # Test the TweetGenerator
    generator = TweetGenerator()
    
    # Test with a simple topic
    test_topic = "Artificial Intelligence"
    tweet = generator.generate_tweet(test_topic)
    print(f"\nGenerated tweet about {test_topic}:")
    print(tweet)
    
    # You can add more test cases here if needed
