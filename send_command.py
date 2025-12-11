import requests
import argparse
import sys

# Default settings
DEFAULT_URL = "http://localhost:8000/process-command"
DEFAULT_DOCTOR = "starlight9219@gmail.com"

def send_to_speakspace(text, doctor_email, url):
    print(f"Sending: '{text}'")
    print(f"To: {doctor_email}")
    print(f"URL: {url}")
    print("...")
    
    try:
        response = requests.post(url, json={
            "text": text,
            "doctor_email": doctor_email
        })
        response.raise_for_status()
        result = response.json()
        
        print("\nSUCCESS!")
        print("-" * 20)
        intents = result.get('results', {}).get('parsed_intents', [])
        for item in intents:
            print(f"- {item}")
        print("-" * 20)
        
    except requests.exceptions.ConnectionError:
        print(f"\nERROR: Could not connect to {url}")
        print("Make sure the server is running!")
    except Exception as e:
        print(f"\nERROR: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send a command to SpeakSpace Orchestrator")
    parser.add_argument("text", help="The natural language text")
    parser.add_argument("--doctor", default=DEFAULT_DOCTOR, help="Doctor's email address")
    parser.add_argument("--url", default=DEFAULT_URL, help="Server URL")
    
    args = parser.parse_args()
    send_to_speakspace(args.text, args.doctor, args.url)
