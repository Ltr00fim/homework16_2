from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from data import *


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    age = db.Column(db.Integer)
    email = db.Column(db.String, unique=True)
    role = db.Column(db.String)
    phone = db.Column(db.String)

    def __repr__(self):
        return f'<users {self.id}>'


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String)

    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def __repr__(self):
        return f'<order {self.id}>'


class Offer(db.Model):
    __tablename__ = 'offers'

    id = db.Column(db.Integer, primary_key=True)

    order_id = (db.Integer, db.ForeignKey('orders.id'))
    executor_id = (db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<offer {self.id}>'

    def serialize(self):
        return {'id': self.id, 'order_id': self.order_id, 'executor_id': self.executor_id}


with app.app_context():
    db.create_all()

    for user_info in users:
        user = User(
            id=user_info['id'],
            first_name=user_info['first_name'],
            last_name=user_info['last_name'],
            age=user_info['age'],
            email=user_info['email'],
            role=user_info['role'],
            phone=user_info['phone']
        )
        db.session.add(user)

    for order_info in orders:
        order = Order(
            id=order_info['id'],
            name=order_info['name'],
            description=order_info['description'],
            start_date=datetime.strptime(order_info['start_date'], '%m/%d/%Y'),
            end_date=datetime.strptime(order_info['end_date'], '%m/%d/%Y'),
            address=order_info['address'],
            customer_id=order_info['customer_id'],
            executor_id=order_info['executor_id']
        )
        db.session.add(order)

    for offer_info in offers:
        offer = Offer(
            id=offer_info['id'],
            order_id=offer_info['order_id'],
            executor_id=offer_info['executor_id'],
        )
        db.session.add(offer)

    db.session.commit()


""" ВЬЮШКИ """


@app.route('/')
@app.route('/users/', methods=['GET', 'POST'])
def users_page():
    if request.method == 'GET':
        result = []

        users_class = User.query.all()

        for user_class in users_class:
            result.append(
                {'id': user_class.id,
                 'first_name': user_class.first_name,
                 'last_name': user_class.last_name,
                 'age': user_class.age,
                 'email': user_class.email,
                 'role': user_class.role,
                 'phone': user_class.phone})

        return jsonify(result)
    if request.method == 'POST':
        new_user = request.json()
        new_user = User(
            id=new_user['id'],
            first_name=new_user['first_name'],
            last_name=new_user['last_name'],
            age=new_user['age'],
            email=new_user['email'],
            role=new_user['role'],
            phone=new_user['phone']
        )
        db.session.add(new_user)
        db.session.comit()
        return '', 201


@app.route('/users/<pk>', methods=['GET', 'DELETE', 'PUT'])
def user_page(pk):
    if request.method == 'GET':
        result = []

        user_class = User.query.get(int(pk))

        if user_class is None:
            return f'Нет пользователя с id {pk}'

        result.append(
            {'id': user_class.id,
             'first_name': user_class.first_name,
             'last_name': user_class.last_name,
             'age': user_class.age,
             'email': user_class.email,
             'role': user_class.role,
             'phone': user_class.phone}
        )

        return jsonify(result)

    if request.method == 'DELETE':
        user_delete = User.query.get(int(pk))

        if user_delete is None:
            return f'Нет пользователя с id {pk}'

        db.session.delete(user_delete)
        db.session.commit()

        return '', 202

    if request.method == 'PUT':
        new_user = request.json()

        user_update = User.query.get(int(pk))

        if user_update is None:
            return f'Нет пользователя с id {pk}'

        user_update.id = new_user['id'],
        user_update.first_name = new_user['first_name'],
        user_update.last_name = new_user['last_name'],
        user_update.age = new_user['age'],
        user_update.email = new_user['email'],
        user_update.role = new_user['role'],
        user_update.phone = new_user['phone']

        db.session.add(user_update)
        db.session.comit()
        return '', 202


@app.route('/orders/', methods=['GET', 'POST'])
def orders_page():
    if request.method == 'GET':
        result = []

        orders_class = Order.query.all()

        for order_class in orders_class:
            result.append(
                {'id': order_class.id,
                 'name': order_class.name,
                 'description': order_class.description,
                 'start_date': order_class.start_date,
                 'end_date': order_class.end_date,
                 'address': order_class.address,
                 'customer_id': order_class.customer_id,
                 'executor_id': order_class.executor_id}
            )

        return jsonify(result)
    if request.method == 'POST':
        order_new = request.json()
        new_order = Order(
            id=order_new['id'],
            name=order_new['name'],
            description=order_new['description'],
            start_date=datetime.strptime(order_new['start_date'], '%m/%d/%Y'),
            end_date=datetime.strptime(order_new['end_date'], '%m/%d/%Y'),
            address=order_new['address'],
            customer_id=order_new['customer_id'],
            executor_id=order_new['executor_id']
        )
        db.session.add(new_order)
        db.session.comit()
        return '', 201


@app.route('/orders/<pk>', methods=['GET', 'DELETE', 'PUT'])
def order_page(pk):
    if request.method == 'GET':
        result = []

        order_class = Order.query.get(int(pk))

        if order_class is None:
            return f'Нет заказа с id {pk}'

        result.append(
            {'id': order_class.id,
             'name': order_class.name,
             'description': order_class.description,
             'start_date': order_class.start_date,
             'end_date': order_class.end_date,
             'address': order_class.address,
             'customer_id': order_class.customer_id,
             'executor_id': order_class.executor_id}
        )
        return jsonify(result)

    if request.method == 'DELETE':
        order_delete = Order.query.get(int(pk))

        if order_delete is None:
            return f'Нет заказа с id {pk}'

        db.session.delete(order_delete)
        db.session.commit()

        return '', 202

    if request.method == 'PUT':
        new_order = request.json()

        order_update = User.query.get(int(pk))

        if order_update is None:
            return f'Нет заказа с id {pk}'

        order_update.id = new_order['id'],
        order_update.name = new_order['name'],
        order_update.description = new_order['description'],
        order_update.start_date = datetime.strptime(new_order['start_date'], '%m/%d/%Y'),
        order_update.end_date = datetime.strptime(new_order['end_date'], '%m/%d/%Y'),
        order_update.address = new_order['address'],
        order_update.customer_id = new_order['customer_id'],
        order_update.executor_id = new_order['executor_id']

        db.session.add(order_update)
        db.session.comit()
        return '', 202


@app.route('/offers/', methods=['GET', 'POST'])
def offers_page():
    if request.method == 'GET':
        result = []

        offers_class = Offer.query.all()
        for offer_class in offers_class:
            result.append(offer_class.serialize())
        return jsonify(result)
    if request.method == 'POST':
        offer_new = request.json()
        new_offer = Offer(
            id=offer_new['id'],
            order_id=offer_new['order_id'],
            executor_id=offer_new['executor_id'],
        )
        db.session.add(new_offer)
        db.session.comit()
        return '', 201


@app.route('/offers/<pk>', methods=['GET', 'DELETE', 'PUT'])
def offer(pk):
    if request.method == 'GET':
        result = []

        offer_class = Offer.query.get(int(pk))

        if offer_class is None:
            return f'Нет заказа с id {pk}'

        result.append(offer_class.serialize())
        return jsonify(result)
    if request.method == 'DELETE':
        offer_delete = Offer.query.get(int(pk))

        if offer_delete is None:
            return f'Нет заказа с id {pk}'

        db.session.delete(offer_delete)
        db.session.commit()

        return '', 202
    if request.method == 'PUT':
        new_offer = request.json()

        offer_update = User.query.get(int(pk))

        if offer_update is None:
            return f'Нет заказа с id {pk}'

        offer_update.id = new_offer['id'],
        offer_update.name = new_offer['name'],
        offer_update.description = new_offer['description'],
        offer_update.start_date = datetime.strptime(new_offer['start_date'], '%m/%d/%Y'),
        offer_update.end_date = datetime.strptime(new_offer['end_date'], '%m/%d/%Y'),
        offer_update.address = new_offer['address'],
        offer_update.customer_id = new_offer['customer_id'],
        offer_update.executor_id = new_offer['executor_id']

        db.session.add(offer_update)
        db.session.comit()
        return '', 202


if __name__ == '__main__':
    app.run(debug=True)
