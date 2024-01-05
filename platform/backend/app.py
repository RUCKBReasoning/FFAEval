import random

from flask import Flask, request
from flask_socketio import SocketIO

from model_api import get_stream_response
from mongodb import get_bot_all, update_session_by_regenerate, update_session_content, \
    update_session_choose, get_session_rank_and_order

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

@app.route("/choose", methods=['POST'])
def choose():
    data = request.get_json()
    update_session_choose(data['session_id'], data['chosen_msg_index'])
    return {"status": "success"}

@app.route("/terminate", methods=['POST'])
def terminate():
    data = request.get_json()
    rank_list, order_list = get_session_rank_and_order(data['session_id'])
    return {
        "rank_list": rank_list,
        "order_list": order_list
    }

@app.route("/bot", methods=['POST'])
def api_bot():
    bot_list = get_bot_all()
    return {"bot_list": [bot['name'] for bot in bot_list]}

@socketio.on('message', namespace='/chat')
def api_message(data):
    bot_list = get_bot_all()
    random.shuffle(bot_list)

    stream_response_list = []
    for bot in bot_list:
        stream_response = get_stream_response(bot['name'], bot['api_key'],
                                              bot['base_url'], data['msg_send'])
        stream_response_list.append(stream_response)

    msg = {
        'user': data['msg_send'][-1],
        'bot': [{'name': bot['name'], 'value': ''} for bot in bot_list],
        'choice': -1
    }
    is_finish = False
    while not is_finish:
        chunk_list = []
        is_finish = True
        for i in range(len(stream_response_list)):
            chunk = next(stream_response_list[i], None)
            if chunk is None:
                chunk_list.append('')
            else:
                content = chunk.choices[0].delta.content
                if content != None:
                    msg['bot'][i]['value'] += content
                    chunk_list.append(content)
                    is_finish = False
                else:
                    chunk_list.append('')
        if not is_finish:
            socketio.emit('message', {'msg_list': chunk_list, 'state': 'unfinished'}, namespace='/chat')

    # whether regenerate
    if 'regenerate' in data and data['regenerate']:
        update_session_by_regenerate(data['session_id'], msg)
    else:
        update_session_content(data['session_id'], msg)
    socketio.emit('message', {'state': 'finished'}, namespace='/chat')

if __name__ == '__main__':
    socketio.run(app)
