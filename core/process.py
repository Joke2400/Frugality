from temp.test import run
class Process:
    
    def __init__(self, web_app, **kwargs):
        self.app = web_app
    
    def start(self):
        run()
        #self.app.run()