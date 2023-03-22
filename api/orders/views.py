from flask_restx import Namespace, Resource, fields
from ..models.orders import Order
from ..models.users import User
from ..utils import db
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity

order_namespace = Namespace('Order', description='name space for Order')


order_model = order_namespace.model(
	'Order', {
		'flavour': fields.String(description= 'Pizza Flavour', required=True), 
		'quantity': fields.Integer(description='Number of Pizzas'),
		'size': fields.String(description= 'Pizza Size', required=True, enum = ['SMALL', 'MEDIUM', 'LARGE', 'EXTRA_LARGE']),
		'order_status': fields.String(description='Current Order Status', required=True, enum = ['PENDING', 'IN_TRANSIT', 'DELIVERED'])
	}
)

order_status_model = order_namespace.model(
    'OrderStatus', {
        'order_status': fields.String(description='Current Order Status', required=True,
            enum = ['PENDING', 'IN_TRANSIT', 'DELIVERED'])
    }
)


@order_namespace.route('/orders')
class OrderGetCreate(Resource):

	
	@order_namespace.marshal_with(order_model)
	@order_namespace.doc(
		description="Get all orders"
	)
	@jwt_required()
	def get(self):
		"""
			Get all orders
		
		"""
		orders = Order.query.all()
		return orders, HTTPStatus.OK


	@order_namespace.expect(order_model)
	@order_namespace.marshal_with(order_model)
	@order_namespace.doc(
		description="Place an order"
	)
	@jwt_required()
	def post(self):
		"""
			place an order
		"""
		username = get_jwt_identity()
		current_user = User.query.filter_by(username=username).first()

		data = order_namespace.payload

		new_order = Order(
			size = data['size'],
			quantity = data['quantity'],
			flavour = data['flavour']
		)

		new_order.user = current_user

		new_order.save()

		return new_order, HTTPStatus.CREATED

@order_namespace.route("/order/<int:order_id>")
class GetUpdateDelete(Resource):
	
	@order_namespace.marshal_with(order_model)
	@order_namespace.doc(
		description="Retrieve an order by id", params = {
		"order_id": "An id for the order"
		}
	)
	@jwt_required()
	def get(self, order_id):
		"""
			Retrieve an order by id
		"""
		order = Order.get_by_id(order_id)

		return order, HTTPStatus.OK


	@order_namespace.expect(order_model)
	@order_namespace.marshal_with(order_model)
	@order_namespace.doc(
		description="Update an order by id", params = {
		"order_id": "An id for the order"}
	)
	@jwt_required()
	def put(self, order_id):

		"""
			Update an order by id
		"""
		order_to_update = Order.get_by_id(order_id)
		data = order_namespace.payload

		order_to_update.flavour = data["flavour"]
		order_to_update.quantity = data["quantity"]
		order_to_update.size = data["size"]

		order_to_update.update()

		return order_to_update, HTTPStatus.OK


	@order_namespace.expect(order_model)
	@order_namespace.marshal_with(order_model)
	@order_namespace.doc(
		description="Delete an order by id"
	)
	@jwt_required()
	def delete(self, order_id):
		"""
			delete an order by ID
		"""
		order_to_delete = Order.get_by_id(order_id)

		order_to_delete.delete()

		return {"message": "Order Deleted Successfully"}, HTTPStatus.OK


@order_namespace.route("/user/<int:user_id>/order/<int:order_id>")
class GetSpecificOrderByUser(Resource):

	@order_namespace.marshal_with(order_model)
	@order_namespace.doc(
		description="Get specific order by id"
	)
	@jwt_required()
	def get(self, user_id, order_id):
		"""
			get a specific order by a user id and order id
		"""
		user = User.get_by_id(user_id)
		order = Order.query.filter_by(id=order_id).filter_by(user=user).first()

		return order, HTTPStatus.OK


@order_namespace.route("/user/<int:user_id>/orders")
class UserOrders(Resource):

	@order_namespace.marshal_with(order_model)
	@order_namespace.doc(
		description="Get all orders by a user using user id"
	)
	@jwt_required()
	def get(self, user_id):
		"""
				Get all orders by a user
		"""
		user = User.get_by_id(user_id)

		orders = user.orders
		
		return orders, HTTPStatus.OK


@order_namespace.route("/order/status/<int:order_id>")
class UpdateOrderStatus(Resource):
	
	@order_namespace.expect(order_status_model)
	@order_namespace.marshal_with(order_model)
	@order_namespace.doc(
		description="Update an order status"
	)
	@jwt_required()
	def patch(self, order_id):
		"""
			Update an order's status
		"""
		data = order_namespace.payload

		order_to_update = Order.get_by_id(order_id)

		order_to_update.order_status = data["order_status"]

		db.session.commit()

		return order_to_update, HTTPStatus.OK
	




