from flask import Flask
from flask import request
from flask import jsonify
from celery import Celery
import json
import time

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
        proj_id = task_form['proj_id']
        task_type = task_form['task_type']

        counter = 0
        task_id = 'TASK' + time.strftime('%y%m%d%H%M%S') + '{:02d}'.format(counter)
        app.logger.info('Creating task: %s' % task_id)

        task_name = task_form['task_name']
        task_config = {}
        task_config['proj_name'] = task_form['proj_name']
        task_config['train_data'] = task_form['train_data']
        task_config['val_data'] = task_form['val_data']
        task_config['enable_test'] = task_form['enable_test']
        task_config['test_data'] = task_form['test_data']
        task_config['model'] = task_form['model']
        task_config['param_set'] = task_form['param_set']

        task_executor.delay(
            taskid = task_id,
            tasktype = task_form['task_type'],
            traindata = task_config['train_data'],
            valdata = task_config['val_data'],
            enabletest = task_config['enable_test'],
            testdata = task_config['test_data'],
            model = task_config['model'],
            paramset = task_config['param_set']
        )

        response_content['task_form'] = task_form
        response_content['msg'] = 'success'
        response_content['code'] = 200

    except Exception as e:
        response_content['msg'] = str(e)
        response_content['code'] = 500

    return jsonify(response_content)

@celery.task
def task_executor(taskid, tasktype, traindata, valdata, enabletest, testdata, model, paramset):
    print(taskid, tasktype, traindata, valdata, enabletest, testdata, model, paramset)
    return

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)