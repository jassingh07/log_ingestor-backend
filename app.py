from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS  # Import CORS from Flask-CORS
from pymongo.server_api import ServerApi
import os # for environement variables
from dotenv import load_dotenv

load_dotenv()#load environment variables

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes in the app

uri = "mongodb+srv://"+ os.getenv('MONGO_USERNAME') + ":" + os.getenv('MONGO_PASSWORD') +"@cluster0.rhrrq3r.mongodb.net/?retryWrites=true&w=majority",


# Connect to MongoDB
client = MongoClient(uri, server_api=ServerApi('1'))  # Update with your MongoDB connection string
db = client["logs_db"]  # Choose or create a database
logs_collection = db["logs"]  # Choose or create a collection

@app.route('/ingest', methods=['POST'])
def ingest():
    log_data = request.json
    # Insert log into MongoDB
    result = logs_collection.insert_one(log_data)

    return jsonify({"status": "success", "message": "Log ingested successfully", "log_id": str(result.inserted_id)})

@app.route('/query', methods=['GET'])
def query():
    # Get query parameters from the request
    level = request.args.get('level')
    message = request.args.get('message')
    resourceId = request.args.get('resourceId')
    timestamp = request.args.get('timestamp')

    # Construct the query using $or for an OR behavior
    query = {
        '$or': [
            {'level': level} if level else {},
            {'message': message} if message else {},
            {'resourceId': resourceId} if resourceId else {},
            {'timestamp': timestamp} if timestamp else {},
            # Add more conditions as needed
        ]
    }

    # Execute the query and retrieve the logs
    logs = list(logs_collection.find(query))

    # Convert ObjectId to string for JSON serialization
    for log in logs:
        log['_id'] = str(log['_id'])

    # Return the logs as JSON
    return jsonify({'logs': logs, 'status': 'success'})

if __name__ == '__main__':
    app.run(port=3000)
