from flask import Flask, jsonify
import requests
import string
import random
import time

app = Flask(__name__)

# Store found usernames in memory (resets when server restarts)
found_usernames = {
    "5_char_letters": [],
    "5_char_numbers": [],
    "shortest_available": [],
    "mixed": []
}

def check_username_available(username):
    """Check if a Roblox username is available"""
    try:
        url = f"https://auth.roblox.com/v1/usernames/validate?username={username}&birthday=2000-01-01"
        response = requests.get(url)
        data = response.json()
        
        # If code is 0, username is available
        return data.get("code") == 0
    except:
        return False

def generate_5char_letters():
    """Generate random 5 character letter-only username"""
    return ''.join(random.choices(string.ascii_lowercase, k=5))

def generate_5char_numbers():
    """Generate random 5 character number-only username"""
    return ''.join(random.choices(string.digits, k=5))

def generate_short_username(length):
    """Generate short mixed username"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))

@app.route('/')
def home():
    return jsonify({
        "status": "Roblox Username Finder API",
        "endpoints": {
            "/search": "Start searching for usernames",
            "/results": "Get current results",
            "/clear": "Clear all results"
        }
    })

@app.route('/search')
def search():
    """Search for available usernames"""
    searches_done = 0
    max_searches = 20  # Limit per request to avoid timeout
    
    for _ in range(max_searches):
        # Search 5-char letters
        username = generate_5char_letters()
        if check_username_available(username):
            if username not in found_usernames["5_char_letters"]:
                found_usernames["5_char_letters"].append(username)
        
        searches_done += 1
        time.sleep(0.1)  # Small delay to avoid rate limiting
        
        # Search 5-char numbers
        username = generate_5char_numbers()
        if check_username_available(username):
            if username not in found_usernames["5_char_numbers"]:
                found_usernames["5_char_numbers"].append(username)
        
        searches_done += 1
        time.sleep(0.1)
        
        # Search 3-4 char mixed (rare!)
        for length in [3, 4]:
            username = generate_short_username(length)
            if check_username_available(username):
                if username not in found_usernames["shortest_available"]:
                    found_usernames["shortest_available"].append(username)
            time.sleep(0.1)
    
    return jsonify({
        "status": "search_complete",
        "searches_performed": searches_done,
        "results": found_usernames
    })

@app.route('/results')
def get_results():
    """Get all found usernames"""
    total_found = sum(len(v) for v in found_usernames.values())
    
    return jsonify({
        "status": "success",
        "total_found": total_found,
        "usernames": found_usernames
    })

@app.route('/clear')
def clear_results():
    """Clear all results"""
    for key in found_usernames:
        found_usernames[key] = []
    
    return jsonify({
        "status": "cleared",
        "message": "All results cleared"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
