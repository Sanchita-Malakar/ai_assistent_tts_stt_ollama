from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import threading
import json
import time
from queue import Queue

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from agent.graph import app as agent_app
from agent.stt import listen_and_convert
from agent.tts import speak
from agent.llm import SYSTEM_PROMPT

flask_app = Flask(__name__)
CORS(flask_app)

# Store conversation histories per session
conversations = {}
speech_queues = {}

def get_conversation_history(session_id):
    """Get or create conversation history for a session"""
    if session_id not in conversations:
        conversations[session_id] = [SystemMessage(content=SYSTEM_PROMPT)]
    return conversations[session_id]

@flask_app.route('/')
def index():
    """Serve the main UI"""
    return render_template('index.html')

@flask_app.route('/api/listen', methods=['POST'])
def listen():
    """Listen to user's voice and convert to text"""
    try:
        print("🎤 Starting to listen...")
        transcript = listen_and_convert()
        
        if transcript:
            print(f"✅ Transcribed: {transcript}")
            return jsonify({
                'success': True,
                'text': transcript
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No speech detected'
            }), 400
            
    except Exception as e:
        print(f"❌ Listen error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@flask_app.route('/api/chat', methods=['POST'])
def chat():
    """Process chat message and return response"""
    try:
        data = request.json
        user_input = data.get('message')
        session_id = data.get('session_id', 'default')
        
        if not user_input:
            return jsonify({
                'success': False,
                'error': 'No message provided'
            }), 400
        
        # Get conversation history
        conversation_history = get_conversation_history(session_id)
        
        # Prepare messages
        messages = conversation_history + [HumanMessage(content=user_input)]
        
        # Get response from agent
        print(f"💬 Processing: {user_input}")
        full_response = ""
        
        for event in agent_app.stream(
            {"messages": messages},
            stream_mode="values"
        ):
            if event["messages"]:
                last_msg = event["messages"][-1]
                
                if hasattr(last_msg, 'content') and last_msg.content:
                    full_response = last_msg.content
        
        print(f"🤖 Response: {full_response}")
        
        # Update conversation history
        conversation_history.append(HumanMessage(content=user_input))
        conversation_history.append(AIMessage(content=full_response))
        
        # Keep history manageable (last 10 exchanges)
        if len(conversation_history) > 21:
            conversations[session_id] = [conversation_history[0]] + conversation_history[-20:]
        
        return jsonify({
            'success': True,
            'response': full_response
        })
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@flask_app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """Stream chat response in real-time"""
    try:
        data = request.json
        user_input = data.get('message')
        session_id = data.get('session_id', 'default')
        
        if not user_input:
            return jsonify({'error': 'No message'}), 400
        
        conversation_history = get_conversation_history(session_id)
        messages = conversation_history + [HumanMessage(content=user_input)]
        
        def generate():
            full_response = ""
            
            for event in agent_app.stream(
                {"messages": messages},
                stream_mode="values"
            ):
                if event["messages"]:
                    last_msg = event["messages"][-1]
                    if isinstance(last_msg, AIMessage) and last_msg.content:
                        delta = last_msg.content[len(full_response):]
                        full_response = last_msg.content
                        yield f"data: {json.dumps({'delta': delta})}\n\n"
            
            # Update history
            conversation_history.append(HumanMessage(content=user_input))
            conversation_history.append(AIMessage(content=full_response))
            
            if len(conversation_history) > 21:
                conversations[session_id] = [conversation_history[0]] + conversation_history[-20:]
            
            yield f"data: {json.dumps({'done': True, 'full': full_response})}\n\n"
        
        return Response(generate(), mimetype='text/event-stream')
        
    except Exception as e:
        print(f"❌ Stream error: {e}")
        return jsonify({'error': str(e)}), 500

@flask_app.route('/api/speak', methods=['POST'])
def speak_text():
    """Convert text to speech"""
    try:
        data = request.json
        text = data.get('text')
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'No text provided'
            }), 400
        
        # Run speak in separate thread to avoid blocking
        thread = threading.Thread(target=speak, args=(text,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Speaking started'
        })
        
    except Exception as e:
        print(f"❌ Speak error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@flask_app.route('/api/clear', methods=['POST'])
def clear_history():
    """Clear conversation history"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        
        conversations[session_id] = [SystemMessage(content=SYSTEM_PROMPT)]
        
        return jsonify({
            'success': True,
            'message': 'History cleared'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@flask_app.route('/api/mode', methods=['POST'])
def set_mode():
    """Set voice/text mode"""
    try:
        data = request.json
        mode = data.get('mode', 'voice')
        
        return jsonify({
            'success': True,
            'mode': mode
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 AI VOICE ASSISTANT SERVER STARTING...".center(70))
    print("=" * 70)
    print()
    print("📱 Web Interface: http://localhost:5000".center(70))
    print("🎤 Voice Mode: Enabled".center(70))
    print("🤖 LangGraph Agent: Ready".center(70))
    print("🔧 Tools: Web Search, Wikipedia".center(70))
    print()
    print("=" * 70)
    
    flask_app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)