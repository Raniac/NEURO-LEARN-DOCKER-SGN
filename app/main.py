from flask import Flask
from flask import request
from celery import Celery

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://127.0.0.1:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://127.0.0.1:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@app.route('/')
def hello_world():
    return 'Hello, Benny!'

@app.route('/api/v0/newtask', methods=['POST'])
def new_task():
    task = task_executor.delay(10, 20)
    return 'Successfully created a task!'

@celery.task
def task_executor(arg1, arg2):
    result = arg1 + arg2
    return result

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)