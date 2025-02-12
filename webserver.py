import uuid
import yaml
from flask import Flask, request, jsonify, abort, render_template
from flask_sqlalchemy import SQLAlchemy

# Flask & SQLAlchemy Setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Database Models
class TodoList(db.Model):
    __tablename__ = 'todo_list'
    id = db.Column(db.String(36), primary_key=True)  # UUID as string (36 characters)
    name = db.Column(db.String(80), nullable=False)
    # When a todo list is deleted, all its items are removed too.
    items = db.relationship('Item', backref='todo_list', cascade='all, delete-orphan', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'items': [item.to_dict() for item in self.items]
        }


class Item(db.Model):
    __tablename__ = 'item'
    id = db.Column(db.String(36), primary_key=True)  # UUID as string (36 characters)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), default='')
    list_id = db.Column(db.String(36), db.ForeignKey('todo_list.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'list': self.list_id
        }


# CORS Header (for Swagger Editor preview)
@app.after_request
def apply_cors_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


# Routes

# Render the OpenAPI specification page
@app.route('/')
def index():
    with open('openapi3_0.yaml', 'r') as file:
        spec = yaml.safe_load(file)
    return render_template('index.html', spec=spec)


# GET and DELETE a specific todo-list
@app.route('/todo-list/<list_id>', methods=['GET', 'DELETE'])
def handle_list(list_id):
    todo_list = TodoList.query.get(list_id)
    if not todo_list:
        abort(404)
    if request.method == 'GET':
        return jsonify(todo_list.to_dict())
    elif request.method == 'DELETE':
        db.session.delete(todo_list)
        db.session.commit()
        return '', 200


# POST a new todo-list
@app.route('/todo-list', methods=['POST'])
def add_new_list():
    new_list_data = request.get_json(force=True)
    if 'name' not in new_list_data:
        abort(400)
    new_list = TodoList(id=str(uuid.uuid4()), name=new_list_data['name'])
    db.session.add(new_list)
    db.session.commit()
    return jsonify(new_list.to_dict()), 200


# POST a new item to a specific todo-list
@app.route('/todo-list/<list_id>/item', methods=['POST'])
def add_new_item(list_id):
    todo_list = TodoList.query.get(list_id)
    if not todo_list:
        abort(404)
    data = request.get_json(force=True)
    if 'name' not in data:
        abort(400)
    new_item = Item(
        id=str(uuid.uuid4()),
        name=data['name'],
        description=data.get('description', ''),
        list_id=list_id
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify(new_item.to_dict()), 200


# PUT or DELETE an item in a specific todo-list
@app.route('/todo-list/<list_id>/items/<item_id>', methods=['PUT', 'DELETE'])
def update_item(list_id, item_id):
    todo_list = TodoList.query.get(list_id)
    if not todo_list:
        abort(404)
    item = Item.query.filter_by(id=item_id, list_id=list_id).first()
    if not item:
        abort(404)
    if request.method == 'DELETE':
        db.session.delete(item)
        db.session.commit()
        return jsonify(todo_list.to_dict())
    elif request.method == 'PUT':
        data = request.get_json(force=True)
        if 'name' not in data:
            abort(400)
        item.name = data['name']
        item.description = data.get('description', item.description)
        db.session.commit()
        return jsonify(item.to_dict()), 200


# GET all todo-lists (with items embedded)
@app.route('/lists', methods=['GET'])
def get_all_lists():
    all_lists = TodoList.query.all()
    return jsonify([lst.to_dict() for lst in all_lists])


# database with the provided data
def init_db():
    print("Initializing database and creating tables...")
    with app.app_context():
        db.drop_all()  # Remove old tables if they exist
        db.create_all()  # Create new tables

        if TodoList.query.first() is None:
            print("Inserting sample data...")
            # Predefined IDs for sample lists
            list1_id = '1318d3d1-d979-47e1-a225-dab1751dbe75'
            list2_id = '3062dc25-6b80-4315-bb1d-a7c86b014c65'
            list3_id = '44b02e00-03bc-451d-8d01-0c67ea866fee'
            list1 = TodoList(id=list1_id, name='EinkaufsListe')
            list2 = TodoList(id=list2_id, name='Arbeit')
            list3 = TodoList(id=list3_id, name='Privat')
            db.session.add_all([list1, list2, list3])

            # Sample items for the lists
            item1 = Item(id=str(uuid.uuid4()), name='Milch', description='', list_id=list1_id)
            item2 = Item(id=str(uuid.uuid4()), name='Arbeitsblätter ausdrucken', description='', list_id=list2_id)
            item3 = Item(id=str(uuid.uuid4()), name='Kinokarten kaufen', description='', list_id=list3_id)
            item4 = Item(id=str(uuid.uuid4()), name='Eier', description='', list_id=list1_id)
            db.session.add_all([item1, item2, item3, item4])
            db.session.commit()
            print("Sample data inserted.")


# main
if __name__ == '__main__':
    init_db()  # Ensure database is initialized
    app.run(host='0.0.0.0', port=5000, use_reloader=False)
