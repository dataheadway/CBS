from flask import Flask, request, jsonify

app = Flask(__name__)

# Verification Token
VERIFY_TOKEN = "my_secure_token_123"


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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
