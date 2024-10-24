from flask import Flask, request, jsonify, redirect
import requests # type: ignore

app = Flask(__name__)

# Verification Token
VERIFY_TOKEN = "my_secure_token_123"

# Your Instagram App credentials
CLIENT_ID = "556879356850932"
CLIENT_SECRET = "a33c58e9c6ddc8e9e5e60080ea4997ea"
REDIRECT_URI = "https://cbs-beta.vercel.app/webhook"

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
        print('Received Instagram event:', data)
        # Process the event here

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
