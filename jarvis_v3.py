from groq import Groq
import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import os
import pyautogui
import psutil
import requests
import re
import sys
import webbrowser

# ✅ Load API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")

# ✅ Initialize Clients
client = Groq(api_key=GROQ_API_KEY)
engine = pyttsx3.init()
engine.setProperty('rate', 170)

def speak(text):
    """Jarvis speaks the given text aloud"""
    if not text:
        text = "Sorry Vansh, I couldn’t find any answer for that."
    if len(text) > 250:
        text = text[:250] + "..."
    print(f"🟢 Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    """Capture user voice command"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎧 Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        command = r.recognize_google(audio, language='en-in')
        print(f"🗣 You said: {command}")
        return command.lower()
    except:
        speak("Sorry, I didn’t catch that.")
        return ""

# ✅ SERPAPI Function (smart + short answer)
def search_serpapi(query):
    try:
        url = f"https://serpapi.com/search.json?q={query}&api_key={SERP_API_KEY}&hl=en&gl=in"
        response = requests.get(url).json()

        # 🎯 If query is about gold price
        if any(word in query for word in ["gold price", "price of gold", "sone ka daam", "gold rate"]):
            if 'answer_box' in response:
                for key in ['answer', 'snippet', 'result']:
                    if key in response['answer_box'] and re.search(r'₹[\d,]+', response['answer_box'][key]):
                        return response['answer_box'][key]
            if 'organic_results' in response:
                for result in response['organic_results']:
                    snippet = result.get('snippet', '')
                    match = re.search(r'₹[\d,]+', snippet)
                    if match:
                        return f"Current gold price in India is around {match.group(0)} per gram."
            if 'knowledge_graph' in response and 'description' in response['knowledge_graph']:
                desc = response['knowledge_graph']['description']
                match = re.search(r'₹[\d,]+', desc)
                if match:
                    return f"Gold price is {match.group(0)}."
            return "Sorry, I couldn’t find the latest gold price in INR."

        # 🎯 For general queries
        if 'answer_box' in response:
            box = response['answer_box']
            for key in ['answer', 'snippet', 'result']:
                if key in box:
                    return box[key]

        if 'organic_results' in response and len(response['organic_results']) > 0:
            snippet = response['organic_results'][0].get('snippet', '')
            return snippet if snippet else "Couldn't find live data."

        return "Couldn't fetch live data."
    except Exception as e:
        return f"SerpAPI error: {e}"

# ✅ GPT (Groq) fallback
def ask_gpt(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are Jarvis, a smart and friendly AI assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Groq error: {e}"

# ✅ Main Jarvis Logic
def run_jarvis():
    speak("Hello Vansh, I am Jarvis. How can I help you today?")
    while True:
        query = listen()

        if 'stop' in query or 'exit' in query:
            speak("Goodbye Vansh! Shutting down Jarvis.")
            sys.exit()

        elif 'time' in query:
            time = datetime.datetime.now().strftime('%I:%M %p')
            speak(f"The current time is {time}")

        elif 'open chrome' in query:
            speak("Opening Google Chrome")
            os.startfile(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

        elif 'open notepad' in query:
            speak("Opening Notepad")
            os.system("notepad")

        elif 'open vs code' in query or 'open visual studio' in query:
            speak("Opening Visual Studio Code")
            os.startfile(r"C:\Users\Vansh\AppData\Local\Programs\Microsoft VS Code\Code.exe")

        elif 'screenshot' in query:
            speak("Taking screenshot")
            img = pyautogui.screenshot()
            img.save("screenshot.png")
            speak("Screenshot saved in the current folder.")

        elif 'battery' in query:
            battery = psutil.sensors_battery()
            percent = battery.percent
            speak(f"Battery is at {percent} percent")

        elif 'play' in query:
            song = query.replace('play', '')
            speak(f"Playing {song}")
            pywhatkit.playonyt(song)

        elif 'search' in query:
            topic = query.replace('search', '')
            speak(f"Searching for {topic}")
            pywhatkit.search(topic)

        elif any(word in query for word in ['price', 'latest', 'today', 'current', 'score', 'weather', 'rate']):
            speak("Fetching the latest info...")
            result = search_serpapi(query)
            speak(result)

        else:
            speak("Let me think...")
            answer = ask_gpt(query)
            speak(answer)

# ✅ Run Jarvis
run_jarvis()
