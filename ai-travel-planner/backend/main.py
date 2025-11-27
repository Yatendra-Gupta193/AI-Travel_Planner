from flask import Flask, jsonify, request, session
from flask_cors import CORS
import json
from datetime import datetime
import hashlib
import re
import os
# from dotenv import load_dotenv
# import google.generativeai as genai
# from ai_service import ai_planner

# Load environment variables
# load_dotenv()

app = Flask(__name__)
app.secret_key = 'ai_travel_planner_secret_key_2024'
CORS(app, supports_credentials=True)

# Configure Gemini AI (temporarily disabled)
print("⚠️  AI features temporarily disabled. Using mock data for demonstration.")

# In-memory storage
users = []
travel_plans = []

# Helper functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_mobile(mobile):
    pattern = r'^[0-9]{10}$'
    return re.match(pattern, mobile) is not None

def find_user_by_email(email):
    return next((user for user in users if user['email'] == email), None)

def find_user_by_mobile(mobile):
    return next((user for user in users if user['mobile'] == mobile), None)

def is_authenticated():
    return 'user_id' in session

@app.route('/')
def home():
    return jsonify({"message": "Welcome to AI Travel Planner API", "status": "running"})

# Authentication Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    required_fields = ['name', 'password', 'confirm_password']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    if data['password'] != data['confirm_password']:
        return jsonify({"error": "Passwords do not match"}), 400
    
    if 'email' not in data and 'mobile' not in data:
        return jsonify({"error": "Either email or mobile number is required"}), 400
    
    if 'email' in data and data['email']:
        if not validate_email(data['email']):
            return jsonify({"error": "Invalid email format"}), 400
        if find_user_by_email(data['email']):
            return jsonify({"error": "Email already registered"}), 400
    
    if 'mobile' in data and data['mobile']:
        if not validate_mobile(data['mobile']):
            return jsonify({"error": "Invalid mobile number format"}), 400
        if find_user_by_mobile(data['mobile']):
            return jsonify({"error": "Mobile number already registered"}), 400
    
    user = {
        "id": len(users) + 1,
        "name": data['name'],
        "email": data.get('email', ''),
        "mobile": data.get('mobile', ''),
        "password": hash_password(data['password']),
        "created_at": datetime.now().isoformat()
    }
    
    users.append(user)
    session['user_id'] = user['id']
    session['user_name'] = user['name']
    
    return jsonify({
        "message": "User registered successfully",
        "user": {
            "id": user['id'],
            "name": user['name'],
            "email": user['email'],
            "mobile": user['mobile']
        }
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    if 'password' not in data:
        return jsonify({"error": "Password is required"}), 400
    
    if 'email' not in data and 'mobile' not in data:
        return jsonify({"error": "Either email or mobile number is required"}), 400
    
    user = None
    if 'email' in data and data['email']:
        user = find_user_by_email(data['email'])
    elif 'mobile' in data and data['mobile']:
        user = find_user_by_mobile(data['mobile'])
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if user['password'] != hash_password(data['password']):
        return jsonify({"error": "Invalid password"}), 401
    
    session['user_id'] = user['id']
    session['user_name'] = user['name']
    
    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user['id'],
            "name": user['name'],
            "email": user['email'],
            "mobile": user['mobile']
        }
    })

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logout successful"})

@app.route('/api/user', methods=['GET'])
def get_current_user():
    if not is_authenticated():
        return jsonify({"error": "Not authenticated"}), 401
    
    user_id = session['user_id']
    user = next((u for u in users if u['id'] == user_id), None)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "user": {
            "id": user['id'],
            "name": user['name'],
            "email": user['email'],
            "mobile": user['mobile']
        }
    })

# AI Travel Planning Routes
@app.route('/api/generate-plan', methods=['POST'])
def generate_travel_plan():
    """Generate AI-powered travel plan"""
    if not is_authenticated():
        return jsonify({"error": "Authentication required"}), 401

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Validate required fields
    required_fields = ['budget', 'travelers', 'destinations']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        # Generate mock travel plan (AI temporarily disabled)
        ai_plan = generate_mock_travel_plan(data)

        # Create plan record
        plan = {
            "id": len(travel_plans) + 1,
            "user_id": session['user_id'],
            "user_input": data,
            "ai_plan": ai_plan,
            "created_at": datetime.now().isoformat(),
            "type": "ai_generated"
        }

        travel_plans.append(plan)
        return jsonify(plan), 201

    except Exception as e:
        print(f"Error generating travel plan: {e}")
        return jsonify({"error": "Failed to generate travel plan"}), 500

@app.route('/api/plans', methods=['GET'])
def get_plans():
    """Get all travel plans for current user"""
    if not is_authenticated():
        return jsonify({"error": "Authentication required"}), 401

    user_id = session['user_id']
    user_plans = [plan for plan in travel_plans if plan['user_id'] == user_id]
    return jsonify(user_plans)

@app.route('/api/plans/<int:plan_id>', methods=['DELETE'])
def delete_plan(plan_id):
    """Delete a travel plan"""
    if not is_authenticated():
        return jsonify({"error": "Authentication required"}), 401

    global travel_plans
    user_id = session['user_id']

    # Find plan and check ownership
    plan = next((p for p in travel_plans if p['id'] == plan_id and p['user_id'] == user_id), None)
    if not plan:
        return jsonify({"error": "Plan not found or access denied"}), 404

    travel_plans = [p for p in travel_plans if p['id'] != plan_id]
    return jsonify({"message": "Plan deleted successfully"})

# Mock travel plan generator
def generate_mock_travel_plan(user_input):
    """Generate mock travel plan"""
    destinations = user_input.get('destinations', '').split(',')
    main_destination = destinations[0].strip() if destinations else "Amazing Destination"
    budget = int(user_input.get('budget', 1000))
    travelers = int(user_input.get('travelers', 1))

    # Location-specific data
    location_data = get_location_specific_data(main_destination.lower())

    return {
        "destination": {
            "name": location_data['name'],
            "country": location_data['country'],
            "description": location_data['description']
        },
        "itinerary": [
            {
                "day": 1,
                "title": f"Arrival in {location_data['main_city']}",
                "activities": [
                    "Airport/Railway station pickup",
                    "Hotel check-in",
                    f"Visit {location_data['places'][0]}",
                    "Local cuisine dinner"
                ],
                "estimated_cost": 100
            },
            {
                "day": 2,
                "title": f"Explore {location_data['places'][1]}",
                "activities": [
                    f"Early morning visit to {location_data['places'][1]}",
                    f"Explore {location_data['places'][2]}",
                    "Local market shopping",
                    f"Try {location_data['cuisine'][0]}"
                ],
                "estimated_cost": 150
            }
        ],
        "total_estimated_cost": min(budget, budget * 0.95),
        "budget_breakdown": {
            "accommodation": budget * 0.3,
            "transportation": budget * 0.25,
            "food": budget * 0.25,
            "activities": budget * 0.15,
            "miscellaneous": budget * 0.05
        },
        "tips": location_data['tips'][:4],
        "best_time_to_visit": location_data['best_time'],
        "local_cuisine": location_data['cuisine'][:4],
        "cultural_highlights": location_data['culture'][:4],
        "ai_generated": False,
        "note": "This is a sample plan. For AI-generated plans, install required dependencies."
    }

def get_location_specific_data(destination):
    """Get location-specific data"""
    destination = destination.lower().strip()

    # Indian States Database
    if 'uttar pradesh' in destination or 'up' in destination:
        return {
            'name': 'Uttar Pradesh',
            'country': 'India',
            'main_city': 'Lucknow',
            'description': 'The heartland of India with rich cultural heritage',
            'places': ['Taj Mahal (Agra)', 'Varanasi Ghats', 'Mathura-Vrindavan', 'Lucknow'],
            'cuisine': ['Lucknowi Biryani', 'Petha (Agra)', 'Kachori-Sabzi', 'Tunde Kabab'],
            'culture': ['Ganga Aarti at Varanasi', 'Holi at Mathura', 'Mughal Architecture', 'Classical Music'],
            'tips': ['Visit Taj Mahal at sunrise', 'Respect religious customs', 'Try street food safely', 'Book trains in advance'],
            'best_time': 'October to March (Winter season)'
        }
    elif 'rajasthan' in destination:
        return {
            'name': 'Rajasthan',
            'country': 'India',
            'main_city': 'Jaipur',
            'description': 'Land of Kings with magnificent palaces and forts',
            'places': ['Jaipur (Pink City)', 'Udaipur (City of Lakes)', 'Jodhpur (Blue City)', 'Jaisalmer'],
            'cuisine': ['Dal Baati Churma', 'Laal Maas', 'Gatte ki Sabzi', 'Pyaaz Kachori'],
            'culture': ['Folk Music and Dance', 'Camel Safari', 'Palace Architecture', 'Puppet Shows'],
            'tips': ['Carry sunscreen', 'Try camel safari', 'Book heritage hotels', 'Stay hydrated'],
            'best_time': 'October to March (Winter season)'
        }
    else:
        return {
            'name': destination.title(),
            'country': 'Various',
            'main_city': destination.title(),
            'description': f'A wonderful destination - {destination.title()}',
            'places': ['Main City Center', 'Local Attractions', 'Cultural Sites', 'Shopping Areas'],
            'cuisine': ['Local Specialties', 'Traditional Dishes', 'Street Food', 'Regional Delicacies'],
            'culture': ['Local Traditions', 'Cultural Sites', 'Festivals', 'Art and Crafts'],
            'tips': ['Research local customs', 'Try local cuisine', 'Respect traditions', 'Stay safe'],
            'best_time': 'Check local weather patterns'
        }

if __name__ == '__main__':
    print("🚀 Starting AI Travel Planner API...")
    print("📍 Server running on: http://localhost:5000")
    print("⚠️ Using Mock Data (AI dependencies not installed)")
    app.run(debug=True, port=5000)
