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
The Twitter Posting Agent is a tool designed to automate the process of generating and posting tweets. It integrates with various data sources to create informative and engaging content for Twitter.

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
