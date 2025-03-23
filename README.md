# Twitter Posting Agent

![Image](https://github.com/user-attachments/assets/962b1a63-cd75-4aff-aa63-761347be5ac0)

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Components](#components)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Introduction
The Twitter Posting Agent is an innovative tool designed to streamline and automate the process of generating and posting tweets. Leveraging advanced AI models, this application integrates seamlessly with various data sources, including news articles and Wikipedia, to craft informative and engaging content tailored for Twitter audiences. 

With features that support both scheduled and manual tweet posting, the Twitter Posting Agent empowers users to maintain an active and dynamic social media presence effortlessly. Additionally, the tool includes robust document processing capabilities, enabling users to retrieve and utilize context from a variety of document formats, enhancing the depth and relevance of the generated tweets.

Whether you're a social media manager looking to optimize your workflow or a developer interested in AI-driven content creation, the Twitter Posting Agent offers a comprehensive solution to meet your needs.

## Features
- Automated tweet generation using AI models.
- Scheduled and manual tweet posting.
- Integration with news and Wikipedia for context-rich tweets.
- Document processing and context retrieval.

## Installation
1. Clone the repository.
2. Install the required packages using `pip install -r requirements.txt`.
3. Set up your environment variables in a `.env` file.

## Usage
- Run the application using Streamlit to access the web interface.
- Use the interface to generate, schedule, and post tweets.

## Components

### TweetPoster
Located in `tweet_poster.py`, this class handles the posting of tweets to Twitter using the Tweepy library.

### TwitterAgent
Found in `twitter_agent.py`, this script sets up the Streamlit interface and manages the interaction between different components.

### TweetGenerator
Defined in `tweet_generator.py`, this class uses the ChatGroq language model to generate tweets based on various contexts.

### DocumentHandler
Implemented in `document_handler.py`, this class processes documents and retrieves context using a local vector database and Hugging Face embeddings.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any bugs or feature requests.

## License
This project is licensed under the MIT License.

## Contact
For any inquiries, please contact the project maintainers.
