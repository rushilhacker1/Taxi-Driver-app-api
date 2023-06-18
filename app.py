from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_bcrypt import Bcrypt

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Replace with your own secret key

db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)


# Customer Model
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(1000))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(1100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    balance = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Customer(id={self.id}, image_url={self.image_url}, name='{self.name}', email={self.email}, password={self.password}, rating={self.rating}, balance={self.balance}, location='{self.location}', destination='{self.destination}')"


# Driver Model
class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(1000))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(1100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Driver(id={self.id}, image_url={self.image_url}, name='{self.name}', email={self.email}, password={self.password}, rating={self.rating}, status='{self.status}', location='{self.location}', destination='{self.destination}')"

# Customer Schema
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True


# Driver Schema
class DriverSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Driver
        load_instance = True


customer_schema = CustomerSchema()
driver_schema = DriverSchema()
customers_schema = CustomerSchema(many=True)
drivers_schema = DriverSchema(many=True)


# Authentication Resource
class AuthResource(Resource):
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')

        # Authenticate the user (you can use your own authentication logic here)
        customer = Customer.query.filter_by(email=username).first()
        driver = Driver.query.filter_by(email=username).first()

        if not customer and not driver:
            abort(401, message="Invalid credentials")

        if customer and bcrypt.check_password_hash(customer.password, password):
            # Generate access token
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token)

        if driver and bcrypt.check_password_hash(driver.password, password):
            # Generate access token
            access_token = create_access_token(identity=username)
            return jsonify(access_token=access_token)

        abort(401, message="Invalid credentials")


# Customer Resource
class CustomerResource(Resource):
    @jwt_required()
    def get(self, customer_id):
        customer = Customer.query.get(customer_id)
        if not customer:
            abort(404, message="Customer not found")
        return customer_schema.dump(customer)

    def put(self, customer_id):
        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str, help="Name of the customer is required", required=True)
        parser.add_argument("rating", type=int, help="Rating of the customer is required", required=True)
        parser.add_argument("balance", type=int, help="Balance of the customer is required", required=True)
        parser.add_argument("location", type=str, help="Location of the customer is required", required=True)
        parser.add_argument("destination", type=str, help="Destination of the customer is required", required=True)
        parser.add_argument("email", type=str, help="Email of the customer is required", required=True)
        parser.add_argument("password", type=str, help="Password of the customer is required", required=True)
        args = parser.parse_args()

        customer = Customer.query.get(customer_id)
        if customer:
            abort(409, message="Customer ID already exists")

        hashed_password = bcrypt.generate_password_hash(args['password']).decode('utf-8')

        new_customer = Customer(
            id=customer_id,
            name=args['name'],
            email=args['email'],
            password=hashed_password,
            rating=args['rating'],
            balance=args['balance'],
            location=args['location'],
            destination=args['destination']
        )

        db.session.add(new_customer)
        db.session.commit()
        return customer_schema.dump(new_customer), 201

    @jwt_required()
    def patch(self, customer_id):
        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str, help="Name of the customer")
        parser.add_argument("rating", type=int, help="Rating of the customer")
        parser.add_argument("balance", type=int, help="Balance of the customer")
        parser.add_argument("location", type=str, help="Location of the customer")
        parser.add_argument("destination", type=str, help="Destination of the customer")
        parser.add_argument("email", type=str, help="Email of the customer")
        parser.add_argument("password", type=str, help="Password of the customer")
        args = parser.parse_args()

        customer = Customer.query.get(customer_id)
        if not customer:
            abort(404, message="Customer not found")

        if args['name']:
            customer.name = args['name']
        if args['rating']:
            customer.rating = args['rating']
        if args['balance']:
            customer.balance = args['balance']
        if args['location']:
            customer.location = args['location']
        if args['destination']:
            customer.destination = args['destination']
        if args['email']:
            customer.email = args['email']
        if args['password']:
            hashed_password = bcrypt.generate_password_hash(args['password']).decode('utf-8')
            customer.password = hashed_password

        db.session.commit()
        return customer_schema.dump(customer)

    @jwt_required()
    def delete(self, customer_id):
        customer = Customer.query.get(customer_id)
        if not customer:
            abort(404, message="Customer not found")

        db.session.delete(customer)
        db.session.commit()
        return '', 204


# Driver Resource
class DriverResource(Resource):
    @jwt_required()
    def get(self, driver_id):
        driver = Driver.query.get(driver_id)
        if not driver:
            abort(404, message="Driver not found")
        return driver_schema.dump(driver)

    @jwt_required()
    def put(self, driver_id):
        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str, help="Name of the driver is required")
        parser.add_argument("image_url", type=str, help="Image URL of the driver")
        parser.add_argument("email", type=str, help="Email of the driver")
        parser.add_argument("password", type=str, help="Password of the driver")
        parser.add_argument("rating", type=int, help="Rating of the driver")
        parser.add_argument("status", type=str, help="Status of the driver")
        parser.add_argument("location", type=str, help="Location of the driver")
        parser.add_argument("destination", type=str, help="Destination of the driver")

        args = parser.parse_args()

        driver = Driver.query.get(driver_id)
        if driver:
            abort(409, message="Driver ID already exists")

        hashed_password = bcrypt.generate_password_hash(args['password']).decode('utf-8')

        new_driver = Driver(
            id=driver_id,
            name=args['name'],
            email=args['email'],
            password=hashed_password,
            rating=args['rating'],
            status=args['status'],
            location=args['location'],
            destination=args['destination']
        )

        db.session.add(new_driver)
        db.session.commit()
        return driver_schema.dump(new_driver), 201

    @jwt_required()
    def patch(self, driver_id):
        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str, help="Name of the driver is required")
        parser.add_argument("image_url", type=str, help="Image URL of the driver")
        parser.add_argument("email", type=str, help="Email of the driver")
        parser.add_argument("password", type=str, help="Password of the driver")
        parser.add_argument("rating", type=int, help="Rating of the driver")
        parser.add_argument("status", type=str, help="Status of the driver")
        parser.add_argument("location", type=str, help="Location of the driver")
        parser.add_argument("destination", type=str, help="Destination of the driver")

        args = parser.parse_args()

        driver = Driver.query.get(driver_id)
        if not driver:
            abort(404, message="Driver not found")

        if args['name']:
            driver.name = args['name']
        if args['image_url']:
            driver.image_url = args['image_url']
        if args['email']:
            driver.email = args['email']
        if args['password']:
            hashed_password = bcrypt.generate_password_hash(args['password']).decode('utf-8')
            driver.password = hashed_password
        if args['rating']:
            driver.rating = args['rating']
        if args['status']:
            driver.status = args['status']
        if args['location']:
            driver.location = args['location']
        if args['destination']:
            driver.destination = args['destination']

        db.session.commit()
        return driver_schema.dump(driver)

    @jwt_required()
    def delete(self, driver_id):
        driver = Driver.query.get(driver_id)
        if not driver:
            abort(404, message="Driver not found")

        db.session.delete(driver)
        db.session.commit()
        return '', 204


# Customer List Resource
class CustomerListResource(Resource):
    @jwt_required()
    def get(self):
        customers = Customer.query.all()
        return customers_schema.dump(customers)

    @jwt_required()
    def delete(self):
        Customer.query.delete()
        db.session.commit()
        return '', 204


# Driver List Resource
class DriverListResource(Resource):
    @jwt_required()
    def get(self):
        drivers = Driver.query.all()
        return drivers_schema.dump(drivers)

    @jwt_required()
    def delete(self):
        Driver.query.delete()
        db.session.commit()
        return '', 204


api.add_resource(AuthResource, '/auth')
api.add_resource(CustomerResource, '/customers/<int:customer_id>')
api.add_resource(DriverResource, '/drivers/<int:driver_id>')
api.add_resource(CustomerListResource, '/customers')
api.add_resource(DriverListResource, '/drivers')


if __name__ == "__main__":
    app.run(debug=True)
