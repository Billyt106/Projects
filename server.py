from flask import Flask, jsonify
import AI_scouter  # Import your AI_scouter script

app = Flask(__name__)

@app.route('/run-ai-scouter', methods=['GET'])
def run_ai_scouter():
    try:
        data = AI_scouter.main()  # Run the main function of AI_scouter
        return jsonify(data)  # Send the data back as JSON
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # Run the server on port 5000
