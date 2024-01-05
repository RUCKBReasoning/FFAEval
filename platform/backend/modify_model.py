import argparse
from mongodb import insert_model, update_model_state, delete_model

def add_model_action(args):
    res = insert_model(args.model_name, args.api_key, args.base_url)
    if res.inserted_id:
        print('add model success')
    else:
        print('add model fail')

def deactivate_model_action(args):
    res = update_model_state(args.model_name, False)
    if res.matched_count > 0:
        print('deactivate model success')
    else:
        print('deactivate model fail')

def activate_model_action(args):
    res = update_model_state(args.model_name, True)
    if res.matched_count > 0:
        print('activate model success')
    else:
        print('activate model fail')

def delete_model_action(args):
    res = delete_model(args.model_name)
    if res.deleted_count > 0:
        print('delete model success')
    else:
        print('delete model fail')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', required=True, type=str, help='add/deactivate/activate/delete')
    parser.add_argument('--model_name', required=True, type=str, help='name of model')
    parser.add_argument('--api_key', default="", type=str, help='api key of model')
    parser.add_argument('--base_url', default="", type=str, help='base url of model')
    args = parser.parse_args()

    if args.action == 'add':
        add_model_action(args)
    elif args.action == 'deactivate':
        deactivate_model_action(args)
    elif args.action == 'activate':
        activate_model_action(args)
    elif args.action == 'delete':
        delete_model_action(args)
    else:
        print('Action does not exist')
