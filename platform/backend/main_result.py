import json
import random
from trueskill import Rating, rate, expose


def get_match_score(match, bot_dict):
    match_score = [0 for _ in range(len(bot_dict))]
    for turn in match['content']:
        bot_responses = turn['bot']
        user_choice = turn['choice']
        chosen_bot = bot_responses[user_choice]['name']
        match_score[bot_dict[chosen_bot]] += 1
    return match_score


if __name__ == '__main__':
    data_type = 'en'

    if data_type == 'en':
        bot_name = ['BART', 'DialoGPT', 'BlenderBot-90m', 'BlenderBot-3b', 'PLATO-XL']
    elif data_type == 'zh':
        bot_name = ['CDial-GPT', 'EVA', 'PLATO-2', 'XDAI', 'GLM-Finetune']
    else:
        print('Wrong data type!')
        exit(-1)

    bot_dict = {bot_name[i]: i for i in range(len(bot_name))}

    with open(f'data/{data_type}.jsonl') as fp:
        lines = fp.readlines()
    random.shuffle(lines)

    rating = [[Rating()] for _ in range(5)]
    for line in lines:
        data = json.loads(line)
        match_score = get_match_score(data, bot_dict)
        ranks = [e * -1 for e in match_score]
        rating = rate(rating, ranks=ranks)
    
    final_score = {bot_name[i]: round(expose(rating[i][0]), 3) for i in range(len(bot_name))}
    print(final_score)
