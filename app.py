import os
import re
import json
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional
from pathlib import Path
from io import BytesIO

import streamlit as st
import requests
from dotenv import load_dotenv
from openai import OpenAI
from tavily import TavilyClient
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.units import inch

# ================================
# Load Environment Variables
# ================================

try:
    script_dir = Path(__file__).parent if '__file__' in globals() else Path.cwd()

    # Load environment variables
    load_dotenv(script_dir / "TAVILY_API_KEY.env")
    load_dotenv(script_dir / "OPENAI_API_KEY.env")
    load_dotenv(script_dir / "PEXELS_API_KEY.env")

    TAVILY_KEY = os.getenv("TAVILY_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    PEXELS_KEY = os.getenv("PEXELS_API_KEY")

    # Validate API keys
    required_keys = [
        (TAVILY_KEY, "TAVILY_API_KEY"),
        (OPENAI_API_KEY, "OPENAI_API_KEY"),
    ]

    missing_keys = [name for key, name in required_keys if not key]

    if missing_keys:
        st.error(f"Missing API keys: {', '.join(missing_keys)}. Please check your .env files.")
        st.info(f"Looking for .env files in: {script_dir}")
        st.stop()

    # Pexels is optional
    if not PEXELS_KEY:
        st.warning("PEXELS_API_KEY not found. Images will not be displayed.")

    # ================================
    # Initialize Clients
    # ================================

    tavily_client = TavilyClient(api_key=TAVILY_KEY)
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    
except Exception as e:
    st.error(f"Initialization error: {str(e)}")
    st.stop()

# ================================
# Helper Functions
# ================================
def get_destination_image(destination: str) -> Optional[str]:
    """Fetch image URL from Pexels API"""
    if not PEXELS_KEY:
        return None
    try:
        url = f"https://api.pexels.com/v1/search?query={destination} travel&per_page=1"
        headers = {"Authorization": PEXELS_KEY}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('photos'):
                return data['photos'][0]['src']['large']
    except Exception:
        pass
    return None

def download_image(image_url: str) -> Optional[BytesIO]:
    try:
        response = requests.get(image_url, timeout=10)
        if response.status_code == 200:
            return BytesIO(response.content)
    except Exception:
        pass
    return None

def normalize_price(text: str) -> Optional[float]:
    match = re.search(r"\$([\d,]+)", str(text))
    return float(match.group(1).replace(",", "")) if match else None

def search_travel_info(destination: str, departure: str = "San Francisco",
                       start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, list]:
    results: dict = {"flights": [], "hotels": [], "cars": [], "pois": []}

    # Flights
    flight_results = tavily_client.search(f"Flights from {departure} to {destination} {start_date or ''} to {end_date or ''}", search_depth="advanced")
    for r in flight_results.get("results", [])[:3]:
        results["flights"].append({
            "name": r.get("title", "Unknown"),
            "url": r.get("url", ""),
            "snippet": r.get("content", ""),
            "price": normalize_price(r.get("content", ""))
        })

    # Hotels
    hotel_results = tavily_client.search(f"Hotels in {destination} {start_date or ''} to {end_date or ''}", search_depth="advanced")
    for r in hotel_results.get("results", [])[:3]:
        results["hotels"].append({
            "name": r.get("title", "Unknown"),
            "url": r.get("url", ""),
            "snippet": r.get("content", ""),
            "price": normalize_price(r.get("content", ""))
        })

    # Cars
    car_results = tavily_client.search(f"Car rentals in {destination}", search_depth="advanced")
    for r in car_results.get("results", [])[:3]:
        results["cars"].append({
            "name": r.get("title", "Unknown"),
            "url": r.get("url", ""),
            "snippet": r.get("content", "")
        })

    # Attractions
    poi_results = tavily_client.search(f"Top attractions in {destination}", search_depth="advanced")
    for r in poi_results.get("results", [])[:5]:
        results["pois"].append({
            "name": r.get("title", "Unknown"),
            "url": r.get("url", ""),
            "snippet": r.get("content", "")
        })

    return results

def generate_trip_plan(trip_details: dict, search_results: dict) -> str:
    prompt = f"""
    Create a detailed trip plan for a {trip_details.get('duration_nights')} night trip using:
    TRIP DETAILS:
    {json.dumps(trip_details, indent=2)}
    SEARCH RESULTS:
    {json.dumps(search_results, indent=2, default=str)}

    Structure it by day (Day 1, Day 2, etc.) and include an Overview, Flights, Hotels, Cars, Attractions, Budget, and Tips.
    Use markdown-style headings.
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2500
    )
    return response.choices[0].message.content

def generate_pdf(trip_details: dict, trip_plan: str, image_bytes: Optional[BytesIO] = None) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = [Paragraph(f"Travel Itinerary: {trip_details.get('destination')}", styles['Title'])]

    if image_bytes:
        elements.append(RLImage(image_bytes, width=5*inch, height=3*inch))

    elements.append(Spacer(1, 12))
    details = f"""
    <b>From:</b> {trip_details.get('departure_city')}<br/>
    <b>Dates:</b> {trip_details.get('start_date')} - {trip_details.get('end_date')}<br/>
    <b>Duration:</b> {trip_details.get('duration_nights')} nights<br/>
    <b>Travelers:</b> {trip_details.get('travelers')}<br/>
    <b>Budget:</b> {trip_details.get('budget')}<br/>
    """
    elements.append(Paragraph(details, styles['Normal']))
    elements.append(Spacer(1, 12))

    for line in trip_plan.splitlines():
        if line.startswith("##"):
            elements.append(Paragraph(line.replace("##", ""), styles['Heading2']))
        elif line.startswith("- "):
            elements.append(Paragraph("• " + line[2:], styles['Normal']))
        else:
            elements.append(Paragraph(line, styles['Normal']))
        elements.append(Spacer(1, 6))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ================================
# Streamlit UI
# ================================
def main():
    st.set_page_config(page_title="AI Travel Planner", layout="wide")
    
    st.markdown("<h1 style='text-align:center; color:#0066CC'>✈️ AI Powered Travel Planner</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#0066CC'>Create personalized travel plans using AI and real-time data</p>", unsafe_allow_html=True)

    # Add custom CSS for 3D input styling
    st.markdown("""
        <style>
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stDateInput > div > div > input,
        .stSelectbox > div > div > select,
        .stMultiSelect > div > div {
            box-shadow: inset 2px 2px 5px rgba(0,0,0,0.2), 
                        inset -2px -2px 5px rgba(255,255,255,0.7);
            border: 1px solid #ccc;
            border-radius: 8px;
            background: linear-gradient(145deg, #f0f0f0, #ffffff);
        }
        
        /* Container styling for the form area */
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
            background: linear-gradient(145deg, #f5f5f5, #e8e8e8);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 5px 5px 15px rgba(0,0,0,0.1),
                        -5px -5px 15px rgba(255,255,255,0.7);
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize session state for page navigation
    if 'page' not in st.session_state:
        st.session_state.page = 1
    
    # Initialize form data in session state
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}

    # Progress indicator
    progress_col1, progress_col2, progress_col3 = st.columns(3)
    with progress_col1:
        st.markdown(f"**{'✅' if st.session_state.page >= 1 else '⭕'} Step 1: Location & Dates**")
    with progress_col2:
        st.markdown(f"**{'✅' if st.session_state.page >= 2 else '⭕'} Step 2: Budget & Style**")
    with progress_col3:
        st.markdown(f"**{'✅' if st.session_state.page >= 3 else '⭕'} Step 3: Preferences**")
    
    st.markdown("---")

    # PAGE 1: Destination and Dates
    if st.session_state.page == 1:
        with st.container():
            _, center_col, _ = st.columns([1, 2, 1])
            with center_col:
                st.subheader("📍 Where and When?")
                
                destination = st.text_input("Destination City/Country", 
                                          value=st.session_state.form_data.get('destination', ''),
                                          placeholder="e.g., Tokyo, Japan")
                origin = st.text_input("Origin City (Optional)", 
                                     value=st.session_state.form_data.get('origin', ''),
                                     placeholder="e.g., San Francisco, USA")
                
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Start Date", 
                                             value=st.session_state.form_data.get('start_date', date.today() + timedelta(days=30)))
                with col2:
                    end_date = st.date_input("End Date", 
                                           value=st.session_state.form_data.get('end_date', date.today() + timedelta(days=37)))
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("Next ➡️", use_container_width=True):
                    if not destination or end_date <= start_date:
                        st.error("Please enter a valid destination and date range.")
                    else:
                        st.session_state.form_data['destination'] = destination
                        st.session_state.form_data['origin'] = origin
                        st.session_state.form_data['start_date'] = start_date
                        st.session_state.form_data['end_date'] = end_date
                        st.session_state.page = 2
                        st.rerun()

    # PAGE 2: Budget and Travel Style
    elif st.session_state.page == 2:
        with st.container():
            _, center_col, _ = st.columns([1, 2, 1])
            with center_col:
                st.subheader("💰 Budget & Travel Style")
                
                budget = st.number_input("Budget (USD)", 
                                       min_value=100, 
                                       max_value=50000, 
                                       value=st.session_state.form_data.get('budget', 2000), 
                                       step=100)
                travelers = st.number_input("Number of Travelers", 
                                          min_value=1, 
                                          max_value=10, 
                                          value=st.session_state.form_data.get('travelers', 1))
                travel_style = st.selectbox("Travel Style", 
                                          ["Budget", "Mid-range", "Luxury", "Backpacker", "Family-friendly"],
                                          index=["Budget", "Mid-range", "Luxury", "Backpacker", "Family-friendly"].index(
                                              st.session_state.form_data.get('travel_style', 'Mid-range')))
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("⬅️ Back", use_container_width=True):
                        st.session_state.form_data['budget'] = budget
                        st.session_state.form_data['travelers'] = travelers
                        st.session_state.form_data['travel_style'] = travel_style
                        st.session_state.page = 1
                        st.rerun()
                with col2:
                    if st.button("Next ➡️", use_container_width=True):
                        st.session_state.form_data['budget'] = budget
                        st.session_state.form_data['travelers'] = travelers
                        st.session_state.form_data['travel_style'] = travel_style
                        st.session_state.page = 3
                        st.rerun()

    # PAGE 3: Interests and Preferences
    elif st.session_state.page == 3:
        with st.container():
            _, center_col, _ = st.columns([1, 2, 1])
            with center_col:
                st.subheader("🎯 Your Preferences")
                
                interests = st.multiselect("Interests", 
                                         ["Culture", "Nature", "Food", "History", "Adventure", "Relaxation", "Nightlife", "Shopping"], 
                                         default=st.session_state.form_data.get('interests', ["Culture", "Food"]))
                activity_level = st.selectbox("Activity Level", 
                                            ["Relaxed", "Moderate", "Active", "Very Active"],
                                            index=["Relaxed", "Moderate", "Active", "Very Active"].index(
                                                st.session_state.form_data.get('activity_level', 'Moderate')))
                food_preferences = st.multiselect("Food Preferences", 
                                                ["Local Cuisine", "International", "Vegetarian", "Vegan", "Fine Dining", "Street Food"], 
                                                default=st.session_state.form_data.get('food_preferences', ["Local Cuisine"]))
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("⬅️ Back", use_container_width=True):
                    st.session_state.form_data['interests'] = interests
                    st.session_state.form_data['activity_level'] = activity_level
                    st.session_state.form_data['food_preferences'] = food_preferences
                    st.session_state.page = 2
                    st.rerun()
                
                if st.button("🚀 Generate Trip Plan", use_container_width=True, type="primary"):
                    st.session_state.form_data['interests'] = interests
                    st.session_state.form_data['activity_level'] = activity_level
                    st.session_state.form_data['food_preferences'] = food_preferences
                    
                    # Build trip details from session state
                    trip_details = {
                        'destination': st.session_state.form_data['destination'],
                        'departure_city': st.session_state.form_data['origin'] or "San Francisco",
                        'start_date': st.session_state.form_data['start_date'].strftime("%Y-%m-%d"),
                        'end_date': st.session_state.form_data['end_date'].strftime("%Y-%m-%d"),
                        'duration_nights': (st.session_state.form_data['end_date'] - st.session_state.form_data['start_date']).days,
                        'budget': f"${st.session_state.form_data['budget']:,.2f}",
                        'travelers': st.session_state.form_data['travelers'],
                        'preferences': st.session_state.form_data['interests'],
                        'trip_type': f"{st.session_state.form_data['travel_style']} {st.session_state.form_data['activity_level']}",
                        'food_preferences': st.session_state.form_data['food_preferences'],
                    }

                    with st.spinner("Generating itinerary..."):
                        image_url = get_destination_image(trip_details['destination'])
                        image_bytes = download_image(image_url) if image_url else None
                        search_results = search_travel_info(trip_details['destination'], 
                                                          trip_details['departure_city'],
                                                          trip_details['start_date'], 
                                                          trip_details['end_date'])
                        trip_plan = generate_trip_plan(trip_details, search_results)
                        
                        st.subheader("🗺️ Your Travel Itinerary")
                        if image_url:
                            st.markdown(f"""
                                <div style="
                                    border: 8px solid #0066CC;
                                    border-radius: 15px;
                                    box-shadow: 0 8px 16px rgba(0,0,0,0.3);
                                    padding: 10px;
                                    background: white;
                                    max-width: 100%;
                                    margin: 20px auto;
                                ">
                                    <img src="{image_url}" style="
                                        width: 100%;
                                        border-radius: 8px;
                                        display: block;
                                    ">
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.info("No image available for this destination")
                        
                        st.markdown(trip_plan)
                        
                        pdf_buffer = generate_pdf(trip_details, trip_plan, image_bytes)
                        st.download_button("📥 Download Itinerary as PDF", pdf_buffer,
                                         file_name=f"{trip_details['destination'].replace(', ', '_')}_itinerary.pdf",
                                         mime="application/pdf")
                        
                        # Add button to start over
                        if st.button("✨ Plan Another Trip"):
                            st.session_state.page = 1
                            st.session_state.form_data = {}
                            st.rerun()


if __name__ == "__main__":
    main()