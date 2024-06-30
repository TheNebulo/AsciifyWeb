from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from . import asciify
import queue, os, cv2

app = None
q = queue.Queue()
db = SQLAlchemy()
DB_NAME = "database.db"

def get_video(id):
    from .models import Video
    
    with app.app_context():
        video = db.session.query(Video).get(int(id))
        return video

def get_videos(prompt=None):
    from .models import Video
    
    with app.app_context():
        if prompt == None: return db.session.query(Video).all()
        videos = db.session.query(Video).all()
        filtered = []
        for video in videos:
          if prompt.lower().strip() in video.name.lower().strip(): filtered.append(video)
        return filtered
    
def get_user(id):
    login_manager = app.login_manager
    from .models import User
    
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    return load_user(id)

def worker():
  from .models import Video
  
  with app.app_context():
    while True:
      item = q.get()
      if item is None:
        break
      print('Processing Video ID:', item)
      video = db.session.query(Video).get(int(item))
      user = get_user(video.user_id)
      user.alerts = str(video.id)+"_added"
      video.processing = True
      db.session.commit()
      
      if not os.path.exists(f'{os.getcwd()}/website/static/resources/videos'):
        os.mkdir(f'{os.getcwd()}/website/static/resources/videos')
      
      try:
        asciify.ascii_video(f'{os.getcwd()}/instance/{item}.mp4',f'{os.getcwd()}/website/static/resources/videos/{item}.mp4', progress_bar=False)
      except Exception as e:
        print(e)
        video = db.session.query(Video).get(int(item))
        video.processing = False
        video.in_queue = False
        video.failed = True
        user = get_user(video.user_id)
        user.alerts = str(video.id)+"_error"
        db.session.commit()
      else:
        video = db.session.query(Video).get(int(item))
        video.processing = False
        video.in_queue = False
        video.done = True
        user = get_user(video.user_id)
        user.alerts = str(video.id)+"_success"
        db.session.commit()
      os.remove(f'{os.getcwd()}/instance/{item}.mp4')
      vidcap = cv2.VideoCapture(f'{os.getcwd()}/website/static/resources/videos/{item}.mp4')
      success, image = vidcap.read()
      if success:
        cv2.imwrite(f"{os.getcwd()}/website/static/resources/images/{item}.png", image)
      q.task_done()
    

def create_app():
    global app
    app = Flask(__name__,instance_path=f'{os.getcwd()}/instance/')
    app.config['SECRET_KEY'] = 'PRE-PRODUCTION-KEY-001'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    with app.app_context():
        db.create_all()
        
    from .models import User

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
