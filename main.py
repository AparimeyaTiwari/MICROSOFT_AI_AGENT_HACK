import chainlit as cl
from chainlit import run_sync
from chainlit.element import Element
from chainlit.types import AskSpec
import os
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
import googlemaps
import requests
from typing import Optional
import docx
from io import BytesIO
import PyPDF2
import requests
import uuid
from os import environ
from typing import List, Dict, Any
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize global variables
kernel = None
gmaps = None

# initialize translator key and endpoint
language_map = {
    'hi': 'Hindi',
    'mr': 'Marathi',
    'gu': 'Gujarati',
    'kn': 'Kannada',
    'ta': 'Tamil',
    'te': 'Telugu',
    'en': 'English',
    'bn': 'Bengali',
    'pa': 'Punjabi',
    'ml': 'Malayalam',
    'or': 'Odia',
    'as': 'Assamese',
    'ur': 'Urdu',
    'kok': 'Konkani',
    'mai': 'Maithili',
    'ks': 'Kashmiri',
    'ne': 'Nepali',
    'sd': 'Sindhi',
    'sa': 'Sanskrit',
    'bho': 'Bhojpuri',
    'dog': 'Dogri',
    'mni': 'Manipuri',
    'sat': 'Santali',
}

key = os.getenv("TRANSLATOR_KEY")
endpoint = os.getenv("TRANSLATOR_ENDPOINT")
region = os.getenv("TRANSLATOR_REGION")

headers = {
    'Ocp-Apim-Subscription-Key': key,
    'Ocp-Apim-Subscription-Region': region,
    'Content-type': 'application/json',
    'X-ClientTraceId': str(uuid.uuid4())
}

@cl.password_auth_callback
def auth_callback(username: str, password: str):
    username_stored = environ.get("CHAINTLIT_USERNAME")
    password_stored = environ.get("CHAINTLIT_PASSWORD")

    if username_stored is None or password_stored is None:
        raise ValueError(
            "Username or password not set. Please set CHAINTLIT_USERNAME and "
            "CHAINTLIT_PASSWORD environment variables."
        )

    if (username, password) == (username_stored, password_stored):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None

async def detect_and_translate_to_english (text):
    # Step 1: Detect Language
    detect_url = f"{endpoint.rstrip('/')}/detect?api-version=3.0"
    body = [{'Text': text}]
    detect_response = requests.post(detect_url, headers=headers, json=body)
    detect_response.raise_for_status()
    detected_lang = detect_response.json()[0]['language']
    detected_language_name = language_map.get(detected_lang, detected_lang)
    print(f"🕵️ Detected Language: {detected_lang} ({detected_language_name})")

    # Step 2: Translate to English
    translate_to_english_url = f"{endpoint.rstrip('/')}/translate?api-version=3.0&from={detected_lang}&to=en"
    translate_response = requests.post(translate_to_english_url, headers=headers, json=body)
    translate_response.raise_for_status()
    english_text = translate_response.json()[0]['translations'][0]['text']
    # print("🔠 Translated to English:", english_text)
    translated = english_text 
    return translated, detected_lang

async def translate_back_to_original(english_text, original_lang_code):
    body_back = [{'Text': english_text}]
    translate_back_url = f"{endpoint.rstrip('/')}/translate?api-version=3.0&from=en&to={original_lang_code}"
    translate_back_response = requests.post(translate_back_url, headers=headers, json=body_back)
    translate_back_response.raise_for_status()
    back_translated_text = translate_back_response.json()[0]['translations'][0]['text']
    # print("🔁 Back-Translated to Original:", back_translated_text)
    return back_translated_text

@cl.on_chat_start
async def initialize_chat():
    """Initializes the chat session with all agents"""
    global kernel, gmaps
    
    kernel = Kernel()
    kernel.add_service(
        AzureChatCompletion(
            service_id="legal_agents",
            deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        )
    )
    
    # Initialize plugins
    legal_plugin = kernel.add_plugin(plugin_name="LegalAgents", parent_directory="plugins")
    location_plugin = kernel.add_plugin(plugin_name="LocationAgent", parent_directory="plugins")
    
    # Initialize session state
    cl.user_session.set("legal_plugin", legal_plugin)
    cl.user_session.set("location_plugin", location_plugin)
    cl.user_session.set("chat_history", [])
    cl.user_session.set("session_start", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Initialize Google Maps client
    gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

async def extract_city_from_message(message: str) -> Optional[str]:
    """Extracts standardized city name from current message"""
    try:
        location_plugin = cl.user_session.get("location_plugin")
        result = await kernel.invoke(
            location_plugin["city_validator"],
            arguments=KernelArguments(current_message=message)
        )
        city = str(result).strip()
        return city if city != "UNKNOWN" else None
    except Exception as e:
        print(f"City extraction error: {e}")
        return None

async def geocode_city(city: str) -> Optional[str]:
    """Converts city name to coordinates"""
    try:
        geocode_result = gmaps.geocode(f"{city}, India")
        if geocode_result:
            loc = geocode_result[0]['geometry']['location']
            await cl.Message(content=f"📍 Detected location: {city}").send()
            return f"{loc['lat']},{loc['lng']}"
    except Exception as e:
        print(f"Geocoding error for {city}: {e}")
    return None

async def detect_location_from_ip() -> Optional[str]:
    """Attempts location detection via IP address"""
    try:
        ip = cl.user_session.get("client").get("host")
        if ip not in ["127.0.0.1", "::1"]:
            response = requests.get(
                f"https://ipinfo.io/{ip}?token={os.getenv('IPINFO_TOKEN')}",
                timeout=3
            )
            if response.status_code == 200 and "loc" in response.json():
                data = response.json()
                await cl.Message(content=f"📍 IP detected location: {data.get('city', 'Unknown')}").send()
                return data["loc"]
    except Exception as e:
        print(f"IP detection error: {e}")
    return None

async def manual_location_fallback() -> str:
    """Handles manual city input with proper validation"""
    try:
        # Get user input with proper error handling
        res = await cl.AskUserMessage(
            content="📍 Please share your city (e.g. 'Mumbai'):",
            timeout=120
        ).send()

        if not res or not isinstance(res, dict) or 'output' not in res or not res['output'].strip():
            raise ValueError("No valid city input received")
        user_input = res['output'].strip()  # Corrected line
        print(f"DEBUG - User input: {user_input}")  # Log raw input

        # Get plugin and validate
        location_plugin = cl.user_session.get("location_plugin")
        if not location_plugin:
            raise ValueError("Location plugin not initialized")

        # Process through city validator
        validation_result = await kernel.invoke(
            location_plugin["city_validator"],
            arguments=KernelArguments(current_message=user_input)
        )

        clean_city = str(validation_result).strip()
        print(f"DEBUG - Validated city: {clean_city}")  # Log cleaned city
        if clean_city == "UNKNOWN":
            raise ValueError(f"Couldn't identify city from: {user_input}")

        # Geocode the city
        geocode_result = gmaps.geocode(f"{clean_city}, India")
        if not geocode_result:
            raise ValueError(f"Google Maps couldn't locate: {clean_city}")

        loc = geocode_result[0]['geometry']['location']
        await cl.Message(content=f"📍 Location set to: {clean_city}").send()
        return f"{loc['lat']},{loc['lng']}"

    except Exception as e:
        print(f"LOCATION ERROR: {str(e)}")
        await cl.Message(
            content=f"⚠️ Error: {str(e)}\nFalling back to Delhi"
        ).send()
        return "28.6139,77.2090"


async def get_user_location(message: str) -> str:
    """Optimized location detection flow"""
    try:
        # 1. Try extracting from current message
        if message:
            if city := await extract_city_from_message(message):
                if coords := await geocode_city(city):
                    return coords
    except Exception as e:
        print(f"Error extracting city from message: {e}")

    try:
        # 2. Try IP detection
        if coords := await detect_location_from_ip():
            return coords
    except Exception as e:
        print(f"IP detection failed: {e}")

    # 3. Manual fallback
    return await manual_location_fallback()

async def analyze_document(file: cl.File) -> str:
    """
    Processes uploaded legal documents with direct file reading for text files.
    
    Args:
        file: Chainlit File object containing the document to analyze
        
    Returns:
        str: Analysis results with recommendations
    """
    try:
        # Initialize progress message
        progress_msg = cl.Message(content="📄 Processing document...")
        await progress_msg.send()

        # Extract text content based on file type
        content = ""
        file_path = file.path  # Chainlit provides the temporary file path

        if file.name.endswith('.txt'):
            try:
                # Direct file reading for text files
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if not content.strip():
                    return "Error: Text file is empty or contains only whitespace."
            except UnicodeDecodeError:
                # Fallback for non-UTF-8 text files
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except Exception as e:
                return f"Text file reading error: {str(e)}"

        elif file.name.endswith('.pdf'):
            try:
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    content = "\n".join([page.extract_text() or "" for page in reader.pages])
                if not content.strip():
                    return "Error: PDF appears to be empty or contains no extractable text."
            except Exception as e:
                return f"PDF processing error: {str(e)}"

        elif file.name.endswith(('.docx', '.doc')):
            try:
                doc = docx.Document(file_path)
                content = "\n".join([para.text for para in doc.paragraphs])
                if not content.strip():
                    return "Error: Word document appears to be empty."
            except Exception as e:
                return f"Word document processing error: {str(e)}"

        else:
            return f"Unsupported file type: {file.name.split('.')[-1]}"

        # Update progress message
        progress_msg.content = "🔍 Analyzing document content..."
        await progress_msg.update()

        # Get the legal plugin
        legal_plugin = cl.user_session.get("legal_plugin")
        if not legal_plugin:
            raise ValueError("Legal plugin not initialized")

        # Create arguments for semantic kernel
        arguments = KernelArguments(document_text=content[:4000])  # Limit to 4000 chars

        # Invoke document analyzer
        analysis = await kernel.invoke(
            plugin_name=legal_plugin.name,
            function_name="document_analyzer",
            arguments=arguments
        )

        # Get action recommendation
        progress_msg.content = "⚖️ Evaluating legal implications..."
        await progress_msg.update()

        action_required = await kernel.invoke(
            plugin_name=legal_plugin.name,
            function_name="action_required",
            arguments=KernelArguments(document_analysis=str(analysis))
        )

        # Format the response
        action_flag = str(action_required).strip().upper()
        action_text = ("⚠️ **Action Recommended** - Consult a lawyer immediately" 
                      if "YES" in action_flag 
                      else "✅ **No Immediate Action Needed**")

        # Create summary
        summary = await kernel.invoke(
            plugin_name=legal_plugin.name,
            function_name="document_summarizer",
            arguments=KernelArguments(document_text=content[:4000])
        )
        
        response = (
            f"## 📑 Document Analysis Summary\n"
            f"{str(summary).strip()}\n\n"
            f"## 🔍 Detailed Analysis\n"
            f"{str(analysis).strip()}\n\n"
            f"## ⚖️ Legal Assessment\n"
            f"{action_text}\n\n"
            f"📌 _Analysis based on {file.name}_"
        )
        
        return response
        
    except Exception as e:
        error_msg = (
            f"❌ Document analysis failed\n\n"
            f"**Error**: {str(e)}\n\n"
            f"Please try again or upload a different file."
        )
        return error_msg

async def get_lawyer_recommendations(coords: str, lawyer_type: str) -> str:
    """Finds nearby lawyers with ranking"""
    try:
        places = gmaps.places_nearby(
            location=coords,
            keyword=f"{lawyer_type} lawyer",
            radius=50000,
            type="lawyer",
        )
        
        top_lawyers = sorted(
            places.get("results", []),
            key=lambda x: (-x.get('rating', 0), x.get('user_ratings_total', 0)),
        )[:3]

        if not top_lawyers:
            return "No nearby lawyers found for this specialty"

        return "\n\n".join(
            f"🏛 **{lawyer['name']}** (⭐ {lawyer.get('rating', 'N/A')})\n"
            f"📍 {lawyer['vicinity']}\n"
            f"📞 Contact via Google Maps"
            for lawyer in top_lawyers
        )
    except Exception as e:
        return f"⚠️ Error finding lawyers: {str(e)}"



@cl.on_message
async def handle_message(message: cl.Message):
    # Get current chat history
    chat_history: List[Dict[str, Any]] = cl.user_session.get("chat_history", [])
    
    # Add user message to history
    chat_history.append({
        "role": "user",
        "content": message.content,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })
    
    # Handle file attachments (keep your existing file handling code)
    if message.elements:
        processing_msg = await cl.Message(content="📄 Analyzing document...").send()
        analyses = []
        for element in message.elements:
            if isinstance(element, cl.File):
                analysis = await analyze_document(element)
                analyses.append(analysis)
        
        if analyses:
            # Add analysis to history
            chat_history.append({
                "role": "assistant",
                "content": "\n\n".join(analyses),
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            await cl.Message(content="\n\n".join(analyses)).send()
            await processing_msg.remove()
            return
    
    # Process text query
    processing_msg = await cl.Message(content="🔍 Analyzing your query...").send()
    
    try:
        translated_text, langd = await detect_and_translate_to_english(message.content)
        legal_plugin = cl.user_session.get("legal_plugin")
        
        # Get the last 3 messages for context
        context_messages = [
            msg["content"] for msg in chat_history[-3:] 
            if msg["role"] == "user" or msg["role"] == "assistant"
        ]
        context = "\n".join(context_messages)
        
        # Get location-aware legal advice with context
        user_location = await get_user_location(translated_text)
        advice = await kernel.invoke(
            legal_plugin["legal_advisor"], 
            arguments=KernelArguments(
                query=translated_text,
                chat_history=context  # Pass chat history as context
            )
        )
        advice_text = str(advice).strip()
        trans_op = await translate_back_to_original(advice_text, langd)
        
        # Add assistant response to history
        chat_history.append({
            "role": "assistant",
            "content": trans_op,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        
        # Check if lawyer is needed (keep your existing lawyer recommendation code)
        needs_lawyer = await kernel.invoke(
            legal_plugin["lawyer_needed"],
            arguments=KernelArguments(
                legal_advice=str(advice),
                user_query=translated_text,
            )
        )
        needs_lawyer = str(needs_lawyer).strip().upper()
        
        if "YES" in needs_lawyer:
            lawyer_type = await kernel.invoke(
                legal_plugin["lawyer_type"],
                arguments=KernelArguments(legal_advice=str(advice))
            )
            lawyer_type = str(lawyer_type).strip()
            
            lawyers = await get_lawyer_recommendations(user_location, lawyer_type)
            final_content = f"\n\n⚖️ Recommended: {lawyer_type} lawyer"
            final_content += f"\n\n## Legal Advice\n{trans_op}\n\n## Local {lawyer_type} Lawyers\n{lawyers}"
            
            # Update the final message in history
            chat_history[-1]["content"] = final_content
            await processing_msg.stream_token(final_content)
        else:
            await cl.Message(content=f"✅ Advice:\n{trans_op}").send()
            await processing_msg.remove()
            
        # Update the chat history in session
        cl.user_session.set("chat_history", chat_history)
            
    except Exception as e:
        error_msg = f"❌ Processing error: {str(e)}"
        chat_history.append({
            "role": "assistant",
            "content": error_msg,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        cl.user_session.set("chat_history", chat_history)
        await cl.Message(content=error_msg).send()
        await processing_msg.remove()