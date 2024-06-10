import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
from googletrans import Translator
import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
from threading import Thread
import serial
import time


port = "COM5"  # Replace this with your Bluetooth port
baudrate = 9600

# Open serial port
ser = serial.Serial(port, baudrate)
# time.sleep(2)  # Wait for the connection to establish

# # Request input from the user
data = ""

# # Send data via Bluetooth
ser.write(data.encode('utf-8'))
print("Connect successfully!")

class BolbolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bolbol Robot")

        # Configure generativeai library using API key
        google_api_key = "AIzaSyCSPMSX4NrwtD0p_BrgKiHZpjO_clyOI0A"  # استبدلها بمفتاح API الخاص بك
        genai.configure(api_key=google_api_key)
        self.model = genai.GenerativeModel('gemini-1.0-pro-latest')

        # Initialize text-to-speech engine
        self.wel = pyttsx3.init()
        voices = self.wel.getProperty('voices')
        self.wel.setProperty('voice', voices[1].id)    # اختيار صوت اللي بيتكلم
        self.wel.setProperty('rate', 130)              # سرعة كلامه

        # Initialize translator
        self.translator = Translator()                 # تجهيز دالة الترجمة

        self.initial_message = '''
        I want you to imagine that you are a robot assistant to a doctor in a hospital. 
        The name of this robot is Bolbol or Bolbol Or whatever name the person calls you, 
        and he is a smart friend and assistant to a doctor named Zain. 
        Zain is also the inventor who invented Bolbol. Bolbol follows up on patients' conditions, 
        entertains them, and answers their questions. 
        It is a robot that can move and serve patients, and it is also an expert in medicine.
        
        any answer must be breafly
        '''


        self.conversation = self.initial_message

        self.load_background_image()                # استدعاء صورة الخلفية

        self.label = tk.Label(root, text="Bolbol Robot", bg='brown', font=("Helvetica", 24))  # اسم التطبيق ولونه وحجمه
        self.label.place(x=590, y=20)                                                         # مكانه

        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.NONE, width=128, height=18)  # حقل كتابة الكلام بالأنجليزي
        self.text_area.place(x=165, y=83)                                                     # مكانه
 
        self.translation_label = tk.Label(root, text="Translate to Arabic", bg='yellow')      # كلمة الترجمة
        self.translation_label.place(x=630, y=378)                                            # مكانه

        self.translation_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=10)  # حقل كتابة اللغة بالعربي
        self.translation_area.place(x=165, y=400)                                                   # مكانه

        self.button = tk.Button(root, text='Speak', command=self.on_button_press)              # زرار الصوت
        self.button.place(x=630, y=580)

        # زراير الحركة
        btn_forward = tk.Button(root, text="Forward", width=10, height=2)
        btn_forward.place(x=1025, y=385)
        btn_forward.bind("<ButtonPress>", lambda event: self.start_moving("forward"))
        btn_forward.bind("<ButtonRelease>", lambda event: self.stop_moving())

        btn_backward = tk.Button(root, text="Backward", width=10, height=2)
        btn_backward.place(x=1025, y=515)
        btn_backward.bind("<ButtonPress>", lambda event: self.start_moving("backward"))
        btn_backward.bind("<ButtonRelease>", lambda event: self.stop_moving())

        btn_left = tk.Button(root, text="Left", width=10, height=2)
        btn_left.place(x=925, y=450)
        btn_left.bind("<ButtonPress>", lambda event: self.start_moving("left"))
        btn_left.bind("<ButtonRelease>", lambda event: self.stop_moving())

        btn_right = tk.Button(root, text="Right", width=10, height=2)
        btn_right.place(x=1125, y=450)
        btn_right.bind("<ButtonPress>", lambda event: self.start_moving("right"))
        btn_right.bind("<ButtonRelease>", lambda event: self.stop_moving())

        # auto
        btn_auto = tk.Button(root, text="auto", width=10, height=2, command=self.auto)
        btn_auto.place(x=1025, y=450)
        #180 degree

        self.moving = False

    # تظبيط الخلفية
    def load_background_image(self):
        self.background_image = Image.open(r"E:\\Year 5\\Second term\\project\\Mohammed Amr\\n.jpg")
        window_width = self.root.winfo_screenwidth()                          # تجهيز العرض
        window_height = self.root.winfo_screenheight()                        # تجهيز الطول
        self.background_image = self.background_image.resize((window_width, window_height), Image.LANCZOS)
        self.background_photo = ImageTk.PhotoImage(self.background_image)
        self.background_label = tk.Label(self.root, image=self.background_photo)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)       # تملى الصفحة

    # لما تدوس على زرار الصوت
    def on_button_press(self):
        self.text_area.delete('1.0', tk.END)                                # يمسح النص السابق 
        self.text_area.insert(tk.END, "Listening...")                       # يجيب كلمة الاستماع
        Thread(target=self.listen_loop, daemon=True).start()                # يفضل يسمع طوالي

    # تظبيط الصوت بقا
    def listen_loop(self):
        recognizer = sr.Recognizer()
        while True:
            with sr.Microphone() as mic:                                    # تجهيز الميكرفون
                print("Listening...")
                recognizer.adjust_for_ambient_noise(mic, duration=1)  # زودت مدة ضبط الضوضاء
                audio = recognizer.listen(mic)                              # الأستماع للميكرفون
                try:
                    print("Recognizing...")
                    query = recognizer.recognize_google(audio, language='en') # تحويل الصوت لكلام بالأنجليزي
                    print(f"You said: {query}")
                    self.text_area.delete('1.0', tk.END)
                    self.text_area.insert(tk.END, f"You said: {query}")
                    
                    if "stop" in query:                                       # لما اقول ستوب يقف
                        self.text_area.delete('1.0', tk.END)
                        self.text_area.insert(tk.END, "Robot stopped.")
                        
                    # لما اقول كذا يتحرك
                    elif "give me the medicine" in query:
                        response_text = "I will give you the medicine"
                        self._180_degree()
                        self.auto()
                    elif "go to the other side" in query:
                        response_text = "I will go to the patient"
                        self._180_degree()
                        self.auto()

                    else:
                        self.conversation += f"\nUser: {query}\nBolbol: "
                        response_text = self.send_text_to_gemini(self.conversation)
                    
                    translation = self.translator.translate(response_text, dest='ar').text
                    
                    self.text_area.delete('1.0', tk.END)
                    self.text_area.insert(tk.END, response_text + "\n")
                    self.translation_area.delete('1.0', tk.END)
                    self.translation_area.insert(tk.END, translation + "\n")
                    self.conversation += response_text

                    # بعد عرض النصوص، تشغيل دالة النطق
                    self.speak(response_text)
                
                except sr.UnknownValueError:
                    pass
                except sr.RequestError as e:
                    pass
                except Exception as e:
                    print(e)
                    pass

    def speak(self, audio):
        self.wel.say(audio)         # نطق النص
        self.wel.runAndWait()       # لستنى لما يخلص كلام

    def send_text_to_gemini(self, conversation):
        try:
            response = self.model.generate_content(conversation)        # بعت الرسالة لجيميناي
            return response._result.candidates[0].content.parts[0].text
        except Exception as e:
            print(f"Error: {e}")
            return "I don't understand. Can you ask another way?"

    def start_moving(self, direction):
        self.moving = True
        self.move(direction)

    def stop_moving(self):
        self.moving = False
        response_text = "I am stop"
        data = "S"
        ser.write(data.encode('utf-8'))
        self.speak(response_text)
        print(response_text)

    def move(self, direction):
        if self.moving:
            if direction == "forward":
                data = "F"
                ser.write(data.encode('utf-8'))
                response_text = "I will move forward"
            elif direction == "backward":
                data = "B"
                ser.write(data.encode('utf-8'))
                response_text = "I will move backward"
            elif direction == "left":
                data = "L"
                ser.write(data.encode('utf-8'))
                response_text = "I will turn left"
            elif direction == "right":
                response_text = "I will turn right"
                data = "R"
                ser.write(data.encode('utf-8'))

            
            self.speak(response_text)
            print(response_text)
            self.root.after(100, lambda: self.move(direction))
    
    def auto(self):
        response_text = "I will move auto"
        data = "H"
        ser.write(data.encode('utf-8'))
        print(response_text)
        response_text = "I will move auto"
        time.sleep(2)
        
    def _180_degree(self):
        response_text = "I will move 180 degrees "
        data = "J"
        ser.write(data.encode('utf-8'))
        self.speak(response_text)
        print(response_text)
                

root = tk.Tk()
app = BolbolApp(root)
root.mainloop()





# D:\\kivy-app\\bolbo-back.jpg



