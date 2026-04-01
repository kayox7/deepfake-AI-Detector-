from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "../uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

API_USER = os.getenv("API_USER")
API_SECRET = os.getenv("API_SECRET")

@app.route("/detect", methods=["POST"])
def detect():

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"})

    file = request.files["image"]
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    with open(filepath, 'rb') as img:
        response = requests.post(
            'https://api.sightengine.com/1.0/check.json',
            files={'media': img},
            data={
                'models': 'genai',
                'api_user': API_USER,
                'api_secret': API_SECRET
            }
        )

    result = response.json()
    print(result)

    try:
        ai_score = result.get("type", {}).get("ai_generated", 0)

        confidence = ai_score * 100

        if ai_score > 0.7:
            label = "AI Generated"
        elif ai_score > 0.4:
            label = "Suspicious"
        else:
            label = "Real Image"

    except Exception as e:
        return jsonify({
            "error": "API parsing error",
            "details": str(e)
        })

    return jsonify({
        "result": label,
        "confidence": round(confidence, 2)
    })


if __name__ == "__main__":
    app.run(debug=True)
