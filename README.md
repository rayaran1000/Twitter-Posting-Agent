# Twitter Posting Agent

![Image](https://github.com/user-attachments/assets/5f651884-3166-4e58-9863-f21c7d28992c)

## Project Overview

**Twitter Posting Agent** is a web application designed to automate the process of generating and posting tweets. It integrates with various data sources to create informative and engaging content for Twitter. The application includes user authentication, tweet generation, scheduling capabilities, and advanced integration features.

## Features

- **User Authentication**: Secure JWT-based authentication system with role-based access control.
- **Tweet Generation & Management**: Automated tweet generation using AI models with support for scheduling and manual posting.
- **Data Integration**: Integration with news and Wikipedia for context-rich tweets.
- **Document Processing**: Supports document processing and context retrieval using local vector databases and Hugging Face embeddings.
- **Interactive Interface**: Built with Streamlit for a user-friendly web interface.

## Project Structure

### Backend (Python)
- **Core Components**:
  - `tweet_poster.py`: Handles the posting of tweets to Twitter using the Tweepy library.
  - `twitter_agent.py`: Sets up the Streamlit interface and manages the interaction between different components.
  - `tweet_generator.py`: Uses the ChatGroq language model to generate tweets based on various contexts.
  - `document_handler.py`: Processes documents and retrieves context using a local vector database and Hugging Face embeddings.

### Frontend (Streamlit)
- Modern UI built with Streamlit.
- Responsive design for various screen sizes.

## Installation

### Prerequisites
- Python 3.9+
- Node.js (for any additional frontend development)
- Docker (optional)

### Environment Variables
Create a `.env` file with:

```bash
TWITTER_API_KEY=<your-twitter-api-key>
TWITTER_API_SECRET=<your-twitter-api-secret>
GROQ_API_KEY=<your-groq-key>
```

### Local Development Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd twitter-posting-agent
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
streamlit run twitter_agent.py
```

### Docker Deployment

```bash
docker-compose up --build
```

## API Endpoints

### Authentication
- `POST /users/token`: Get access token.
- `POST /users/register`: Register new user.
- `POST /users/login`: Login existing user.

### Tweet Management
- `POST /tweets/generate`: Generate a new tweet.
- `POST /tweets/schedule`: Schedule a tweet for future posting.
- `POST /tweets/post`: Post a tweet immediately.

## Technologies Used

### Backend
- Python
- Tweepy
- Hugging Face
- LangChain

### Frontend
- Streamlit

### Infrastructure
- Docker
- GitHub (for version control)

## Security

- JWT-based authentication
- Role-based access control
- Secure password hashing
- Environment variable protection

## Contributing

Please read our contributing guidelines before submitting pull requests.

## License

This project is licensed under the MIT License.

## Acknowledgments

- Tweepy library for Twitter API integration
- Hugging Face for language models
- Streamlit for the web interface
