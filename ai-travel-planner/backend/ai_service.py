import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class AITravelPlanner:
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.is_configured = self.gemini_api_key and self.gemini_api_key != AIzaSyB4JTTtfomvUnDlIXFep7JvSqmNBpDaGVg
        
        if self.is_configured:
            genai.configure(api_key=self.gemini_api_key)
    
    def generate_travel_plan(self, user_input):
        """Generate travel plan using Gemini AI or mock data"""
        try:
            if self.is_configured:
                return self._generate_ai_plan(user_input)
            else:
                return self._generate_mock_plan(user_input)
        except Exception as e:
            print(f"Error generating plan: {e}")
            return self._generate_mock_plan(user_input)
    
    def _generate_ai_plan(self, user_input):
        """Generate plan using Gemini AI"""
        model = genai.GenerativeModel('gemini-pro')

        destinations = user_input.get('destinations', '')

        prompt = f"""
        Create a detailed travel plan for the following destinations: {destinations}

        IMPORTANT: For each destination mentioned, include the most famous and must-visit places within that region.

        For example:
        - If destination is "Uttar Pradesh" or "UP", include places like Agra (Taj Mahal), Varanasi, Mathura, Vrindavan, Lucknow, Ayodhya, Allahabad
        - If destination is "Rajasthan", include Jaipur, Udaipur, Jodhpur, Jaisalmer, Pushkar, Mount Abu
        - If destination is "Kerala", include Kochi, Munnar, Alleppey, Thekkady, Wayanad
        - If destination is "Goa", include North Goa beaches, South Goa, Old Goa churches, Dudhsagar Falls
        - If destination is "Himachal Pradesh", include Shimla, Manali, Dharamshala, Kasol, Spiti Valley

        Travel Requirements:
        Budget: ${user_input.get('budget', 'Not specified')}
        Travelers: {user_input.get('travelers', 1)} people
        Destinations: {destinations}
        Travel dates: {user_input.get('start_date', 'Flexible')} to {user_input.get('end_date', 'Flexible')}
        Preferences: {user_input.get('preferences', 'General travel')}
        Notes: {user_input.get('notes', 'None')}

        Please provide a comprehensive travel plan in JSON format with this structure:
        {{
            "destination": {{
                "name": "Main destination name",
                "country": "Country",
                "description": "Brief description"
            }},
            "itinerary": [
                {{
                    "day": 1,
                    "title": "Day title",
                    "activities": ["Activity 1", "Activity 2"],
                    "estimated_cost": 100
                }}
            ],
            "accommodation": {{
                "type": "Hotel type",
                "estimated_cost_per_night": 80,
                "recommendations": ["Hotel 1", "Hotel 2"]
            }},
            "transportation": {{
                "type": "Transport type",
                "estimated_cost": 300,
                "recommendations": "Transport tips"
            }},
            "total_estimated_cost": 1000,
            "budget_breakdown": {{
                "accommodation": 300,
                "transportation": 200,
                "food": 250,
                "activities": 200,
                "miscellaneous": 50
            }},
            "tips": ["Tip 1", "Tip 2"],
            "best_time_to_visit": "Season info",
            "local_cuisine": ["Food 1", "Food 2"],
            "cultural_highlights": ["Culture 1", "Culture 2"]
        }}
        
        Make sure the plan fits within ${user_input.get('budget', 1000)} budget.
        """
        
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Extract JSON from response
        if '```json' in response_text:
            json_start = response_text.find('```json') + 7
            json_end = response_text.find('```', json_start)
            response_text = response_text[json_start:json_end]
        elif '{' in response_text:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            response_text = response_text[json_start:json_end]
        
        try:
            plan_data = json.loads(response_text)
            plan_data['ai_generated'] = True
            return plan_data
        except json.JSONDecodeError:
            # If JSON parsing fails, return structured response
            return {
                "destination": {
                    "name": user_input.get('destinations', 'Custom Destination').split(',')[0].strip(),
                    "country": "Various",
                    "description": "AI-generated travel plan"
                },
                "ai_response": response_text,
                "total_estimated_cost": user_input.get('budget', 1000),
                "message": "AI generated a detailed plan. Check ai_response for full details.",
                "ai_generated": True
            }
    
    def _generate_mock_plan(self, user_input):
        """Generate mock plan when AI is not available"""
        destinations = user_input.get('destinations', '').split(',')
        main_destination = destinations[0].strip() if destinations else "Amazing Destination"
        budget = int(user_input.get('budget', 1000))
        travelers = int(user_input.get('travelers', 1))

        # Calculate costs based on travelers
        base_accommodation = 80 * travelers
        base_food = 50 * travelers
        base_activities = 40 * travelers

        # Get location-specific places and activities
        location_data = self._get_location_specific_data(main_destination.lower())
        
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
                    "estimated_cost": base_food + 20
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
                    "estimated_cost": base_activities + base_food
                },
                {
                    "day": 3,
                    "title": f"Cultural Experience at {location_data['places'][3] if len(location_data['places']) > 3 else location_data['places'][0]}",
                    "activities": [
                        f"Visit {location_data['places'][3] if len(location_data['places']) > 3 else location_data['places'][0]}",
                        f"Experience {location_data['culture'][0]}",
                        f"Enjoy {location_data['cuisine'][1]}",
                        "Photography and relaxation"
                    ],
                    "estimated_cost": base_activities + base_food + 30
                }
            ],
            "accommodation": {
                "type": "Mid-range Hotel",
                "estimated_cost_per_night": base_accommodation,
                "recommendations": ["Hotel Paradise", "City Center Inn", "Comfort Lodge"]
            },
            "transportation": {
                "type": "Mixed (Flight + Local Transport)",
                "estimated_cost": min(budget * 0.3, 500),
                "recommendations": "Book flights in advance for better prices. Use local transport for city travel."
            },
            "total_estimated_cost": min(budget, budget * 0.95),
            "budget_breakdown": {
                "accommodation": base_accommodation * 3,
                "transportation": min(budget * 0.3, 500),
                "food": base_food * 3,
                "activities": base_activities * 3,
                "miscellaneous": budget * 0.1
            },
            "tips": location_data['tips'],
            "best_time_to_visit": location_data['best_time'],
            "local_cuisine": location_data['cuisine'],
            "cultural_highlights": location_data['culture'],
            "ai_generated": False,
            "note": "This is a sample plan. For AI-generated personalized plans, please add your Gemini API key to the .env file."
        }

    def _get_location_specific_data(self, destination):
        """Get location-specific tourist places and information"""
        destination = destination.lower().strip()

        # Indian States and Popular Destinations
        location_database = {
            'uttar pradesh': {
                'name': 'Uttar Pradesh',
                'country': 'India',
                'main_city': 'Lucknow',
                'description': 'The heartland of India with rich cultural heritage and historical monuments',
                'places': ['Taj Mahal (Agra)', 'Varanasi Ghats', 'Mathura-Vrindavan', 'Lucknow', 'Ayodhya', 'Allahabad (Prayagraj)', 'Fatehpur Sikri', 'Sarnath'],
                'cuisine': ['Lucknowi Biryani', 'Petha (Agra)', 'Kachori-Sabzi', 'Tunde Kabab', 'Malaiyo', 'Bedai-Jalebi'],
                'culture': ['Ganga Aarti at Varanasi', 'Holi at Mathura', 'Mughal Architecture', 'Classical Music Traditions', 'Kathak Dance', 'Religious Festivals'],
                'tips': ['Visit Taj Mahal at sunrise', 'Respect religious customs at temples', 'Try street food safely', 'Book trains in advance', 'Carry hand sanitizer', 'Dress modestly at religious places'],
                'best_time': 'October to March (Winter season)'
            },
            'up': {
                'name': 'Uttar Pradesh',
                'country': 'India',
                'main_city': 'Lucknow',
                'description': 'The heartland of India with rich cultural heritage and historical monuments',
                'places': ['Taj Mahal (Agra)', 'Varanasi Ghats', 'Mathura-Vrindavan', 'Lucknow', 'Ayodhya', 'Allahabad (Prayagraj)', 'Fatehpur Sikri', 'Sarnath'],
                'cuisine': ['Lucknowi Biryani', 'Petha (Agra)', 'Kachori-Sabzi', 'Tunde Kabab', 'Malaiyo', 'Bedai-Jalebi'],
                'culture': ['Ganga Aarti at Varanasi', 'Holi at Mathura', 'Mughal Architecture', 'Classical Music Traditions', 'Kathak Dance', 'Religious Festivals'],
                'tips': ['Visit Taj Mahal at sunrise', 'Respect religious customs at temples', 'Try street food safely', 'Book trains in advance', 'Carry hand sanitizer', 'Dress modestly at religious places'],
                'best_time': 'October to March (Winter season)'
            },
            'rajasthan': {
                'name': 'Rajasthan',
                'country': 'India',
                'main_city': 'Jaipur',
                'description': 'Land of Kings with magnificent palaces, forts, and desert landscapes',
                'places': ['Jaipur (Pink City)', 'Udaipur (City of Lakes)', 'Jodhpur (Blue City)', 'Jaisalmer (Golden City)', 'Pushkar', 'Mount Abu', 'Bikaner', 'Chittorgarh'],
                'cuisine': ['Dal Baati Churma', 'Laal Maas', 'Gatte ki Sabzi', 'Pyaaz Kachori', 'Ghevar', 'Mawa Kachori'],
                'culture': ['Folk Music and Dance', 'Camel Safari', 'Palace Architecture', 'Puppet Shows', 'Desert Festivals', 'Royal Heritage'],
                'tips': ['Carry sunscreen and water', 'Bargain at local markets', 'Try camel safari in Jaisalmer', 'Book heritage hotels', 'Respect local customs', 'Stay hydrated'],
                'best_time': 'October to March (Winter season)'
            },
            'kerala': {
                'name': 'Kerala',
                'country': 'India',
                'main_city': 'Kochi',
                'description': 'God\'s Own Country with backwaters, hill stations, and pristine beaches',
                'places': ['Alleppey Backwaters', 'Munnar Hill Station', 'Kochi (Fort Kochi)', 'Thekkady (Periyar)', 'Wayanad', 'Kovalam Beach', 'Kumarakom', 'Varkala'],
                'cuisine': ['Kerala Fish Curry', 'Appam with Stew', 'Puttu and Kadala', 'Banana Chips', 'Payasam', 'Karimeen Fish'],
                'culture': ['Kathakali Dance', 'Ayurvedic Treatments', 'Houseboat Experience', 'Spice Plantations', 'Temple Festivals', 'Traditional Architecture'],
                'tips': ['Book houseboat in advance', 'Try Ayurvedic massage', 'Carry mosquito repellent', 'Respect local customs', 'Try fresh coconut water', 'Pack light cotton clothes'],
                'best_time': 'September to March (Post-monsoon and Winter)'
            },
            'goa': {
                'name': 'Goa',
                'country': 'India',
                'main_city': 'Panaji',
                'description': 'Beach paradise with Portuguese heritage and vibrant nightlife',
                'places': ['Baga Beach', 'Calangute Beach', 'Old Goa Churches', 'Dudhsagar Falls', 'Anjuna Beach', 'Palolem Beach', 'Basilica of Bom Jesus', 'Aguada Fort'],
                'cuisine': ['Fish Curry Rice', 'Bebinca', 'Vindaloo', 'Xacuti', 'Feni', 'Prawn Balchao'],
                'culture': ['Portuguese Architecture', 'Beach Shacks', 'Carnival Festival', 'Flea Markets', 'Water Sports', 'Sunset Views'],
                'tips': ['Try water sports', 'Visit flea markets', 'Respect beach rules', 'Try local seafood', 'Book accommodation early', 'Carry sunscreen'],
                'best_time': 'November to February (Winter season)'
            },
            'himachal pradesh': {
                'name': 'Himachal Pradesh',
                'country': 'India',
                'main_city': 'Shimla',
                'description': 'Mountain paradise with snow-capped peaks, valleys, and adventure activities',
                'places': ['Shimla', 'Manali', 'Dharamshala-McLeod Ganj', 'Kasol', 'Spiti Valley', 'Dalhousie', 'Kullu', 'Rohtang Pass'],
                'cuisine': ['Himachali Dham', 'Chana Madra', 'Siddu', 'Babru', 'Aktori', 'Mittha'],
                'culture': ['Buddhist Monasteries', 'Adventure Sports', 'Mountain Trekking', 'Local Handicrafts', 'Apple Orchards', 'Tibetan Culture'],
                'tips': ['Carry warm clothes', 'Check road conditions', 'Book in advance during peak season', 'Try adventure activities', 'Respect mountain environment', 'Stay hydrated'],
                'best_time': 'March to June and September to November'
            }
        }

        # Check if destination matches any in database
        for key, data in location_database.items():
            if key in destination or destination in key:
                return data

        # Default data for unknown destinations
        return {
            'name': destination.title(),
            'country': 'Various',
            'main_city': destination.title(),
            'description': f'A wonderful destination to explore - {destination.title()}',
            'places': ['Main City Center', 'Local Attractions', 'Cultural Sites', 'Shopping Areas'],
            'cuisine': ['Local Specialties', 'Traditional Dishes', 'Street Food', 'Regional Delicacies'],
            'culture': ['Local Traditions', 'Cultural Sites', 'Festivals', 'Art and Crafts'],
            'tips': ['Research local customs', 'Try local cuisine', 'Respect traditions', 'Stay safe', 'Keep documents safe', 'Enjoy the experience'],
            'best_time': 'Check local weather patterns'
        }

# Create global instance
ai_planner = AITravelPlanner()
