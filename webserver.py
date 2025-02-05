import uuid
import yaml

from flask import Flask, request, jsonify, abort, render_template

# initialize Flask server
app = Flask(__name__)

# Editor!
@app.after_request
def apply_cors_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


@app.route('/')
def index():
    with open('openapi3_0.yaml', 'r') as file:
        spec = yaml.safe_load(file)
    return render_template('index.html', spec=spec)


# define endpoint for getting and deleting existing todo lists
@app.route('/todo-list/<list_id>', methods=['GET', 'DELETE'])
def handle_list(list_id):
    # find todo list depending on given list id
    selected_list = None
    for l in todo_lists:
        if l['id'] == list_id:
            selected_list = l
            break
    # if the given list id is invalid, return status code 404
    if not selected_list:
        abort(404)
    if request.method == 'GET':
        # find all todo entries for the todo list with the given id
        print('Returning todo-list...')
        selected_list['items'] = []
        # add items to todo-list objecta and extract json data from json response
        selected_list['items'].extend([jsonify(i).json for i in items if i['list'] == list_id])
        return jsonify(selected_list)
    elif request.method == 'DELETE':
        # delete list with given id
        print('Deleting todo list...')
        todo_lists.remove(selected_list)
        return '', 200


# define endpoint for adding a new list
@app.route('/todo-list', methods=['POST'])
def add_new_list():
    # make JSON from POST data (even if content type is not set correctly)
    new_list = request.get_json(force=True)
    print('Got new list to be added: {}'.format(new_list))
    # create id for new list, save it and return the list with id
    new_list['id'] = uuid.uuid4()
    todo_lists.append(new_list)
    return jsonify(new_list), 200


# define endpoint for adding a new list
@app.route('/todo-list/<list_id>/item', methods=['POST'])
def add_new_item(list_id):
    selected_list = None
    for l in todo_lists:
        if l['id'] == list_id:
            selected_list = l
            break
    # if the given list id is invalid, return status code 404
    if not selected_list:
        abort(404)
    if not request.get_json['name']:
        abort(400)

    # make JSON from POST data (even if content type is not set correctly)
    new_item = request.get_json(force=True)
    print('Got new item to be added: {}'.format(new_item))
    # create id for new list, save it and return the list with id
    new_item['id'] = uuid.uuid4()
    new_item['list'] = list_id
    items.append(new_item)
    return jsonify(new_item), 200


# U Update todo-list item
@app.route('/todo-list/<list_id>/items/<item_id>', methods=['PUT', 'DELETE'])
def update_item(list_id, item_id):
    selected_list = None
    for l in todo_lists:
        if l['id'] == list_id:
            selected_list = l
            break

    selected_item = None
    for i in items:
        if i['id'] == item_id:
            selected_item = i
            break

    # make JSON from POST data (even if content type is not set correctly)
    updated_item = request.get_json(force=True)
    # if the given list id is invalid, return status code 404
    if not selected_list or not selected_item or selected_item['list'] != list_id:
        abort(404)

    if request.method == 'DELETE':
        items.remove(selected_item)
        return jsonify(selected_list)

    if request.method == 'PUT':
        if not updated_item['name']:
            abort(400)

        print('Got new data to update an item: {}'.format(updated_item))
        # create id for new list, save it and return the list with id
        selected_item = update_item
        return jsonify(selected_item), 200


# define endpoint for getting all lists
@app.route('/lists', methods=['GET'])
def get_all_lists():
    return jsonify(todo_lists)


if __name__ == '__main__':
    # start Flask server
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
