from flask import Blueprint, render_template, request, flash, redirect, send_file
from flask_login import login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from .models import Video
from . import db, q, get_video, get_videos, get_user, utils
import os, werkzeug

views = Blueprint('views', __name__)

def check_alerts(user_id):
  try:
    user = get_user(user_id)
    alert = user.alerts.split('_')
    if alert[1] == "success": flash(f"Video (ID: {alert[0]}) Uploaded", category='success')
    if alert[1] == "error": flash(f"Video (ID: {alert[0]}) Failed", category='error')
    if alert[1] == "added": flash(f"Video (ID: {alert[0]}) Started Processing", category='success')
    user.alerts = ""
    db.session.commit()
  except:
    pass

@views.errorhandler(werkzeug.exceptions.RequestEntityTooLarge)
def handle_too_large(e):
    flash('File too large',category="error")
    return redirect('/upload')

@views.route('/', methods=['GET', 'POST'])
def home():
  if current_user.is_authenticated: check_alerts(current_user.id)
  if request.method == "GET":
    videos = get_videos()
    return render_template("home.html", user=current_user,prompt=None, videos=videos)
    
  else:
      prompt = request.form.get('search')
      videos = get_videos(prompt)
      return render_template("home.html", user=current_user, videos = videos, prompt=prompt)


@views.route('/watch/<id>', methods=['GET'])
def watch(id=0):
    if current_user.is_authenticated: check_alerts(current_user.id)
    if get_video(id) == None: return 404
    if get_video(id).done != True: return 500
    return render_template("video.html", user=current_user,video=get_video(id),author=get_user(get_video(id).user_id))
  
@views.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
  if current_user.is_authenticated: check_alerts(current_user.id)
  if request.method == "GET":
    return render_template("upload.html", user=current_user)
  else:
      videos = get_videos()
      name = request.form.get('name')
      if name == None or len(name) < 4 or len(name) > 20:
          flash("Invalid name!",category="error")
          return redirect('/upload')      
      for video in videos:
        if video.user_id == current_user.id and video.in_queue:
          flash("Only one video in queue at a time.",category="error")
          return redirect('/upload')  
      video = request.files['video'] 
      if video.mimetype != "video/mp4":
        flash("Incorrect video type",category='error')
        return redirect('/upload')      
      new_video = Video(name=request.form.get('name'), user_id = current_user.id)
      db.session.add(new_video)
      db.session.commit()
      id = new_video.id
      video.save(f"{os.getcwd()}/instance/"+secure_filename(f"{id}.mp4"))
      db.session.commit()
      q.put(new_video.id)
      flash("Video added to queue!",category="success")
      return redirect("/upload")
  
@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if current_user.is_authenticated: check_alerts(current_user.id)
    if request.method == 'POST':
        if request.form.get('meta') == 'account':
            videos = get_videos()
            for video in videos:
              if video.user_id == current_user.id and video.in_queue:
                flash("Cannot delete while in queue.",category='error')
                return redirect('/settings')
            for video in videos:
              if video.user_id == current_user.id: 
                os.remove(f'{os.getcwd()}/website/static/resources/videos/{video.id}.mp4')
                os.remove(f'{os.getcwd()}/website/static/resources/images/{video.id}.png')
                db.session.delete(video)
            db.session.delete(current_user)
            db.session.commit()
            logout_user()
            flash("Account Deleted", category="success")
            return redirect('/')
        else:
            new_name = request.form.get('name')
            new_email = request.form.get('email')
            new_pass = request.form.get('password')
            print(type(new_email))
            change = False
            if new_name != current_user.name and new_name != "":
                if not utils.check_name(new_name):
                    flash("Invalid name!",category="error")
                    return redirect('/settings')
                change = True
                current_user.name = new_name
            if new_email != current_user.email and new_email != "":
                if not utils.check_email(new_email):
                    flash("Invalid email!",category="error")
                    return redirect('/settings')
                change = True
                current_user.email = new_email
            if new_pass != "" and not check_password_hash(current_user.password, new_pass):
                if not utils.check_pass(new_pass):
                    flash("Invalid password!",category="error")
                    return redirect('/settings')
                change = True
                current_user.password = generate_password_hash(new_pass, method="sha256")

            if change:
                flash("Updated account!", category="success")
                db.session.commit()
                return redirect('/settings')
            else:
                flash("Nothing to update",category="error")
                return redirect('/settings')
                
    return render_template("settings.html", user=current_user)


@views.route('/delete-video/<id>', methods=['GET'])
def delete_note(id=0):
  video = Video.query.get(id)
  if video:
    if video.user_id == current_user.id:
      os.remove(f'{os.getcwd()}/website/static/resources/videos/{id}.mp4')
      os.remove(f'{os.getcwd()}/website/static/resources/images/{id}.png')
      db.session.delete(video)
      db.session.commit()
      flash(f'Video (ID: {id}) Deleted',category='success')

  return redirect('/upload')