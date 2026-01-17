from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# DATABASE
active_players = {}

@app.route('/')
def home():
    return "Hat Server is Running!", 200

# 1. PLAYERS SEND THEIR HATS + JOB ID
@app.route('/update', methods=['POST'])
def update_player():
    try:
        data = request.json
        user_id = str(data.get("userId"))
        hats = data.get("hats")
        job_id = str(data.get("jobId", "unknown"))

        if not user_id or hats is None:
            return jsonify({"error": "Missing data"}), 400

        # Update storage
        active_players[user_id] = {
            "hats": hats,
            "jobId": job_id,
            "last_seen": time.time()
        }
        
        return jsonify({"status": "updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2. GET ONLY PLAYERS IN YOUR SPECIFIC SERVER
@app.route('/poll', methods=['GET'])
def get_players():
    current_time = time.time()
    cutoff = current_time - 15 
    
    requester_job_id = request.args.get('jobId')

    # Clean up old players first
    to_remove = [uid for uid, data in active_players.items() if data['last_seen'] < cutoff]
    for uid in to_remove:
        del active_players[uid]

    # Filter: Only return players who match the requester's Job ID
    if requester_job_id:
        filtered_players = {
            uid: data for uid, data in active_players.items() 
            if data.get('jobId') == requester_job_id
        }
        # IMPORTANT: Return empty dict as JSON, not empty string
        response = jsonify(filtered_players)
        response.headers['Content-Type'] = 'application/json'
        return response, 200
    
    # Fallback
    response = jsonify(active_players)
    response.headers['Content-Type'] = 'application/json'
    return response, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
