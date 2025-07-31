import streamlit as st
import pandas as pd
import base64
import PyPDF2
import io
import requests
import googlemaps
from datetime import datetime
from geopy.distance import geodesic
import time

# Set up page
st.set_page_config(page_title="HealthMate AI", layout="centered")
st.title("🩺 HealthMate AI")
st.markdown("Helping you find the right doctor based on your symptoms or medical reports.")

# Google Maps API Key
gmaps_api_key = "AIzaSyAbRuVkKJ9BHBnWgn_J7DFVjv61q0AtAQI"
gmaps = googlemaps.Client(key="AIzaSyAbRuVkKJ9BHBnWgn_J7DFVjv61q0AtAQI")

# Doctor info sample database
doctor_data = [
    {"name": "Dr. A. Sharma", "specialty": "General Physician", "experience": 10, "location": "Pune", "photo": "https://randomuser.me/api/portraits/men/1.jpg"},
    {"name": "Dr. B. Mehta", "specialty": "Cardiologist", "experience": 15, "location": "Pune", "photo": "https://randomuser.me/api/portraits/men/2.jpg"},
    {"name": "Dr. C. Rao", "specialty": "Dermatologist", "experience": 8, "location": "Pune", "photo": "https://randomuser.me/api/portraits/women/1.jpg"},
    {"name": "Dr. D. Kapoor", "specialty": "ENT Specialist", "experience": 6, "location": "Pune", "photo": "https://randomuser.me/api/portraits/men/3.jpg"},
    {"name": "Dr. E. Patel", "specialty": "Orthopedic", "experience": 12, "location": "Pune", "photo": "https://randomuser.me/api/portraits/men/4.jpg"},
    {"name": "Dr. F. Iyer", "specialty": "Gastroenterologist", "experience": 9, "location": "Pune", "photo": "https://randomuser.me/api/portraits/women/2.jpg"},
    {"name": "Dr. G. Nair", "specialty": "Neurologist", "experience": 11, "location": "Pune", "photo": "https://randomuser.me/api/portraits/men/5.jpg"},
    {"name": "Dr. H. Verma", "specialty": "Urologist", "experience": 13, "location": "Pune", "photo": "https://randomuser.me/api/portraits/men/6.jpg"},
    {"name": "Dr. I. Desai", "specialty": "Gynecologist", "experience": 14, "location": "Pune", "photo": "https://randomuser.me/api/portraits/women/3.jpg"},
    {"name": "Dr. J. Chatterjee", "specialty": "Ophthalmologist", "experience": 7, "location": "Pune", "photo": "https://randomuser.me/api/portraits/women/4.jpg"},
]

# Extended symptom-to-specialist mapping
symptom_doctor_map = {
    "fever": "General Physician",
    "cold": "General Physician",
    "cough": "General Physician",
    "headache": "General Physician",
    "fatigue": "General Physician",
    "body ache": "General Physician",
    "chest pain": "Cardiologist",
    "palpitations": "Cardiologist",
    "shortness of breath": "Cardiologist",
    "high bp": "Cardiologist",
    "low bp": "Cardiologist",
    "skin rash": "Dermatologist",
    "itching": "Dermatologist",
    "acne": "Dermatologist",
    "psoriasis": "Dermatologist",
    "eczema": "Dermatologist",
    "ear pain": "ENT Specialist",
    "hearing loss": "ENT Specialist",
    "sore throat": "ENT Specialist",
    "nasal congestion": "ENT Specialist",
    "joint pain": "Orthopedic",
    "back pain": "Orthopedic",
    "swelling": "Orthopedic",
    "fracture": "Orthopedic",
    "abdominal pain": "Gastroenterologist",
    "nausea": "Gastroenterologist",
    "diarrhea": "Gastroenterologist",
    "vomiting": "Gastroenterologist",
    "constipation": "Gastroenterologist",
    "dizziness": "Neurologist",
    "numbness": "Neurologist",
    "memory loss": "Neurologist",
    "seizure": "Neurologist",
    "urinary issues": "Urologist",
    "kidney pain": "Urologist",
    "frequent urination": "Urologist",
    "menstrual issues": "Gynecologist",
    "pregnancy": "Gynecologist",
    "pcos": "Gynecologist",
    "vision loss": "Ophthalmologist",
    "eye redness": "Ophthalmologist",
    "eye pain": "Ophthalmologist",
}

# Animation confetti style
def show_confetti():
    for i in range(10):
        st.markdown(f"{'💊 '*((10-i)%10)}")
        time.sleep(0.05)

# Get user location automatically
st.subheader("📍 Get Location")
location_btn = st.button("📌 Detect My Location Automatically")
user_latlon = None
if location_btn:
    try:
        ip_req = requests.get("https://ipinfo.io/json")
        location_data = ip_req.json()
        lat, lon = map(float, location_data['loc'].split(","))
        user_latlon = (lat, lon)
        st.success(f"Detected Location: {location_data['city']}, {location_data['region']}")
    except:
        st.error("Failed to detect location.")

# Input methods
st.subheader("💬 Describe Your Symptom")
symptom_input = st.text_input("Type your symptom(s), like chest pain or fever")
symptom_choice = st.selectbox("Or choose from list", ["Select"] + sorted(symptom_doctor_map.keys()))

# Blood report PDF upload
st.subheader("📄 Upload PDF Report")
uploaded_pdf = st.file_uploader("Upload your blood report PDF", type=["pdf"])

# Manual blood values form
st.subheader("📝 Enter Blood Values Manually")
col1, col2, col3 = st.columns(3)
with col1:
    haemoglobin = st.text_input("Haemoglobin (g/dL)")
with col2:
    bp = st.text_input("Blood Pressure (mmHg)")
with col3:
    sugar = st.text_input("Blood Sugar (mg/dL)")

if st.button("🔍 Analyze and Find Doctor"):
    matched_specialty = None

    if symptom_input:
        for keyword in symptom_doctor_map:
            if keyword in symptom_input.lower():
                matched_specialty = symptom_doctor_map[keyword]
                break

    if not matched_specialty and symptom_choice != "Select":
        matched_specialty = symptom_doctor_map.get(symptom_choice)

    if not matched_specialty and uploaded_pdf:
        pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        if "haemoglobin" in text.lower() or "hb" in text.lower():
            matched_specialty = "General Physician"

    if not matched_specialty and (haemoglobin or bp or sugar):
        matched_specialty = "General Physician"

    if matched_specialty:
        show_confetti()
        st.success(f"🎯 Recommended Specialist: {matched_specialty}")

        if user_latlon:
            st.subheader("Nearby Doctors")
            for doc in doctor_data:
                if doc["specialty"] == matched_specialty:
                    place_result = gmaps.places(query=f"{doc['name']} {doc['location']}")
                    if place_result['results']:
                        doc_loc = place_result['results'][0]['geometry']['location']
                        distance = geodesic(user_latlon, (doc_loc['lat'], doc_loc['lng'])).km
                        with st.container():
                            st.image(doc['photo'], width=70)
                            st.markdown(f"**Dr. {doc['name']}**")
                            st.markdown(f"Specialty: {doc['specialty']}")
                            st.markdown(f"Experience: {doc['experience']} years")
                            st.markdown(f"Distance: {round(distance, 2)} km")
                            st.markdown(f"📞 [Call Clinic](tel:+91-9999999999)")
                            st.markdown(f"📅 [Book Appointment](#) (mock link)")
                    else:
                        st.warning(f"Location not found for {doc['name']}")
        else:
            st.info("Location not available. Enable location detection above to find nearby doctors.")
    else:
        st.error("Could not identify the right doctor. Please check your input.")

st.markdown("---")
st.markdown("📞 **Emergency Contact:** 102 (Ambulance) | 108 (Medical Emergency)")
