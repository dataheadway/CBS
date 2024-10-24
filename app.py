from flask import Flask, request, jsonify, redirect
import requests 

app = Flask(__name__)

# Verification Token
VERIFY_TOKEN = "my_secure_token_123"

# Your Instagram App credentials
CLIENT_ID = "556879356850932"
CLIENT_SECRET = "a33c58e9c6ddc8e9e5e60080ea4997ea"
REDIRECT_URI = "https://cbs-beta.vercel.app/webhook"
GRAPH_API_URL = "https://graph.facebook.com/v17.0"
ACCESS_TOKEN = "YOUR_PAGE_ACCESS_TOKEN"  # Replace with the obtained access token

# Welcome route
@app.route('/')
def welcome():
    return "Welcome to CBS", 200

# Handle webhook verification (GET request)
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode and token:
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print("WEBHOOK VERIFIED")
            return challenge, 200
        else:
            return "Forbidden", 403

# Handle webhook events (POST request)
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = request.get_json()

    if data['object'] == 'instagram':
        for entry in data.get('entry', []):
            for messaging in entry.get('messaging', []):
                if 'message' in messaging:
                    sender_id = messaging['sender']['id']
                    message_text = messaging['message'].get('text', '')

                    # Log the incoming message
                    print(f'Received message from {sender_id}: {message_text}')

                    # Example: Send an automated response back
                    send_instagram_message(sender_id, "Thank you for your message!")

    return "EVENT RECEIVED", 200

# OAuth Redirect URL for Instagram
@app.route('/instagram/callback', methods=['GET'])
def instagram_callback():
    code = request.args.get('code')

    if code:
        # Exchange the code for an access token
        access_token_url = 'https://api.instagram.com/oauth/access_token'
        payload = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'code': code
        }
        
        try:
            response = requests.post(access_token_url, data=payload)
            response_data = response.json()
            
            if 'access_token' in response_data:
                access_token = response_data['access_token']
                user_id = response_data['user_id']
                print(f"Access Token: {access_token}, User ID: {user_id}")
                return "Instagram login successful! Access Token obtained.", 200
            else:
                return f"Failed to obtain access token: {response_data}", 400
        except Exception as e:
            return f"An error occurred: {str(e)}", 500
    else:
        return "Authorization code not provided", 400

def send_instagram_message(recipient_id, message_text):
    """
    Sends a message to a user on Instagram using the Instagram Graph API.
    """
    url = f"{GRAPH_API_URL}/me/messages"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        },
        "messaging_type": "RESPONSE"
    }
    params = {
        "access_token": ACCESS_TOKEN
    }

    try:
        response = requests.post(url, json=payload, params=params, headers=headers)
        response_data = response.json()
        if response.status_code == 200:
            print(f"Message sent successfully: {response_data}")
        else:
            print(f"Failed to send message: {response_data}")
    except Exception as e:
        print(f"An error occurred while sending message: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
