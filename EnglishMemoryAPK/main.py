from kivy.app import App
from kivy.uix.webview import WebView

class EnglishMemory(App):
    def build(self):
        return WebView(
            url="file:///android_asset/index.html"
        )

EnglishMemory().run()
