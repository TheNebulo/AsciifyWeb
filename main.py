from website import create_app, worker, models, db
import threading, os

if __name__ == '__main__':
    app = create_app()
    with app.app_context():  
        videos = db.session.query(models.Video).all()
        for video in videos:
            if video.in_queue == True and video.done == False:
                video.processing = False
                video.failed = True
                video.in_queue = False
            db.session.commit()
    t = threading.Thread(target=worker)
    t.start()
    app.run(host='0.0.0.0',debug=False, threaded=True)
