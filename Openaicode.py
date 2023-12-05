import speech_recognition as sr
import openai

# Set your OpenAI API key
api_key = "Enter your API key here" 

# Create a recognizer instance1
recognizer = sr.Recognizer()

# Initialize the OpenAI API client
openai.api_key = api_key

# Function to recognize user voice input
def recognize_voice():
    with sr.Microphone() as source:
        print("Listening for a command...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source)
            user_input = recognizer.recognize_google(audio).lower()
            print(f"You said: {user_input}")
            return user_input
        except sr.WaitTimeoutError:
            print("No speech detected. Please speak.")
            return None
        except sr.UnknownValueError:
            print("Could not understand the audio. Please try again.")
            return None

# Function to respond to user commands using OpenAI ChatGPT
def respond_to_user_command(user_command):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use the ChatGPT model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_command}
            ]
        )
        assistant_response = response['choices'][0]['message']['content']
        return assistant_response
    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while processing your request."

# Function to display the user-friendly menu using text
def display_menu():
    print("Tauseeq's Voice/Text Assistant")
    print()
    print("How would you like to provide your command?")
    print()
    print("1. Speak (Say 'One' for 'Ask a question')")
    print("2. Type (Type '2' for 'Give a command')")
    print("3. Exit (Say 'Three' for 'Exit')")
    print()

# Main program loop
def main():
    print("Voice/Text Assistant is ready.")
    while True:
        display_menu()
        choice = input("Please select an option (1/2/3): ")
    
        if choice == "1":
            user_input = recognize_voice()
            if user_input:
                response = respond_to_user_command(user_input)
                print()
                print(f"Assistant: {response}")
        elif choice == "2":
            print()
            user_input = input("Please type your command: ")
            response = respond_to_user_command(user_input)
            print()
            print(f"Assistant: {response}")
        elif choice == "3":
            print("Exiting Voice/Text Assistant. Goodbye!")
            break
        else:
            print("Invalid choice. Please select a valid option (1/2/3).")

main()


