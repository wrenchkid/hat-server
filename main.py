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
        data = request.get_json(force=True)
        
        print(f"Received POST request: {data}")  # Debug log
        
        user_id = str(data.get("userId"))
        hats = data.get("hats")
        job_id = str(data.get("jobId", "unknown"))

        if not user_id or hats is None:
            print("Error: Missing userId or hats")
            return jsonify({"error": "Missing data"}), 400

        # Update storage
        active_players[user_id] = {
            "hats": hats,
            "jobId": job_id,
            "last_seen": time.time()
        }
        
        print(f"Stored player {user_id} with {len(hats)} hats in job {job_id}")
        print(f"Total active players: {len(active_players)}")
        
        return jsonify({"status": "updated"}), 200
    except Exception as e:
        print(f"Error in /update: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 2. GET ONLY PLAYERS IN YOUR SPECIFIC SERVER
@app.route('/poll', methods=['GET'])
def get_players():
    try:
        current_time = time.time()
        cutoff = current_time - 30  # Increased from 15 to 30 seconds
        
        requester_job_id = request.args.get('jobId')
        print(f"Poll request for jobId: {requester_job_id}")

        # Clean up old players first
        to_remove = [uid for uid, data in active_players.items() if data['last_seen'] < cutoff]
        for uid in to_remove:
            print(f"Removing expired player: {uid}")
            del active_players[uid]

        print(f"Active players before filtering: {list(active_players.keys())}")

        # Filter: Only return players who match the requester's Job ID
        if requester_job_id:
            filtered_players = {
                uid: data for uid, data in active_players.items() 
                if data.get('jobId') == requester_job_id
            }
            print(f"Filtered players for job {requester_job_id}: {list(filtered_players.keys())}")
            
            response = app.response_class(
                response=jsonify(filtered_players).get_data(),
                status=200,
                mimetype='application/json'
            )
            return response
        
        # Fallback: return all players
        response = app.response_class(
            response=jsonify(active_players).get_data(),
            status=200,
            mimetype='application/json'
        )
        return response
        
    except Exception as e:
        print(f"Error in /poll: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
