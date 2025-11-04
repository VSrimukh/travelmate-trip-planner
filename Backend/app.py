from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import time
import requests
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app) 

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"

def test_ollama_connection():
    """Test if Ollama is running and model is available"""
    try:
        response = requests.post(OLLAMA_URL, 
            json={
                "model": MODEL_NAME,
                "prompt": "Hello",
                "stream": False
            }, 
            timeout=10
        )
        if response.status_code == 200:
            logger.info(" Ollama connection successful")
            return True
        else:
            logger.error(f" Ollama responded with status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f" Failed to connect to Ollama: {e}")
        return False

def generate_with_ollama(prompt, timeout=180):
    """Generate response using direct Ollama API with optimized settings"""
    try:
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 1500,  
                "num_ctx": 4096,     
                "repeat_penalty": 1.1,
                "stop": ["\n\nHuman:", "\n\nUser:"]  
            }
        }
        
        logger.info(f"Making Ollama request with {timeout}s timeout...")
        
        start_time = time.time()
        
        response = requests.post(OLLAMA_URL, 
            json=payload, 
            timeout=timeout,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', 'No response generated')
            elapsed_time = time.time() - start_time
            logger.info(f"Response generated successfully ({len(generated_text)} characters, {elapsed_time:.1f}s)")
            return generated_text
        else:
            logger.error(f"Ollama API error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error(f"Ollama request timed out after {timeout} seconds")
        return "TIMEOUT"
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Ollama - is it running?")
        return None
    except Exception as e:
        logger.error(f"Error calling Ollama: {e}")
        return None

def vector_db_store_travel_data(destination, itinerary_text, budget_text, metadata=None):
    try:
        """
        import chromadb
        from chromadb.utils import embedding_functions
        
        chroma_client = chromadb.Client()
        
        embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        collection = chroma_client.get_or_create_collection(
            name="travel_itineraries",
            embedding_function=embedding_fn
        )
        
        documents = [
            f"Destination: {destination}\n\nItinerary:\n{itinerary_text}",
            f"Destination: {destination}\n\nBudget:\n{budget_text}"
        ]
        
        import hashlib
        doc_ids = [
            hashlib.md5(f"{destination}_itinerary_{time.time()}".encode()).hexdigest(),
            hashlib.md5(f"{destination}_budget_{time.time()}".encode()).hexdigest()
        ]
        
        metadatas = [
            {
                "destination": destination,
                "type": "itinerary",
                "timestamp": time.time(),
                **(metadata or {})
            },
            {
                "destination": destination,
                "type": "budget",
                "timestamp": time.time(),
                **(metadata or {})
            }
        ]
        
        collection.add(
            documents=documents,
            ids=doc_ids,
            metadatas=metadatas
        )
        
        logger.info(f"Stored travel data for {destination} in vector database")
        
        return {
            "status": "success",
            "destination": destination,
            "documents_stored": len(documents),
            "ids": doc_ids
        }
        """
        
        logger.info(f"[DEMO] Vector DB storage simulated for: {destination}")
        return {
            "status": "demo_mode",
            "message": "Vector DB function ready for integration",
            "destination": destination
        }
        
    except Exception as e:
        logger.error(f"Vector DB storage error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def vector_db_search_similar_trips(query, destination=None, limit=5):
    try:
        """
        import chromadb
        from chromadb.utils import embedding_functions
        
        chroma_client = chromadb.Client()
        embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        collection = chroma_client.get_collection(
            name="travel_itineraries",
            embedding_function=embedding_fn
        )
        
        where_filter = {"type": {"$in": ["itinerary", "budget"]}}
        if destination:
            where_filter["destination"] = destination
        
        results = collection.query(
            query_texts=[query],
            n_results=limit,
            where=where_filter
        )
        
        similar_trips = []
        for i, doc in enumerate(results['documents'][0]):
            similar_trips.append({
                "content": doc,
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i],
                "relevance_score": 1 - results['distances'][0][i]
            })
        
        logger.info(f"Found {len(similar_trips)} similar trips for query: {query}")
        return similar_trips
        """
        
        logger.info(f"[DEMO] Vector search simulated for: {query}")
        return [
            {
                "status": "demo_mode",
                "query": query,
                "destination_filter": destination
            }
        ]
        
    except Exception as e:
        logger.error(f"Vector DB search error: {e}")
        return []

ITINERARY_TEMPLATE = """Create a {duration}-day travel itinerary for {destination}.

Travel Details: {prompt}

Provide a day-by-day plan with:
- Morning, afternoon, evening activities
- Key attractions and local experiences
- Food recommendations
- Transportation tips
- Practical advice

Format: "Day 1:", "Day 2:", etc. Keep it concise but engaging.
"""

BUDGET_TEMPLATE = """Create a budget breakdown for a {duration}-day trip to {destination} for {travelers} travelers.

Details: {prompt}

Provide costs for:
1. Transportation (round trip)
2. Accommodation (per night)
3. Food (daily)
4. Activities and local transport
5. Total estimated cost

Use appropriate currency. Include money-saving tips.
Keep response focused and practical.
"""

def create_optimized_prompt(template, user_prompt):
    """Extract key details and create optimized prompt"""
 
    duration = "multi"
    if "day" in user_prompt.lower():
        import re
        duration_match = re.search(r'(\d+)-day', user_prompt)
        if duration_match:
            duration = duration_match.group(1)
    
    destination = "the destination"
    if "visiting" in user_prompt.lower():
        dest_match = re.search(r'visiting\s+([^.]+)', user_prompt)
        if dest_match:
            destination = dest_match.group(1).strip()
    
    travelers = "travelers"
    if "traveler(s)" in user_prompt:
        travel_match = re.search(r'(\d+)\s+traveler', user_prompt)
        if travel_match:
            travelers = travel_match.group(1) + " travelers"
    
    return template.format(
        duration=duration,
        destination=destination,
        travelers=travelers,
        prompt=user_prompt
    )

@app.route('/api/generate-itinerary', methods=['POST'])
def generate_itinerary():
    """Generate AI-powered travel itinerary"""
    try:
        data = request.json
        user_prompt = data.get('prompt', '')
        
        if not user_prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        logger.info(f"Generating itinerary for: {user_prompt[:100]}...")
     
        full_prompt = create_optimized_prompt(ITINERARY_TEMPLATE, user_prompt)
        
        result = generate_with_ollama(full_prompt, timeout=180)
        
        if result == "TIMEOUT":
            return jsonify({
                'response': generate_fallback_itinerary(user_prompt),
                'status': 'fallback',
                'message': 'AI took too long to respond. Here\'s a basic itinerary structure.'
            })
        elif result is None:
            return jsonify({
                'error': 'Failed to generate itinerary',
                'message': 'Ollama service unavailable. Please ensure Ollama is running with llama3.2 model.'
            }), 500
        
        logger.info("Itinerary generated successfully")
        
        return jsonify({
            'response': result,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error generating itinerary: {str(e)}")
        return jsonify({
            'error': 'Failed to generate itinerary',
            'message': str(e)
        }), 500

@app.route('/api/generate-budget', methods=['POST'])
def generate_budget():
    """Generate AI-powered budget breakdown"""
    try:
        data = request.json
        user_prompt = data.get('prompt', '')
        
        if not user_prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        logger.info(f"Generating budget for: {user_prompt[:100]}...")
        
        full_prompt = create_optimized_prompt(BUDGET_TEMPLATE, user_prompt)
        
        result = generate_with_ollama(full_prompt, timeout=120)
        
        if result == "TIMEOUT":
       
            return jsonify({
                'response': generate_fallback_budget(user_prompt),
                'status': 'fallback',
                'message': 'AI took too long to respond. Here\'s a basic budget estimate.'
            })
        elif result is None:
            return jsonify({
                'error': 'Failed to generate budget',
                'message': 'Ollama service unavailable. Please ensure Ollama is running with llama3.2 model.'
            }), 500
        
        logger.info("Budget generated successfully")
        
        return jsonify({
            'response': result,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error generating budget: {str(e)}")
        return jsonify({
            'error': 'Failed to generate budget',
            'message': str(e)
        }), 500

def generate_fallback_itinerary(user_prompt):
    """Generate a basic fallback itinerary when AI times out"""
    import re
    
    duration_match = re.search(r'(\d+)-day', user_prompt)
    duration = int(duration_match.group(1)) if duration_match else 7
    
    destination_match = re.search(r'visiting\s+([^.]+)', user_prompt)
    destination = destination_match.group(1).strip() if destination_match else "your destination"
    
    fallback = f"""Basic {duration}-day itinerary for {destination}:

Day 1: Arrival
- Morning: Arrive and check into accommodation
- Afternoon: Local orientation walk and nearby attractions
- Evening: Welcome dinner and rest

"""
    
    for day in range(2, min(duration, 6)): 
        fallback += f"""Day {day}: Exploration
- Morning: Visit major attractions in {destination}
- Afternoon: Local experiences and cultural sites
- Evening: Local cuisine and leisure time

"""
    
    if duration > 5:
        fallback += f"""Days 6-{duration}: Extended exploration with day trips, shopping, and relaxation

"""
    
    fallback += f"Final Day: Departure and journey home\n\nNote: This is a basic structure. For detailed recommendations, please try again or consult local travel guides."
    
    return fallback

def generate_fallback_budget(user_prompt):
    """Generate a basic fallback budget when AI times out"""
    import re
    
    duration_match = re.search(r'(\d+)-day', user_prompt)
    duration = int(duration_match.group(1)) if duration_match else 7
    
    travelers_match = re.search(r'(\d+)\s+traveler', user_prompt)
    travelers = int(travelers_match.group(1)) if travelers_match else 2
    is_international = any(country in user_prompt.lower() for country in ['japan', 'usa', 'europe', 'singapore', 'thailand'])
    
    if is_international:
        currency = "$"
        transport = 800 * travelers
        accommodation = 80 * duration * travelers
        food = 40 * duration * travelers
        activities = 50 * duration * travelers
        total = transport + accommodation + food + activities
    else:
        currency = "₹"
        transport = 15000 * travelers
        accommodation = 3000 * duration * travelers
        food = 1500 * duration * travelers
        activities = 2000 * duration * travelers
        total = transport + accommodation + food + activities
    
    fallback = f"""Basic Budget Breakdown ({duration} days, {travelers} travelers):

**Transportation**: {currency}{transport:,}
- Round trip flights/transport

**Accommodation**: {currency}{accommodation:,}
- Mid-range hotels/stays

**Food & Meals**: {currency}{food:,}
- Local restaurants and dining

**Activities**: {currency}{activities:,}
- Attractions, tours, local transport

**Total Estimated Cost**: {currency}{total:,}

*Note: These are rough estimates. Actual costs may vary based on season, specific choices, and current market rates. For detailed pricing, please try again or consult travel booking sites.*
"""
    
    return fallback

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    ollama_status = test_ollama_connection()
    
    return jsonify({
        'status': 'healthy' if ollama_status else 'degraded',
        'ollama_connected': ollama_status,
        'model': MODEL_NAME,
        'message': 'AI Travel Assistant API is running'
    })

@app.route('/', methods=['GET'])
def home():
    """API information"""
    ollama_status = test_ollama_connection()
    
    return jsonify({
        'message': 'TravelMate AI Assistant API',
        'version': '1.0',
        'model': MODEL_NAME,
        'ollama_status': 'connected' if ollama_status else 'disconnected',
        'endpoints': {
            'POST /api/generate-itinerary': 'Generate travel itinerary',
            'POST /api/generate-budget': 'Generate budget breakdown', 
            'GET /health': 'Health check'
        }
    })

if __name__ == '__main__':
    print("\n Starting TravelMate AI Assistant API...")
    print("=" * 50)
    
    if test_ollama_connection():
        print(f"Model: {MODEL_NAME} (Connected)")
    else:
        print(" Ollama: Not Available")
        print("\n  To fix this issue:")
        print("   1. Install Ollama: https://ollama.ai/download")
        print("   2. Pull the model: ollama pull llama3.2")
        print("   3. Start Ollama service")
    
    print("\n Available endpoints:")
    print("   POST /api/generate-itinerary - AI itinerary generation")
    print("   POST /api/generate-budget    - Smart budget planning")
    print("   GET  /health                - Health check")
    print("=" * 50)
    print(" Server starting on http://localhost:5000")
    print("   Frontend can now connect!\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)