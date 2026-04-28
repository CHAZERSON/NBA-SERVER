from flask import Flask, request
import requests
import os

app = Flask(__name__)

# Securely fetches the Bot ID from Render's Environment Variables
BOT_ID = os.environ.get("GROUPME_BOT_ID")

def get_scores():
    url = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    try:
        response = requests.get(url).json()
        events = response.get('events', [])
        
        if not events:
            return "No NBA games scheduled for today."
            
        score_lines = []
        for event in events:
            status_type = event['status']['type']['state'].lower()
            status_detail = event['status']['type']['detail']
            
            home = event['competitions'][0]['competitors'][0]
            away = event['competitions'][0]['competitors'][1]
            
            h_name = home['team']['abbreviation']
            h_score = home.get('score', '0')
            a_name = away['team']['abbreviation']
            a_score = away.get('score', '0')
            
            if status_type == 'pre':
                score_lines.append(f"{a_name} @ {h_name} ({status_detail})")
            else:
                score_lines.append(f"{a_name} {a_score} - {h_score} {h_name} ({status_detail})")
        
        return "\n".join(score_lines)
    except Exception:
        return "Error fetching the scoreboard."

def send_reply(message):
    if not BOT_ID:
        print("Error: No Bot ID configured.")
        return
    requests.post("https://api.groupme.com/v3/bots/post", json={"bot_id": BOT_ID, "text": message})

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    
    # Ensures the bot doesn't reply to its own messages
    if data and data.get('sender_type') != 'bot':
        text = data.get('text', '').strip().lower()
        
        # Only triggers if the exact text is "score"
        if text == 'score':
            scores = get_scores()
            send_reply(scores)
                
    return "OK", 200
