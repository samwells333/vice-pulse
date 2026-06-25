import os
import urllib.request
import json
from flask import Flask, render_template, request, jsonify
from scraper import get_live_updates
# Attempt to load feedparser and google-genai securely for production
try:
    import feedparser
except ModuleNotFoundError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "feedparser"])
    import feedparser

try:
    import google.generativeai as genai
except ModuleNotFoundError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
    import google.generativeai as genai

app = Flask(__name__)

# --- MONETIZATION CONFIG ---
# In production, we keep your API key hidden in a system environment variable for security
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_BACKUP_KEY_HERE")
if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_BACKUP_KEY_HERE":
    genai.configure(api_key=GEMINI_API_KEY)

def get_live_feeds():
    """Scrapes live data feeds with tight timeouts so your web page loads instantly."""
    # Production Cache Fallbacks
    news_list = [{"title": "Rockstar Newswire: Weekly Update Live", "link": "https://www.rockstargames.com/newswire", "image": "https://media-rockstargames-com.akamaized.net/mfe6/prod/__common/img/71239c046e7f7b3ee1e4ebca2d2fa5fa.jpg"}]
    video_list = [{"title": "Ocean Drive Car Duping Glitch (Solo $2.4M/hr)", "link": "https://youtube.com", "author": "ViceGamer", "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg"}]
    
    try:
        f = urllib.request.urlopen("https://www.rockstargames.com/newswire.rss", timeout=2)
        feed = feedparser.parse(f.read())
        if feed.entries:
            news_list = [{"title": e.title, "link": e.link, "image": "https://media-rockstargames-com.akamaized.net/mfe6/prod/__common/img/71239c046e7f7b3ee1e4ebca2d2fa5fa.jpg"} for e in feed.entries[:3]]
    except: pass

    try:
        f = urllib.request.urlopen("https://www.youtube.com/feeds/videos.xml?search_query=gta+6+money+glitch", timeout=2)
        feed = feedparser.parse(f.read())
        if feed.entries:
            video_list = []
            for e in feed.entries[:3]:
                v_id = e.id.split(":")[-1] if "video:" in e.id else ""
                video_list.append({
                    "title": e.title, 
                    "link": e.link, 
                    "author": e.author,
                    "thumbnail": f"https://img.youtube.com/vi/{v_id}/mqdefault.jpg" if v_id else "https://via.placeholder.com/100x60"
                })
    except: pass

    return {"official_news": news_list, "money_glitches": video_list}

@app.route('/')
def home():
    """Serves the frontend visual dashboard dashboard."""
    live_data = get_live_feeds()
    return render_template('index.html', data=live_data)

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """Handles incoming live chatbot traffic from the website dashboard."""
    user_data = request.json
    user_query = user_data.get("message", "").strip()
    
    if not user_query:
        return jsonify({"reply": "System intercept: Empty transmission string."})
        
    live_data = get_live_feeds()
    
    # Try connecting to the cloud AI network
    try:
        if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_BACKUP_KEY_HERE":
            return jsonify({"reply": "LOCAL_FALLBACK"})
            
        model = genai.GenerativeModel('gemini-2.5-flash')
        system_instruction = f"You are ViceAI, a street-smart gaming companion for GTA 6. Use this live dashboard dataset to answer user queries concisely: {json.dumps(live_data)}"
        
        response = model.generate_content(system_instruction + "\nUser: " + user_query)
        return jsonify({"reply": response.text})
    except Exception as e:
        # If rate-limited or quota hit, return LOCAL_FALLBACK so the client-side takes over seamlessly
        return jsonify({"reply": "LOCAL_FALLBACK"})
@app.route('/api/updates', methods=['GET'])
def api_updates():
    # Run your engine to get the newest 3 headlines
    headlines = get_live_updates()
    
    # Send them back to Vercel as clean, organized data
    return jsonify({"status": "success", "data": headlines})
if __name__ == '__main__':
    # Bind to port assigned by free cloud hosts like Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
