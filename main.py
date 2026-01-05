import sys
import time
from langchain_core.messages import HumanMessage, SystemMessage
from agent.graph import app
from agent.stt import listen_and_convert
from agent.tts import speak
from agent.llm import SYSTEM_PROMPT

# Configuration
MODE = "voice"  # Change to "text" for text-only mode
MAX_RETRIES = 3
SILENCE_TIMEOUT = 2  # seconds


def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("🤖 AI Voice Assistant".center(60))
    print("=" * 60)
    print(f"\nMode: {MODE.upper()}")
    if MODE == "voice":
        print("• Speak clearly after the prompt")
        print("• Say 'exit' or 'quit' to stop")
    else:
        print("• Type your message")
        print("• Type 'exit' to quit")
    print("\nCommands:")
    print("• 'switch mode' - Toggle between voice/text")
    print("• 'clear' - Clear conversation history")
    print("=" * 60)


def get_user_input(mode="voice"):
    """Get user input via voice or text"""
    if mode == "voice":
        retries = 0
        while retries < MAX_RETRIES:
            transcript = listen_and_convert()
            
            if transcript:
                print(f"\n📝 You said: {transcript}")
                return transcript
            
            retries += 1
            if retries < MAX_RETRIES:
                print(f"⚠️  Didn't catch that. Try again ({retries}/{MAX_RETRIES})")
                speak("I didn't catch that. Please try again.")
                time.sleep(0.5)
        
        print("❌ Max retries reached. Switching to text mode.")
        speak("I'm having trouble hearing you. Let's switch to text mode.")
        return None
    
    else:  # text mode
        user_input = input("\n💬 You: ").strip()
        return user_input if user_input else None


def stream_agent_response(query, conversation_history):
    """Stream agent response and return full text"""
    print("\n🤖 Agent: ", end="", flush=True)
    
    full_response = ""
    
    try:
        # Prepare messages with conversation history
        messages = conversation_history + [HumanMessage(content=query)]
        
        # Stream response
        for event in app.stream(
            {"messages": messages},
            stream_mode="values"
        ):
            if event["messages"]:
                last_msg = event["messages"][-1]
                
                # Only process AI messages
                if hasattr(last_msg, 'content') and last_msg.content:
                    new_content = last_msg.content
                    
                    # Print incremental content
                    if new_content != full_response:
                        if new_content.startswith(full_response):
                            delta = new_content[len(full_response):]
                            print(delta, end="", flush=True)
                        else:
                            print(new_content, end="", flush=True)
                        
                        full_response = new_content
        
        print()  # Newline after response
        return full_response
    
    except Exception as e:
        error_msg = f"Sorry, I encountered an error: {str(e)}"
        print(f"\n❌ {error_msg}")
        return error_msg


def handle_special_commands(user_input, mode):
    """Handle special commands like mode switching"""
    lower_input = user_input.lower().strip()
    
    if lower_input in ["exit", "quit", "bye", "goodbye"]:
        return "exit", mode
    
    if lower_input in ["switch mode", "change mode", "toggle mode"]:
        new_mode = "text" if mode == "voice" else "voice"
        print(f"\n🔄 Switching to {new_mode.upper()} mode")
        speak(f"Switching to {new_mode} mode")
        return "switch", new_mode
    
    if lower_input == "clear":
        print("\n🗑️  Conversation history cleared")
        speak("Conversation cleared")
        return "clear", mode
    
    return None, mode


def main():
    """Main application loop"""
    global MODE
    
    print_banner()
    
    # Initialize conversation history
    conversation_history = [SystemMessage(content=SYSTEM_PROMPT)]
    
    # Welcome message
    welcome_msg = "Hello! I'm your AI assistant. How can I help you today?"
    print(f"\n🤖 Agent: {welcome_msg}\n")
    if MODE == "voice":
        speak(welcome_msg)
    
    # Main loop
    while True:
        try:
            # Get user input
            user_input = get_user_input(MODE)
            
            if not user_input:
                continue
            
            # Handle special commands
            command, MODE = handle_special_commands(user_input, MODE)
            
            if command == "exit":
                goodbye_msg = "Goodbye! Have a great day!"
                print(f"\n👋 {goodbye_msg}")
                speak(goodbye_msg)
                break
            
            elif command == "switch":
                continue
            
            elif command == "clear":
                conversation_history = [SystemMessage(content=SYSTEM_PROMPT)]
                continue
            
            # Get agent response
            response = stream_agent_response(user_input, conversation_history)
            
            if response:
                # Update conversation history (keep last 10 messages)
                conversation_history.append(HumanMessage(content=user_input))
                conversation_history.append(SystemMessage(content=response))
                
                # Keep history manageable
                if len(conversation_history) > 21:  # System prompt + 10 exchanges
                    conversation_history = [conversation_history[0]] + conversation_history[-20:]
                
                # Speak response in voice mode
                if MODE == "voice":
                    speak(response)
            
            # Small delay between turns
            time.sleep(0.3)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted. Exiting...")
            speak("Goodbye")
            break
        
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            print("Continuing...")
            time.sleep(1)
    
    print("\n" + "=" * 60)
    print("Session ended.".center(60))
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)