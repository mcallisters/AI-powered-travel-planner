🌴 AI-Powered Travel Planner

An intelligent travel planning application that uses AI to help you plan your perfect trip. Simply describe your travel plans using voice or text, and get personalized recommendations for flights, hotels, car rentals, and attractions.

The app is built with Gradio, which provides the user-friendly web interface (UI) for interacting with the model.

✨ Features

🎤 Voice Input: Record your travel plans using the microphone or upload an audio file

✍️ Text Input: Type your travel requirements in natural language

🤖 AI Processing: Uses OpenAI GPT-4 to understand and extract trip details

🔍 Real-time Search: Searches for flights, hotels, and car rentals using Tavily API

📋 Comprehensive Plans: Generates detailed itineraries with budget estimates

🎯 Smart Recommendations: Suggests points of interest and activities

🚀 How to Use
Option 1: Voice Input

Click on the "🎤 Voice Input" tab

Use the microphone to record your travel plans or upload an audio file

Describe your destination, travel dates, preferences, and budget

Click "🎯 Plan My Trip from Audio"

Option 2: Text Input

Click on the "✍️ Text Input" tab

Type your travel plans in the text box

Include destination, dates, preferences, and any special requirements

Click "🎯 Plan My Trip from Text"

📝 Example Inputs

"I want to visit Tokyo for a week in March with my family, budget around $4000"

"Plan a romantic weekend in Paris, leaving from New York, mid-range hotels"

"Business trip to London, 3 days, need hotel near financial district"

"Looking for a beach vacation in Mexico, 5-7 days, all-inclusive resorts"

🔧 Technology Stack

Frontend / UI: Gradio
 for the web interface

AI Models:

OpenAI Whisper for audio transcription

OpenAI GPT-4 for natural language processing and trip planning

Search APIs:

Tavily API for real-time travel information

SerpAPI for enhanced search results (optional)

Backend: Python with various libraries for data processing

🔑 Required API Keys

To run this application, you need the following API keys:

Tavily API Key (TAVILY_API_KEY)

Sign up at Tavily.com

Used for real-time travel search

OpenAI API Key (OPENAI_API_KEY)

Get from OpenAI Platform

Used for AI processing and Whisper transcription

SerpAPI Key (SERPAPI_API_KEY) – Optional

Get from SerpAPI

Provides enhanced search results

Setting API Keys in Hugging Face Spaces

Go to your Space settings

Click on "Variables and secrets"

Add the API keys as secrets:

TAVILY_API_KEY

OPENAI_API_KEY

SERPAPI_API_KEY

📁 Project Structure
├── app.py                 # Main Gradio application
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── .env files (local)     # Environment variables (not included in deployment)
    ├── TAVILY_API_KEY.env
    ├── OPENAI_API_KEY.env
    └── SERPAPI_API_KEY.env

🛠️ Local Development

Clone the repository

Install dependencies: pip install -r requirements.txt

Create .env files with your API keys

Run: python app.py

🌐 Deployment on Hugging Face

Fork this repository

Create a new Hugging Face Space

Connect your GitHub repository

Set the required API keys in Space settings

The app will automatically deploy

⚠️ Important Notes

This app requires active API keys to function

Transcription and AI processing require OpenAI credits

Search functionality requires Tavily API access

Some features may be rate-limited based on your API plan

🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve this application.

📄 License

This project is open source and available under the MIT License.
