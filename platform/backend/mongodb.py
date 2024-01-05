from pymongo import MongoClient

client = MongoClient('IP_ADDRESS', 27017, username='USERNAME', password='PASSWORD').ffa_eval

def insert_model(model_name, api_key, base_url):
    res = client.model.insert_one({
        'name': model_name,
        'api_key': api_key,
        'base_url': base_url,
        'is_activate': True
    })
    return res

def update_model_state(model_name, is_activate):
    res = client.model.update_one(
        {'name': model_name},
        {'$set': {'is_activate': is_activate}}
    )
    return res

def delete_model(model_name):
    res = client.model.delete_one({'name': model_name})
    return res

def get_bot_all():
    return list(client.model.find({'is_activate': True}, {'_id': 0}))

def update_session_content(session_id, doc):
    session = client.session.find_one({'session_id': session_id})
    if session is None:
        client.session.insert_one({
            'session_id': session_id,
            'content': [doc]
        })
    else:
        session['content'].append(doc)
        client.session.update_one(
            {'session_id': session_id},
            {'$set': {'content': session['content']}}
        )

def update_session_by_regenerate(session_id, doc):
    content = client.session.find_one({'session_id': session_id})['content']
    content[-1] = doc
    client.aa_session.update_one(
        {'session_id': session_id},
        {'$set': {'content': content}}
    )

def update_session_choose(session_id, chosen_msg_index):
    content = client.session.find_one({'session_id': session_id})['content']
    content[-1]['choice'] = chosen_msg_index
    client.session.update_one(
        {'session_id': session_id},
        {'$set': {'content': content}}
    )

def get_session_rank_and_order(session_id):
    bot_list = get_bot_all()
    rank_dict = {bot['name']: 0 for bot in bot_list}
    bot_id_dict = {bot_list[i]['name']: i for i in range(len(bot_list))}

    bot_order_list = []
    session_content = client.session.find_one({'session_id': session_id})['content']
    for msg in session_content:
        # rank
        choice = msg['choice']
        bot_name = msg['bot'][choice]['name']
        rank_dict[bot_name] += 1

        # order
        bot_order = []
        for bot in msg['bot']:
            bot_order.append(bot_id_dict[bot['name']])
        bot_order_list.append(bot_order)
    
    rank_list = []
    for key, value in rank_dict.items():
        rank_list.append({
            'bot_name': key,
            'chosen_num': value
        })
    rank_list.sort(key=lambda k: (k.get('chosen_num', 0)), reverse=True)
    
    return rank_list, bot_order_list

def get_session_all():
    session_list = client.session.find({}, {'_id': 0})
    return list(session_list)