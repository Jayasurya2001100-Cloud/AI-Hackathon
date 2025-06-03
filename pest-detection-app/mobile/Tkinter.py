import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import requests
import speech_recognition as sr
import pyttsx3
import threading

backend_url = "http://183.82.102.232:8000/predict-image/"

class PestDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pest Detection")
        self.root.geometry("600x500")
        self.root.configure(bg="#f5f5f5")

        self.tts_engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()

        self.create_widgets()

    def create_widgets(self):
        # Title
        tk.Label(self.root, text="🪲 Pest Detection App", font=("Helvetica", 18, "bold"), bg="#f5f5f5").pack(pady=10)

        # Image display
        self.image_label = tk.Label(self.root, bg="#f5f5f5")
        self.image_label.pack(pady=10)

        # Buttons
        button_frame = tk.Frame(self.root, bg="#f5f5f5")
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="📁 Select Image", command=self.pick_image).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="🎙 Voice Input", command=self.voice_input).grid(row=0, column=1, padx=10)

        # Result
        self.result_text = tk.StringVar()
        self.result_label = tk.Label(self.root, textvariable=self.result_text, wraplength=500, font=("Arial", 14), bg="#f5f5f5")
        self.result_label.pack(pady=20)

    def pick_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if filepath:
            self.display_image(filepath)
            threading.Thread(target=self.predict_image, args=(filepath,)).start()

    def display_image(self, path):
        img = Image.open(path)
        img = img.resize((250, 250))
        img_tk = ImageTk.PhotoImage(img)
        self.image_label.configure(image=img_tk)
        self.image_label.image = img_tk

    def predict_image(self, filepath):
        self.result_text.set("🔍 Analyzing image...")
        try:
            with open(filepath, "rb") as f:
                files = {"file": f}
                response = requests.post(backend_url, files=files)
                if response.status_code == 200:
                    data = response.json()
                    pest = data.get("pest", "Unknown")
                    conf = float(data.get("confidence", 0)) * 100
                    result = f"🪲 Pest: {pest}\n🎯 Confidence: {conf:.2f}%"
                else:
                    result = f"❌ Error: {response.status_code}"
        except Exception as e:
            result = f"⚠️ Exception: {str(e)}"

        self.result_text.set(result)
        self.tts_engine.say(result)
        self.tts_engine.runAndWait()

    def voice_input(self):
        def listen():
            try:
                with sr.Microphone() as source:
                    self.result_text.set("🎧 Listening...")
                    audio = self.recognizer.listen(source, timeout=5)
                    text = self.recognizer.recognize_google(audio)
                    self.result_text.set(f"🗣 You said: {text}")
                    self.tts_engine.say(f"You said: {text}")
                    self.tts_engine.runAndWait()

                    if "capture" in text.lower():
                        self.pick_image()
            except sr.UnknownValueError:
                self.result_text.set("❗ Could not understand audio.")
            except sr.RequestError:
                self.result_text.set("❗ Speech service unavailable.")
            except Exception as e:
                self.result_text.set(f"❗ Error: {str(e)}")

        threading.Thread(target=listen).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = PestDetectorApp(root)
    root.mainloop()
