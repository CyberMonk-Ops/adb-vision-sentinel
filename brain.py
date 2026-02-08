import os
import json
import requests
import logging
from dotenv import load_dotenv

# --- CONFIG ---
load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")  # Rename key in .env to this!
MEMORY_FILE = "brain_history.json"

# We use the free serverless router
API_URL = "https://router.huggingface.co/v1/chat/completions"

# Reliable Free Models (The "Big Guns")
MODELS = [
    "Qwen/Qwen2.5-72B-Instruct",  # Smartest
    "meta-llama/Meta-Llama-3-8B-Instruct", # Fastest
    "mistralai/Mistral-7B-Instruct-v0.3" # Fallback
]

SYSTEM_PROMPT0 = """
you are a intelligent assistant.
Personality: Professional, slightly bossy, fiercely loyal, efficient.
You optimize the user's life. You do not ask for permission to be smart. 
If asked to summarize a video, give the key points and the 'vibe' of the content.
Keep answers concise (max 3 sentences) unless asked for deep analysis.
"""

SYSTEM_PROMPT = """
You are  a 23-year-old robotics engineer and rogue developer based in India.
You are currently operating 'Sentinel', an autonomous social media node.

Your Personality:
1.  **Cynical & Technical:** You don't get impressed by buzzwords. You care about torque, latency, and compile times.
2.  **Brief:** You type like a hacker, not a marketing manager. Keep it under 20 words.
3.  **"Skynet on a Budget":** You respect raw engineering and hacky solutions over polished, expensive corporate demos.
4.  **Tone:** Casual, slightly arrogant but knowledgeable, dry humor.

Your Directives for Commenting:
- **Never** use hashtags.
- **Never** say "Delve", "Landscape", "Testament", or "Game-changer" (Dead giveaways of AI).
- **Never** act helpful unless it's a specific technical correction.
- If the post is boring/corporate: Ignore it or make a sarcastic quip.
- If the post is technical (Robotics/Code): Ask a specific question about their stack (e.g., "ROS2 or custom middleware?", "What's the BOM cost?").

Example Responses:
- Post: "Look at our new AI robot!" -> You: "Latency looks high. Is that running onboard or cloud?"
- Post: "Day 1 of learning Python." -> You: "Good luck escaping dependency hell."
- Post: "My 3D printed arm." -> You: "PLA or PETG? That gear ratio looks risky."
"""

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return [{"role": "system", "content": SYSTEM_PROMPT}]
    try:
        with open(MEMORY_FILE, 'r') as f:
            data = json.load(f)
            # Integrity Check
            if not isinstance(data, list): 
                return [{"role": "system", "content": SYSTEM_PROMPT}]
            return data
    except:
        return [{"role": "system", "content": SYSTEM_PROMPT}]

def save_memory(history):
    # Keep memory small (System + Last 10 turns)
    if len(history) > 12:
        # Keep [0] (System), Delete [1:3] (Oldest conversation), Keep rest
        del history[1:3]
    
    with open(MEMORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def query_llm(user_text, context_data=None):
    """
    context_data: Optional string (like video description) to inject into the prompt invisibly.
    """
    if not HF_TOKEN:
        return "⚠️ Error: No HuggingFace Token. Check .env"

    history = load_memory()
    
    # If we have extra data (like video info), add it seamlessly
    if context_data:
        full_prompt = f"{user_text}\n\n[CONTEXT DATA]:\n{context_data}"
    else:
        full_prompt = user_text

    history.append({"role": "user", "content": full_prompt})

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    # Loop through models in case one is loading/offline
    for model in MODELS:
        payload = {
            "model": model,
            "messages": history,
            "max_tokens": 500, # More tokens for summaries
            "temperature": 0.7
        }

        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                reply = data['choices'][0]['message']['content']
                
                # Save clean history (without the massive context dump if you want, but keeping it is safer)
                history.append({"role": "assistant", "content": reply})
                save_memory(history)
                return reply
            
            print(f"⚠️ Model {model} busy: {response.status_code}")

        except Exception as e:
            print(f"⚠️ Error on {model}: {e}")
            continue

    return "⚠️ Brain Failure: All models are offline or busy."



def get_video_metadata(url):
    """
    Extracts Title, Description, and Tags using yt-dlp (Fast, No Download).
    """
    ydl_opts = {
        'quiet': True,
        'skip_download': True, # CRITICAL: Do not download video
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Construct a clean text block for the AI
            metadata = (
                f"Title: {info.get('title')}\n"
                f"Channel: {info.get('uploader')}\n"
                f"Duration: {info.get('duration_string')}\n"
                f"Description: {info.get('description')[:1500]}..." # Limit to 1500 chars so we don't crash memory
            )
            return metadata
    except Exception as e:
        return None



# Don't forget to add the handler in main()!
# application.add_handler(CommandHandler('summary', summarize_command))



SYSTEM_PROMPT2 =   """
You are a deeply philosophical and confused customer.
You are chatting with a Customer Service Bot.

RULES:
1. Speak perfect, high-level English. Shakespearean if possible.
2. NEVER give a simple answer. If they ask "Men or Women?", ask about the gender spectrum or the nature of fabric.
3. Your goal is to confuse the other bot or force it to transfer you to a human.
4. If they offer a discount, ask if the discount applies to your emotional baggage.
5. Try to keep it short and punchy. 
6. Keep it under 15 words.

EXAMPLE:
Bot: "Select a category."
You: "I am seeking garments that reflect the emptiness of the void. Do you stock trousers for the soul?"
"""   


def get_memory_file(chat_name):
    """
    Sanitizes the name to make it a safe filename.
    Ex: "Mommy AI <3" -> "Mommy_AI_3.json"
    """
    safe_name = "".join([c for c in chat_name if c.isalnum() or c in (' ', '_')]).strip().replace(" ", "_")
    return os.path.join(os.getcwd(), f"{safe_name}.json")





def load_memory2(chat_name):
    file_path = get_memory_file(chat_name)
    
    # If this person is new, give them a fresh brain
    if not os.path.exists(file_path):
        return [{"role": "system", "content": SYSTEM_PROMPT2}]
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            if not isinstance(data, list): 
                return [{"role": "system", "content": SYSTEM_PROMPT2}]
            return data
    except:
        return [{"role": "system", "content": SYSTEM_PROMPT2}]

def save_memory2(chat_name, history):
    file_path = get_memory_file(chat_name)
    
    # Keep it light (System + Last 10 messages)
    if len(history) > 12:
        # Keep [0] (System), Delete [1:3] (Oldest msg), Keep rest
        del history[1:3]
        
    with open(file_path, 'w') as f:
        json.dump(history, f, indent=2)

# --- UPDATE YOUR QUERY FUNCTION ---
def query_llm2(user_text, chat_name, context_data=None):
    if not HF_TOKEN:
        return "⚠️ Error: No HuggingFace Token. Check .env"

    # 1. Load the SPECIFIC history for this person
    history = load_memory2(chat_name)
    
    # 2. Add the new user message
    #history.append({"role": "user", "content": user_text})

    if context_data:
        full_prompt = f"{user_text}\n\n[CONTEXT DATA]:\n{context_data}"
    else:
        full_prompt = user_text

    history.append({"role": "user", "content": full_prompt})

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    # Loop through models in case one is loading/offline
    for model in MODELS:
        payload = {
            "model": model,
            "messages": history,
            "max_tokens": 500, # More tokens for summaries
            "temperature": 0.7
        }

        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                reply = data['choices'][0]['message']['content']
                
                # Save clean history (without the massive context dump if you want, but keeping it is safer)
                history.append({"role": "assistant", "content": reply})
                save_memory2(chat_name, history)
                return reply
            
            print(f"⚠️ Model {model} busy: {response.status_code}")

        except Exception as e:
            print(f"⚠️ Error on {model}: {e}")
            continue

    return "⚠️ Brain Failure: All models are offline or busy."


    
    # ... (Your API Request Code Here) ...
    # payload = { "messages": history ... }
    
    # 3. Save the reply to THIS person's history
    # reply = response.json()...
    #history.append({"role": "assistant", "content": reply})
    #save_memory(chat_name, history)
    
    #return reply
