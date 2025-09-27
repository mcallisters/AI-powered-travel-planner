import os
import json
import re
from datetime import datetime
from typing import Tuple, Dict, Any
from tavily import TavilyClient
import openai
import gradio as gr

# ================================
# Environment Variables
# ================================
TAVILY_KEY: str = os.getenv("TAVILY_API_KEY", "")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

# Initialize clients
if TAVILY_KEY:
    tavily_client: TavilyClient = TavilyClient(api_key=TAVILY_KEY)
if OPENAI_API_KEY:
    openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

# ================================
# Core Functions
# ================================

def transcribe_audio(audio_file_path: str) -> str:
    """
    Transcribe an audio file using OpenAI Whisper.
    """
    with open(audio_file_path, "rb") as audio_file:
        transcription = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcription.text

def extract_trip_details_from_text(user_text: str) -> Dict[str, Any]:
    """
    Extract structured trip details from a natural language description using GPT-4.
    """
    system_prompt: str = f"""
    You are a travel assistant. Extract trip details from the text and return a JSON object:
    {{
        "destination": "City, Country",
        "departure_city": "City or 'Not specified'",
        "start_date": "YYYY-MM-DD or null",
        "end_date": "YYYY-MM-DD or null",
        "duration_nights": number or null,
        "budget": string or null,
        "preferences": ["list of preferences"],
        "trip_type": "vacation/business/etc"
    }}
    Today is {datetime.now().strftime("%Y-%m-%d")}.
    Return ONLY the JSON object.
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ],
        temperature=0.1,
        max_tokens=500
    )
    return json.loads(response.choices[0].message.content)

def normalize_price(text: str) -> float | None:
    """
    Extract a price from text and return as float. Returns None if no price found.
    """
    match = re.search(r"\$([\d,]+)", str(text))
    return float(match.group(1).replace(",", "")) if match else None

def search_travel_info(destination: str, departure: str = "San Francisco", start_date: str | None = None, end_date: str | None = None) -> Dict[str, list]:
    """
    Search flights, hotels, cars, and points of interest using Tavily API.
    """
    results: dict = {"flights": [], "hotels": [], "cars": [], "pois": []}

    # Flights
    flight_query: str = f"Flights from {departure} to {destination}"
    if start_date and end_date:
        flight_query += f" {start_date} to {end_date}"
    flight_results = tavily_client.search(flight_query, search_depth="advanced")
    for r in flight_results.get("results", [])[:3]:
        results["flights"].append({
            "name": r.get("title", "Unknown"),
            "url": r.get("url", ""),
            "snippet": r.get("content", ""),
            "price": normalize_price(r.get("content", ""))
        })

    # Hotels
    hotel_query: str = f"Hotels in {destination}"
    if start_date and end_date:
        hotel_query += f" {start_date} to {end_date}"
    hotel_results = tavily_client.search(hotel_query, search_depth="advanced")
    for r in hotel_results.get("results", [])[:3]:
        results["hotels"].append({
            "name": r.get("title", "Unknown"),
            "url": r.get("url", ""),
            "snippet": r.get("content", ""),
            "price": normalize_price(r.get("content", ""))
        })

    # Cars
    car_query: str = f"Car rentals in {destination}"
    car_results = tavily_client.search(car_query, search_depth="advanced")
    for r in car_results.get("results", [])[:3]:
        results["cars"].append({
            "name": r.get("title", "Unknown"),
            "url": r.get("url", ""),
            "snippet": r.get("content", ""),
            "price": normalize_price(r.get("content", ""))
        })

    # Points of Interest
    poi_query: str = f"Top attractions in {destination}"
    poi_results = tavily_client.search(poi_query, search_depth="advanced")
    for r in poi_results.get("results", [])[:5]:
        results["pois"].append({
            "name": r.get("title", "Unknown"),
            "url": r.get("url", ""),
            "snippet": r.get("content", "")
        })

    return results

def generate_trip_plan(trip_details: dict, search_results: dict) -> str:
    """
    Generate a detailed trip plan using GPT-4.
    """
    prompt: str = f"""
    Create a comprehensive trip plan using the following information:

    TRIP DETAILS:
    {json.dumps(trip_details, indent=2)}

    SEARCH RESULTS:
    {json.dumps(search_results, indent=2, default=str)}
    
    Include sections: Overview, Flights, Hotels, Cars, Attractions, Budget, Tips.
    Format clearly with headings and bullet points.
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2500
    )
    return response.choices[0].message.content

# ================================
# Gradio Processing Functions
# ================================

def process_audio_input(gradio_audio_filepath: str) -> Tuple[str, str, str]:
    """
    Process uploaded or recorded audio and generate a trip plan.
    Returns:
    (transcription_text, trip_details_json, trip_plan_text)
    """
    transcription_text: str = transcribe_audio(gradio_audio_filepath)
    trip_details: dict = extract_trip_details_from_text(transcription_text)
    search_results: dict = search_travel_info(
        destination=trip_details.get("destination", ""),
        departure=trip_details.get("departure_city", "San Francisco"),
        start_date=trip_details.get("start_date"),
        end_date=trip_details.get("end_date")
    )
    trip_plan_text: str = generate_trip_plan(trip_details, search_results)
    return transcription_text, json.dumps(trip_details, indent=2), trip_plan_text

def process_text_input(user_text: str) -> Tuple[str, str]:
    """
    Process typed text and generate a trip plan.
    Returns:
    (trip_details_json, trip_plan_text)
    """
    trip_details: dict = extract_trip_details_from_text(user_text)
    search_results: dict = search_travel_info(
        destination=trip_details.get("destination", ""),
        departure=trip_details.get("departure_city", "San Francisco"),
        start_date=trip_details.get("start_date"),
        end_date=trip_details.get("end_date")
    )
    trip_plan_text: str = generate_trip_plan(trip_details, search_results)
    return json.dumps(trip_details, indent=2), trip_plan_text

# ================================
# Gradio Interface
# ================================

def create_interface() -> gr.Blocks:
    """
    Build the Gradio interface for audio and text trip planning.
    """
    with gr.Blocks(title="🌴 AI Travel Planner") as app:

        gr.Markdown("# 🌴 AI Travel Planner\nUpload audio or type text to generate a trip plan.")

        with gr.Tabs():
            # Audio Tab
            with gr.TabItem("🎤 Voice Input"):
                audio_input = gr.Audio(sources=["microphone", "upload"], type="filepath", label="Audio Input")
                transcription_output = gr.Textbox(label="📝 Transcription", lines=4, interactive=False)
                trip_details_output = gr.Textbox(label="🔍 Trip Details (JSON)", lines=8, interactive=False)
                trip_plan_output = gr.Textbox(label="🌟 Trip Plan", lines=20, interactive=False)
                process_audio_btn = gr.Button("Generate Trip Plan")
                process_audio_btn.click(
                    fn=process_audio_input,
                    inputs=[audio_input],
                    outputs=[transcription_output, trip_details_output, trip_plan_output]
                )

            # Text Tab
            with gr.TabItem("✍️ Text Input"):
                text_input = gr.Textbox(label="Type Your Trip Plans", lines=5)
                text_trip_details = gr.Textbox(label="🔍 Trip Details (JSON)", lines=8, interactive=False)
                text_trip_plan = gr.Textbox(label="🌟 Trip Plan", lines=20, interactive=False)
                process_text_btn = gr.Button("Generate Trip Plan")
                process_text_btn.click(
                    fn=process_text_input,
                    inputs=[text_input],
                    outputs=[text_trip_details, text_trip_plan]
                )

    return app

# ================================
# Launch Application
# ================================

if __name__ == "__main__":
    app = create_interface()
    app.launch(server_name="0.0.0.0", server_port=7860)
