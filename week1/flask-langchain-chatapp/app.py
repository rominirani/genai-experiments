from flask import Flask, render_template, request, jsonify, redirect, session
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_vertexai import ChatVertexAI
from langchain.memory import ChatMessageHistory

app = Flask(__name__)
app.secret_key = 'L200-langchain-chat-app'

llm = ChatVertexAI(
    model="gemini-1.5-flash-001",
    temperature=0,
    max_tokens=None,
    max_retries=6,
    stop=None,
)
# Create a system message
system_message = SystemMessage(content="You are a helpful Travel assistant. You answer only Travel queries. Do not answer any non-travel queries and politely refuse them")

# Use a dictionary to store chat histories per user
user_sessions = {}

#history = ChatMessageHistory()
#history.add_message(system_message)

 # Create a list of valid users and their passwords
valid_users = {
        'admin1': 'admin1',
        'admin2': 'admin2',
        'admin3': 'admin3',
        'admin4': 'admin4',
        'admin5': 'admin5'
    }

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/index')
def index():
    if 'logged_in' in session and session['logged_in']:
        # Initialize chat history for new users
        if session['username'] not in user_sessions:
            user_sessions[session['username']] = ChatMessageHistory()
            user_sessions[session['username']].add_message(
                system_message)
        # Get the chat history for the current user
        history = user_sessions.setdefault(
            session['username'], ChatMessageHistory())
        messages = history.messages
        chat_history = []
        for message in messages:
            if isinstance(message, HumanMessage):
                chat_history.append({
                    'sender': 'user',
                    'message': message.content
                })
            elif isinstance(message, AIMessage):
                chat_history.append({
                    'sender': 'bot',
                    'message': message.content
                })
        return render_template('index.html', chat_history=chat_history)
    else:
        return redirect('/')  # Redirect to login if not logged in

@app.route('/login', methods=['POST'])
def authenticate():
    username = request.form.get('username')
    password = request.form.get('password')

    if username in valid_users and valid_users[username] == password:
        session['logged_in'] = True
        session['username'] = username
        return redirect('/index')
    else:
        return render_template('login.html', error='Invalid username or password')
        
@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # Remove 'logged_in' from session
    session.pop('username', None)   # Remove 'username' from session (optional)
    return redirect('/')  # Redirect to login page    

@app.route('/chat', methods=['POST'])
def chat():
    
    if 'username' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    
    user_message = request.json['message']
    if not isinstance(user_message, str) or not user_message.strip():
        return jsonify({'error': 'Invalid message'}), 400

    # Get the chat history for the current user
    history = user_sessions.setdefault(session['username'], ChatMessageHistory())
    history.add_user_message(user_message)
    ai_msg = llm.invoke(history.messages)
    history.add_ai_message(ai_msg.content)
    response = ai_msg.content
    print(response)
    print(history.messages)

    return jsonify({'response': response})

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    """Clears the chat history for the current user."""
    if 'username' in session:
        if session['username'] in user_sessions:
            user_sessions[session['username']].clear()
            return jsonify({'message': 'Chat history cleared!'})
        else:
            return jsonify({'message': 'No chat history found for this user.'}), 404
    else:
        return jsonify({'error': 'User not logged in'}), 401

if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0', port=8080)