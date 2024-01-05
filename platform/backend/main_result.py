import random
from trueskill import Rating, rate, expose
from mongodb import get_session_all, get_bot_all


def get_match_score(match, bot_dict):
    match_score = [0 for _ in range(len(bot_dict))]
    for turn in match['content']:
        bot_responses = turn['bot']
        user_choice = turn['choice']
        chosen_bot = bot_responses[user_choice]['name']
        match_score[bot_dict[chosen_bot]] += 1
    return match_score


if __name__ == '__main__':    
    bot_list = get_bot_all()
    bot_dict = {bot_list[i]['name']: i for i in range(len(bot_list))}

    session_list = get_session_all()
    random.shuffle(session_list)

    rating = [[Rating()] for _ in range(len(bot_list))]
    for session in session_list:
        match_score = get_match_score(session, bot_dict)
        ranks = [e * -1 for e in match_score]
        rating = rate(rating, ranks=ranks)
    
    final_score = {bot_list[i]['name']: round(expose(rating[i][0]), 3) for i in range(len(bot_list))}
    print(final_score)
