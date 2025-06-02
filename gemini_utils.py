import os
from dotenv import load_dotenv
import json
import google.generativeai as genai

# Load environment variables
load_dotenv()

def extract_fields(incident_text: str) -> dict:
    """Extract structured fields from incident description using Gemini"""
    
    print(f"🔍 Starting extraction for text: {incident_text[:100]}...")
    
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY not found in .env file")
            return {"error": "GEMINI_API_KEY not found in .env file"}
        
        print(f"✅ API Key found: {api_key[:10]}...")
        
        # Configure the API key
        genai.configure(api_key=api_key)
        
        # Use GenerativeModel API
        print("🤖 Using GenerativeModel API")
        return _extract_with_generative_model(genai, incident_text)
            
    except ImportError as e:
        error_msg = f"Import error: {str(e)}. Try: pip install google-generativeai"
        print(f"❌ {error_msg}")
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(f"❌ {error_msg}")
        return {"error": error_msg}

def _extract_with_generative_model(genai, incident_text):
    """Use GenerativeModel API"""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = _create_prompt(incident_text)
        print(f"📤 Sending prompt: {prompt[:200]}...")
        response = model.generate_content(prompt)
        print(f"📥 Response received: {response.text[:200]}...")
        return _parse_response(response.text)
    except Exception as e:
        print(f"❌ GenerativeModel failed: {e}")
        import traceback
        print(f"Stack trace: {traceback.format_exc()}")
        return {"error": f"GenerativeModel failed: {str(e)}"}

def _create_prompt(incident_text):
    """Create the extraction prompt"""
    return f"""You are a data extraction assistant. Extract information from this incident report and return ONLY a valid JSON object.

INCIDENT REPORT:
{incident_text}

Extract these fields:
- category: Must be one of: Harassment, Fraud, Safety Violation, Discrimination, Corruption, Data Breach, Workplace Violence, Theft, Ethics Violation, Other
- date: If a date is mentioned, format as DD/MM/YYYY, otherwise "Not mentioned"
- time: If time is mentioned, format as HH:MM, otherwise "Not mentioned"  
- accused: Name or position of accused person if mentioned, otherwise "Not mentioned"
- location: Specific location if mentioned, otherwise "Not mentioned"
- summary: Brief one-sentence summary of what happened

IMPORTANT: Return ONLY the JSON object, no other text.

Format:
{{"category": "...", "date": "...", "time": "...", "accused": "...", "location": "...", "summary": "..."}}"""

def _parse_response(response_text):
    """Parse the API response"""
    if not response_text:
        return {"error": "Empty response from API"}
        
    print(f"📥 Raw response: {response_text}")
    
    # Clean up the response
    json_text = response_text.strip()
    
    # Remove markdown formatting
    if "```json" in json_text:
        json_text = json_text.split("```json")[1].split("```")[0].strip()
    elif "```" in json_text:
        json_text = json_text.split("```")[1].split("```")[0].strip()
    
    # Extract JSON object
    if "{" in json_text and "}" in json_text:
        start = json_text.find("{")
        end = json_text.rfind("}") + 1
        json_text = json_text[start:end]
    
    print(f"🔧 Cleaned JSON: {json_text}")
    
    try:
        result = json.loads(json_text)
        print(f"✅ Successfully parsed JSON: {result}")
        
        # Validate required fields
        required_fields = ["category", "date", "time", "accused", "location", "summary"]
        for field in required_fields:
            if field not in result:
                result[field] = "Not mentioned"
        
        return result
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {str(e)}")
        
        # Fallback: create a basic response
        return {
            "category": "Other",
            "date": "Not mentioned",
            "time": "Not mentioned", 
            "accused": "Not mentioned",
            "location": "Not mentioned",
            "summary": f"Incident reported: {incident_text[:100]}..."
        }
    
if __name__ == "__main__":
    incident_text = "Yesterday around 3 PM in the marketing department on the 5th floor, my supervisor John Smith made inappropriate comments."
    result = extract_fields(incident_text)
    print(result)