from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# DATABASE (In-Memory)
# Structure: { "123456": { "hats": ["Hat1", "Hat2"], "last_seen": 17000000 } }
active_players = {}

@app.route('/')
def home():
    return "Hat Server is Running!", 200

# 1. PLAYERS SEND THEIR HATS HERE
@app.route('/update', methods=['POST'])
def update_player():
    try:
        data = request.json
        user_id = str(data.get("userId"))
        hats = data.get("hats")

        if not user_id or hats is None:
            return jsonify({"error": "Missing data"}), 400

        # Update storage
        active_players[user_id] = {
            "hats": hats,
            "last_seen": time.time()
        }
        
        return jsonify({"status": "updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2. PLAYERS GET EVERYONE ELSE'S HATS HERE
@app.route('/poll', methods=['GET'])
def get_players():
    current_time = time.time()
    cutoff = current_time - 15 # Remove players inactive for 15 seconds
    
    # Clean up old players (AFK/Left)
    to_remove = [uid for uid, data in active_players.items() if data['last_seen'] < cutoff]
    for uid in to_remove:
        del active_players[uid]

    return jsonify(active_players), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)