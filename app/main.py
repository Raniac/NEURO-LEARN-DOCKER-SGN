from flask import Flask
from flask import request
from flask import jsonify
from celery import Celery
import json

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://127.0.0.1:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://127.0.0.1:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

## Loggers
# app.logger.debug('A value for debugging')
# app.logger.info('An info for notice')
# app.logger.warning('A warning occurred (%d apples)', 42)
# app.logger.error('An error occurred')

@app.route('/')
def hello_world():
    return 'Hello, Benny!'

@app.route('/api/v0/new_task', methods=['POST'])
def new_task():
    response_content = {}

    try:
        task_form = json.loads(request.data.decode("utf-8"))
        app.logger.debug(task_form['proj_id'])

        # task_executor.delay(
        #     tasktype = task_form['task_type']
        # )

        response_content['task_form'] = task_form
        response_content['msg'] = 'success'
        response_content['code'] = 200

    except Exception as e:
        response_content['msg'] = str(e)
        response_content['code'] = 500

    return jsonify(response_content)

@celery.task
def task_executor(tasktype):
    print(tasktype)
    return

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)