from groq import Groq
import speech_recognition as sr
import pyttsx3
import datetime
import os
import pywhatkit
import psutil
import pyautogui
import requests
import re
import webbrowser
import sys
import time

# ✅ API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")

# ✅ Clients
client = Groq(api_key=GROQ_API_KEY)

# ✅ Voice Engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # male voice
engine.setProperty('rate', 175)

def speak(text):
    """Speak aloud and print."""
    if not text:
        text = "Sorry Vansh, I couldn’t find an answer."
    print(f"🟢 Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()
    time.sleep(0.3)  # small pause to avoid overlap

def listen():
    """Listen from microphone."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎧 Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        query = r.recognize_google(audio, language='en-in')
        print(f"🗣 You said: {query}")
        return query.lower()
    except:
        speak("Sorry, I didn’t catch that.")
        return ""

# ✅ SerpAPI Search
def search_serpapi(query):
    try:
        url = f"https://serpapi.com/search.json?q={query}&api_key={SERP_API_KEY}&hl=en&gl=in"
        response = requests.get(url).json()
        if 'answer_box' in response:
            for k in ['answer', 'snippet', 'result']:
                if k in response['answer_box']:
                    return response['answer_box'][k]
        if 'organic_results' in response and len(response['organic_results']) > 0:
            return response['organic_results'][0].get('snippet', 'No live data found.')
        return "Couldn't fetch data."
    except Exception as e:
        speak(f"Error while fetching: {e}")
        return None

# ✅ Groq Chat
def ask_groq(prompt):
    try:
        res = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are Jarvis, an AI assistant that responds clearly and briefly."},
                {"role": "user", "content": prompt}
            ]
        )
        return res.choices[0].message.content
    except Exception as e:
        speak(f"Groq error: {e}")
        return None

# ✅ Main Loop
def run_jarvis():
    speak("Hello Vansh, Jarvis voice system is online.")
    while True:
        query = listen()
        if not query:
            continue

        if 'exit' in query or 'stop' in query:
            speak("Goodbye Vansh. Shutting down.")
            sys.exit()

        elif 'time' in query:
            speak("The time is " + datetime.datetime.now().strftime("%I:%M %p"))

        elif 'open youtube' in query:
            speak("Opening YouTube")
            webbrowser.open("https://youtube.com")

        elif 'open google' in query:
            speak("Opening Google")
            webbrowser.open("https://google.com")

        elif 'battery' in query:
            battery = psutil.sensors_battery()
            speak(f"Battery is at {battery.percent} percent")

        elif 'play' in query:
            song = query.replace('play', '')
            speak(f"Playing {song}")
            pywhatkit.playonyt(song)

        elif any(word in query for word in ['price', 'today', 'latest', 'current', 'weather']):
            speak("Fetching live data, please wait.")
            result = search_serpapi(query)
            if result:
                speak(result)
            else:
                speak("Sorry, no information available right now.")

        else:
            speak("Let me think...")
            answer = ask_groq(query)
            if answer:
                speak(answer)
            else:
                speak("Sorry, I didn’t get any response from Groq.")

# ✅ Run
if __name__ == "__main__":
    run_jarvis()
