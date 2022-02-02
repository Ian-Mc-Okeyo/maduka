from datetime import datetime
from re import search
import flask_login
from flask_bcrypt import Bcrypt, bcrypt
from flask_wtf import FlaskForm
from numpy import product
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import PasswordField, StringField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from flask import Flask, render_template, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_login import UserMixin
from sqlalchemy import true #for login

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///market.db'
db=SQLAlchemy(app)
app.config['SECRET_KEY']='405ccfeb09e3f35cdc0e3f1a'

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login_page"

@login_manager.user_loader#for the login manager to remember that the user was already logged in even after a refresh
def load_user(user_id):
    return User.query.get(int(user_id))

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

orders = db.Table('orders_cart',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('order_id', db.Integer(), db.ForeignKey('order.code'))
    )

class User(db.Model, UserMixin): #UserMixin contains additional methods used  during logIn
    id = db.Column(db.Integer(), primary_key=True)
    userName = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(), nullable=False)
    password_hash = db.Column(db.String(length=60), nullable=False)
    phoneNo = db.Column(db.String(length=12), nullable=False)
    books_cart = db.relationship('Book', secondary=books_cart, backref="users_interested")
    stationery_cart = db.relationship('Stationery', secondary=stationery_cart, backref="users_interested")
    lab_cart = db.relationship('Lab', secondary=lab_cart, backref="users_interested")
    uniform_cart = db.relationship('Uniform', secondary=uniform_cart, backref="users_interested")
    orders = db.relationship('Order', secondary=orders, backref="users_interested")

    @property #creating a new property
    def password(self):
        return self.password
    
    @password.setter #swetting the new password property. This field is the one to be used in assigning the password_hash field
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password): #unhashing the passwords to be used during login
        return bcrypt.check_password_hash(self.password_hash, attempted_password)  #returns true or false
    
    def __repr__(self):
        return f"User('{self.id}', '{self.userName}', '{self.email}', '{self.phoneNo}', '{self.books_cart}')"

class Book(db.Model):
    code = db.Column(db.String(length=10), nullable=False, primary_key=True)
    title = db.Column(db.String(length=20), nullable=False)
    author=db.Column(db.String(), nullable=False)
    price = db.Column(db.Float(), nullable=False)
    numberOfItems=db.Column(db.Integer(), nullable=False)
    description = db.Column(db.String(), nullable=False)

    def __repr__(self):
       return f"User('{self.code}', '{self.title}', '{self.author}', '{self.price}', '{self.numberOfItems}')"

class Stationery(db.Model):
    code = db.Column(db.String(length=10), nullable=False, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    price = db.Column(db.Float(), nullable=False)
    numberOfItems=db.Column(db.Integer(), nullable=False)
    description = db.Column(db.String(), nullable=False)

    def __repr__(self):
       return f"User('{self.code}', '{self.title}', '{self.price}', '{self.numberOfItems}')"

class Lab(db.Model):
    code = db.Column(db.String(length=10), nullable=False, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    price = db.Column(db.Float(), nullable=False)
    numberOfItems=db.Column(db.Integer(), nullable=False)
    description = db.Column(db.String(), nullable=False)

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
    school_name = db.Column(db.String, db.ForeignKey('school.name'), nullable=False)

    def __repr__(self):
       return f"User('{self.code}', '{self.price}', '{self.title}', '{self.numberOfItems}')"

class Order(db.Model):
   code = db.Column(db.String(length=10), nullable=False, primary_key=True)
   product_code = db.Column(db.String(), nullable=False)
   time = db.Column(db.DateTime(), nullable=False, default=datetime.now)
   address = db.Column(db.String(), nullable=False)

#forms
class LoginForm(FlaskForm):#login form
    userName = StringField(label='User Name', validators=[DataRequired()])
    email = StringField(label='Email', validators=[Email()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField(label='Login')

class RegisterForm(FlaskForm):
    #validations
    #is_user_valid = False

    def validate_userName(self, userName):
        user = User.query.filter_by(userName=userName.data).first()
        if user:
            raise ValidationError('The user name already exists')
        
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
             raise ValidationError('The email address already exists. Please use another valid email')
    
    def validate_phoneNo(self, phoneNo):
        user=User.query.filter_by(phoneNo=phoneNo.data).first()
        if user:
             raise ValidationError('This phone Number already exists. Please use another phone Number')
    
    def validate_confirmPassword(self, confirmPassword):
        if not self.password.data == self.confirmPassword.data:
             raise ValidationError('This field must match the password field')
    
    userName = StringField(label='User Name', validators=[Length(min=3, max=30), DataRequired()])
    email = StringField(label='Email', validators=[Email(), DataRequired()])
    phoneNo = StringField(label='Phone Number', validators=[Length(min=10, max=13), DataRequired()])
    password = PasswordField(label="Password", validators=[Length(min=8), DataRequired()])
    confirmPassword = PasswordField(label="Confirm password", validators=[EqualTo('password'), DataRequired()])
    submit = SubmitField(label='Create Account')

class SearchForm(FlaskForm):
    productName = StringField(validators=[DataRequired()])
    submit = SubmitField(label='Search')

class AddToCartForm(FlaskForm):
    submit1 = SubmitField(label='ADD TO CART')

class RemoveFromCartForm(FlaskForm):
    submit1 = SubmitField(label='REMOVE FROM CART')

class OrderForm(FlaskForm):
    submit2 = SubmitField(label='ORDER')


@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user=User(userName=form.userName.data, email=form.email.data,
                    password=form.password.data, phoneNo=form.phoneNo.data )
        db.session.add(new_user)
        db.session.commit()
        flash('Account successfully created', category='success')
        return redirect(url_for('market_page'))
    
    else:
        print(form.errors)
        
    return render_template('register.html', form=form, errors=form.errors)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form=LoginForm()
    if form.validate_on_submit():
        attempting_user = User.query.filter_by(userName=form.userName.data, email=form.email.data).first()
        if attempting_user and attempting_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempting_user)
            flash('Successful LogIn', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Invalid details', category='error')
    
    return render_template('login.html', form=form)

@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    x = Book.query.all()
    print(x[0].code)
    book = Book.query.filter_by(code='123456789012').first()
    products = {'books':[], 'stationery':[], 'lab':[], 'uniforms':[]}

    books = Book.query.all()
    for book in books:
        products['books'].append(book)
    
    stationeries=Stationery.query.all()
    for stationery in stationeries:
        products['stationery'].append(stationery)

    labs = Lab.query.all()
    for lab in labs:
        products['lab'].append(lab)
    
    uniforms=Uniform.query.all()
    for uniform in uniforms:
        products['uniforms'].append(uniform)
    image_file = f'static/{book.code}.png'
    searchForm=SearchForm()
    return render_template('market_index.html', searchForm=searchForm, products=products, image_file=image_file)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("Successful log out!", category='success')
    return redirect(url_for("home_page"))

@app.route('/CCC<product_code>/<cart_code>', methods=['GET', 'POST'])
@login_required
def product_page(product_code, cart_code):
    product=''
    if product_code[0]=='B' or product_code[0]=='1':
        product=Book.query.filter_by(code=product_code).first()
    if product_code[0]=='S':
        product=Stationery.query.filter_by(code=product_code).first()
    if product_code[0]=='L':
        product=Lab.query.filter_by(code=product_code).first()
    if product_code[0]=='U':
        product=Uniform.query.filter_by(code=product_code).first()

    if cart_code!='none':
        if current_user in product.users_interested:
            if product.code[0]=='U':
                current_user.uniform_cart.remove(product)
            if product.code[0]=='S':
                current_user.stationery_cart.remove(product)
            if product.code[0]=='L':
                current_user.lab_cart.remove(product)
            if product.code[0]=='B' or product.code[0]=='1':
                current_user.books_cart.remove(product)
            flash(f'{product.title} has been removed from your cart', category='success')
        else:
            if product.code[0]=='U':
                current_user.uniform_cart.append(product)
            if product.code[0]=='S':
                current_user.stationery_cart.append(product)
            if product.code[0]=='L':
                current_user.lab_cart.append(product)
            if product.code[0]=='B' or product.code[0]=='1':
                current_user.books_cart.append(product)        
            flash(f'{product.title} has been added to your cart', category='success')
        db.session.commit()
        return redirect(url_for("product_page", product_code=product_code, cart_code='none'))
    searchForm = SearchForm()
    return render_template('product.html', searchForm=searchForm, product=product)

@app.route('/market <product_category>')
@login_required
def all_page(product_category):
    products=''
    if product_category=='books':
        products=Book.query.all()
    elif product_category=='uniform':
        products=Uniform.query.all()
    elif product_category=='lab':
        products=Lab.query.all()
    else:
        products=Stationery.query.all()
    
    searchForm=SearchForm()
    return render_template('all_products.html', products=products, searchForm=searchForm)

@app.route('/cart <cart_code>')
@login_required
def cart_page(cart_code):
    searchForm=SearchForm()
    print(cart_code)
    #book = Book.query.filter_by(code='123456789012').first()
    products_cart = {'books':[], 'stationery':[], 'lab':[], 'uniform':[]}
    for book in current_user.books_cart:
        products_cart['books'].append(book)
    for stationery in current_user.stationery_cart:
        products_cart['stationery'].append(stationery)
    for lab in current_user.lab_cart:
        products_cart['lab'].append(lab)
    for uniform in current_user.uniform_cart:
        products_cart['uniform'].append(uniform)

    cartForm = RemoveFromCartForm()
    orderForm = OrderForm()

    if cart_code!='none':
        print(cart_code)
        print('A cart button was clicked')
        if cart_code[0]=='U':
            product=Uniform.query.filter_by(code=cart_code).first()
            current_user.uniform_cart.remove(product)
        if cart_code[0]=='S':
            product=Stationery.query.filter_by(code=cart_code).first()
            current_user.stationery_cart.remove(product)
        if cart_code[0]=='L':
            product=Lab.query.filter_by(code=cart_code).first()
            current_user.lab_cart.remove(product)
        if cart_code[0]=='B' or cart_code[0]=='1':
            product=Book.query.filter_by(code=cart_code).first()
            print(current_user.books_cart)
            current_user.books_cart.remove(product)
        db.session.commit()
        #flash(f'{product.title} has been removed from your cart', category='success')
        return redirect(url_for("cart_page", cart_code='none'))
    else:
        print('The cart code was not clicked')
    if orderForm.submit2.data and orderForm.validate_on_submit:
        print()
        print('An order button was clicked')
    
    return render_template('cart.html', searchForm=searchForm, products_cart=products_cart, cartForm=cartForm, orderForm=orderForm)

@app.route('/Myorders')
def order_page():
    pass
@app.route('/favicon.ico')
def favicon():
    return 'dummy', 200