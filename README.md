# AI Itinerary Travel Planner

***This project is an AI-powered Travel Itinerary Planner where the user enters a city, budget, and number of days, and the system generates a complete day-by-day itinerary. It uses prompt chaining and LLM API calls to produce travel summaries, sightseeing plans, dining recommendations, and map suggestions. The app automates the entire planning process by creating personalized, structured travel itineraries for users. It helps users save time by automatically creating structured travel plans instead of manual research.***

---

## 🚀 Features
- AI-generated travel itineraries
- Day-wise trip planning
- Clean and interactive frontend
- Python backend handling AI logic
- Google Gemini API integration

---

## 🛠 Tech Stack
- **Frontend:** React.js, HTML, CSS, JavaScript  
- **Backend:** Python ,Bubble.io
- **AI:** Google Gemini API (Google AI Studio)

---

## Project Structure

ai-travel-planner/
│
├── backend/
│   ├── __pycache__/
│   ├── .env
│   ├── ai_service.py
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── node_modules/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── package-lock.json
│
├── package.json
├── package-lock.json
└── README.md


## ⚙️ How to Run the Project

## 📥 Clone the Repository
```bash
git clone https://github.com/your-username/AI-Itinerary-Travel-Planner.git
cd AI-Travel-Planner 

🔑 API Key Setup

1. Go to Google AI Studio
2. Generate your Gemini API key
3. Inside backend folder, a file named .env

Add your API key like this:
GEMINI_API_KEY="your_api_key_here"

### 🔹 Backend Setup
```bash
cd backend
python main.py

### 🔹 Frontend Setup
```bash
cd frontend
npm start
