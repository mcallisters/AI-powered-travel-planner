# 🌴 AI-Powered Travel Planner

An intelligent travel planning application that uses AI to help you plan your perfect trip. Simply describe your travel plans using voice or text, and get personalized recommendations for flights, hotels, car rentals, and attractions.

## ✨ Features

- **🎤 Voice Input**: Record your travel plans using the microphone or upload an audio file  
- **✍️ Text Input**: Type your travel requirements in natural language  
- **🤖 AI Processing**: Uses OpenAI GPT-4 to understand and extract trip details  
- **🔍 Real-time Search**: Searches for flights, hotels, and car rentals using Tavily API  
- **📋 Comprehensive Plans**: Generates detailed itineraries with budget estimates  
- **🎯 Smart Recommendations**: Suggests points of interest and activities  
- **🖥️ UI Built with Gradio**: A clean and interactive web interface powered by [Gradio](https://www.gradio.app)  

## 🚀 How to Use

### Option 1: Voice Input

1. Click on the **"🎤 Voice Input"** tab  
2. Use the microphone to record your travel plans or upload an audio file  
3. Describe your destination, travel dates, preferences, and budget  
4. Click **"🎯 Plan My Trip from Audio"**  

### Option 2: Text Input

1. Click on the **"✍️ Text Input"** tab  
2. Type your travel plans in the text box  
3. Include destination, dates, preferences, and any special requirements  
4. Click **"🎯 Plan My Trip from Text"**  

## 📝 Example Inputs

- "I want to visit Tokyo for a week in March with my family, budget around $4000"  
- "Plan a romantic weekend in Paris, leaving from New York, mid-range hotels"  
- "Business trip to London, 3 days, need hotel near financial district"  
- "Looking for a beach vacation in Mexico, 5-7 days, all-inclusive resorts"  

## 🔧 Technology Stack

- **Frontend**: [Gradio](https://www.gradio.app) for the web interface  
- **AI Models**:  
  - OpenAI Whisper for audio transcription  
  - OpenAI GPT-4 for natural language processing and trip planning  
- **Search APIs**:  
  - Tavily API for real-time travel information  
  - SerpAPI for enhanced search results (optional)  
- **Backend**: Python with various libraries for data processing  

## 🔑 Required API Keys

To run this application, you need the following API keys:

1. **Tavily API Key** (`TAVILY_API_KEY`)  
   - Sign up at [Tavily.com](https://tavily.com)  
   - Used for real-time travel search  

2. **OpenAI API Key** (`OPENAI_API_KEY`)  
   - Get from [OpenAI Platform](https://platform.openai.com)  
   - Used for AI processing and Whisper transcription  

3. **SerpAPI Key** (`SERPAPI_API_KEY`) – *Optional*  
   - Get from [SerpAPI](https://serpapi.com)  
   - Provides enhanced search results  

### Setting API Keys in Hugging Face Spaces

1. Go to your Space settings  
2. Click on **"Variables and secrets"**  
3. Add the API keys as secrets:  
   - `TAVILY_API_KEY`  
   - `OPENAI_API_KEY`  
   - `SERPAPI_API_KEY`  

## 📁 Project Structure

├── app.py # Main Gradio application
├── requirements.txt # Python dependencies
├── README.md # This file
└── .env files (local) # Environment variables (not included in deployment)
├── TAVILY_API_KEY.env
├── OPENAI_API_KEY.env
└── SERPAPI_API_KEY.env


## 🛠️ Local Development

1. Clone the repository  
2. Install dependencies:  

   ```bash
   pip install -r requirements.txt

3. Create .env files with your API keys

4. Run:

python app.py

## 🌐 Deployment on Hugging Face

- Fork this repository
- Create a new Hugging Face Space
- Connect your GitHub repository
- Set the required API keys in Space settings
- The app will automatically deploy

## ⚠️ Important Notes

- This app requires active API keys to function
- Transcription and AI processing require OpenAI credits
- Search functionality requires Tavily API access
- Some features may be rate-limited based on your API plan

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve this application.

📄 License

This project is open source and available under the MIT License.

Happy Travels! 🌍✈️
