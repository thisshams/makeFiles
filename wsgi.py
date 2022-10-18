import os,sys
sys.path.append(os.apth.abspath(os.path.join(os.apth.dirname(__file__),"..")))
from main import app
app=app()
if __name__=="__main__":
    app.run()