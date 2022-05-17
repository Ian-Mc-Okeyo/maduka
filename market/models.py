from flask_login import UserMixin
from sqlalchemy import ForeignKey
from market import db
from market import bcrypt
from datetime import datetime

books_cart = db.Table('books_cart',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('book_id', db.Integer(), db.ForeignKey('book.code'))
    )

stationery_cart = db.Table('stationery_cart',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('stationery_id', db.Integer(), db.ForeignKey('stationery.code'))
    )

lab_cart = db.Table('lab_cart',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('lab_id', db.Integer(), db.ForeignKey('lab.code'))
    )

uniform_cart = db.Table('uniform_cart',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('uniform_id', db.Integer, db.ForeignKey('uniform.code'))
    )

product_cart = db.Table('product_cart',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('product_id', db.String(), db.ForeignKey('product.productCode'))
    )

orders = db.Table('orders_cart',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('order_id', db.String(), db.ForeignKey('order.code'))
    )

class User(db.Model, UserMixin): #UserMixin contains additional methods used  during logIn
    id = db.Column(db.Integer(), primary_key=True)
    userName = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(), nullable=False)
    password_hash = db.Column(db.String(length=60), nullable=False)
    phoneNo = db.Column(db.String(length=12), nullable=False)
    books_cart = db.relationship('Book', secondary=books_cart, backref="users_interested")
    stationery_cart = db.relationship('Stationery', secondary=stationery_cart, backref="users_interested")
    lab_cart = db.relationship('Lab', secondary=lab_cart, backref="users_interested")
    uniform_cart = db.relationship('Uniform', secondary=uniform_cart, backref="users_interested")
    products_cart = db.relationship('Product', secondary=product_cart, backref='users_interested')
    orders = db.relationship('Order', secondary=orders, backref="users_interested")
    shop_orders = db.relationship('Shop_order', backref="customers", lazy=True)

    @property #creating a new property
    def password(self):
        return self.password
    
    @password.setter #setting the new password property. This field is the one to be used in assigning the password_hash field
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password): #unhashing the passwords to be used during login
        return bcrypt.check_password_hash(self.password_hash, attempted_password)  #returns true or false
    
    def __repr__(self):
        return f"User('{self.id}', '{self.userName}', '{self.email}', '{self.phoneNo}', '{self.books_cart}')"

class Owner(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False, unique=True)
    shops = db.relationship('Shop', backref='owner', lazy=True)
    
#the seller's database and shops
class Shop(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    shopName = db.Column(db.String(), nullable=False, unique=True)
    owner_id = db.Column(db.Integer(), db.ForeignKey('owner.id'), nullable=False)
    category = db.Column(db.String(), nullable=False)
    paybill = db.Column(db.String())
    country = db.Column(db.String())
    town = db.Column(db.String())
    profilePic = db.Column(db.String())
    products = db.relationship('Product', backref='shop', lazy=True)
    orders = db.relationship('Shop_order', backref="shop", lazy=True)

class Product(db.Model):
    productCode = db.Column(db.String(), primary_key=True)
    shop_id = db.Column(db.Integer(), db.ForeignKey('shop.id'), nullable=False)
    title = db.Column(db.String(), nullable=False)
    price = db.Column(db.Float(), nullable=False)
    stock = db.Column(db.Integer(), nullable=False)
    displayPic = db.Column(db.String(), nullable=False)
    description = db.Column(db.String())
    pic1 = db.Column(db.String())
    pic2 = db.Column(db.String())
    pic3 = db.Column(db.String())
    pic4 = db.Column(db.String())
    orders = db.relationship('Shop_order', backref='product', lazy=True)

class Book(db.Model):
    code = db.Column(db.String(length=10), nullable=False, primary_key=True)
    title = db.Column(db.String(length=20), nullable=False)
    author=db.Column(db.String(), nullable=False)
    price = db.Column(db.Float(), nullable=False)
    numberOfItems=db.Column(db.Integer(), nullable=False)
    description = db.Column(db.String(), nullable=False)
    displayPic = db.Column(db.String())

    def __repr__(self):
       return f"User('{self.code}', '{self.title}', '{self.author}', '{self.price}', '{self.numberOfItems}')"

class Stationery(db.Model):
    code = db.Column(db.String(length=10), nullable=False, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    price = db.Column(db.Float(), nullable=False)
    numberOfItems=db.Column(db.Integer(), nullable=False)
    description = db.Column(db.String(), nullable=False)
    displayPic = db.Column(db.String())

    def __repr__(self):
       return f"User('{self.code}', '{self.title}', '{self.price}', '{self.numberOfItems}')"

class Lab(db.Model):
    code = db.Column(db.String(length=10), nullable=False, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    price = db.Column(db.Float(), nullable=False)
    numberOfItems=db.Column(db.Integer(), nullable=False)
    description = db.Column(db.String(), nullable=False)
    displayPic = db.Column(db.String())

    def __repr__(self):
       return f"User('{self.code}', '{self.title}', '{self.price}', '{self.numberOfItems}')"

class School(db.Model):
    name = db.Column(db.String(), primary_key=True, nullable=False)
    uniforms = db.relationship('Uniform', backref='school', lazy=True)

class Uniform(db.Model):
    code = db.Column(db.String(length=10), nullable=False, primary_key=True)
    price = db.Column(db.Float(), nullable=False)
    title = db.Column(db.String(), nullable=False)
    numberOfItems=db.Column(db.Integer(), nullable=False)
    size = db.Column(db.String(), nullable=False)
    gender = db.Column(db.String(), nullable=False)
    displayPic = db.Column(db.String())
    school_name = db.Column(db.String, db.ForeignKey('school.name'), nullable=False)

    def __repr__(self):
       return f"User('{self.code}', '{self.price}', '{self.title}', '{self.numberOfItems}')"

class Order(db.Model):
   code = db.Column(db.String(length=10), nullable=False, primary_key=True)
   product_code = db.Column(db.String(), nullable=False)
   time = db.Column(db.DateTime(), nullable=False, default=datetime.now)
   address = db.Column(db.String(), nullable=False)
   town=db.Column(db.String(), nullable=False)
   county=db.Column(db.String(), nullable=False)
   numberOfItems=db.Column(db.Integer(), nullable=False)

class Shop_order(db.Model):
    code = db.Column(db.String(length=10), nullable=False, primary_key=True)
    product_code = db.Column(db.String(), db.ForeignKey('product.productCode'), nullable=False)
    shop_id=db.Column(db.Integer(), db.ForeignKey('shop.id'), nullable=False)
    user_id=db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    time = db.Column(db.DateTime(), nullable=False, default=datetime.now)
    address = db.Column(db.String(), nullable=False)
    town=db.Column(db.String(), nullable=False)
    county=db.Column(db.String(), nullable=False)
    numberOfItems=db.Column(db.Integer(), nullable=False)