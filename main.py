
from kivy.app import App
from kivy.uix.label import Label

class EnglishMemory(App):
    def build(self):
        return Label(
            text="English Memory\nجاري تشغيل التطبيق"
        )

EnglishMemory().run()
