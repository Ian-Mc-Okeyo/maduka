from random import choices
from tkinter.tix import Select
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms.fields.numeric import IntegerField, FloatField
from wtforms.fields.simple import PasswordField, StringField, SubmitField, FileField, SearchField, TextAreaField, MultipleFileField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from flask_login import current_user
from market.models import User, Owner, Shop
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
    
    userName = StringField(label='User Name', validators=[Length(min=3, max=30), DataRequired()])
    email = StringField(label='Email', validators=[Email(), DataRequired()])
    phoneNo = StringField(label='Phone Number', validators=[Length(min=10, max=13), DataRequired()])
    password = PasswordField(label="Password", validators=[Length(min=8), DataRequired()])
    confirmPassword = PasswordField(label="Confirm password", validators=[EqualTo('password'), DataRequired()])
    submit = SubmitField(label='Create Account')

class CreateShop(FlaskForm):
    #validations
    #is_user_valid = False

    def validate_userName(self, userName):
        user = User.query.filter_by(userName=userName.data).first()
        if not user:
            raise ValidationError('Wrong User Name')
        
    def validate_shopName(self, shopName):
        user = Shop.query.filter_by(shopName=shopName.data).first()
        if user:
             raise ValidationError('The shop Name already exists. Kindly use another name.')
    
    
    userName = StringField(label='User Name', validators=[Length(min=3, max=30), DataRequired()])
    shopName = StringField(label='Shop Name', validators=[Length(min=3, max=30), DataRequired()])
    country = StringField(label='Country Location', validators=[Length(min=3, max=50), DataRequired()])
    town = StringField(label='Town Location', validators=[Length(min=3, max=50), DataRequired()])
    category = StringField(label='Products Category', validators=[Length(min=3, max=50), DataRequired()])
    password = PasswordField(label="Owner's Password", validators=[Length(min=8), DataRequired()])
    uploadPic = FileField(label='Upload a profile picture', validators=[DataRequired(), FileAllowed(['jpg', 'png', 'jpeg'])])

    submit = SubmitField(label='Create Shop')

class OpenShop(FlaskForm):
    ownerName = StringField(label='Your User Name', validators=[Length(min=3, max=30), DataRequired()])
    shopName = StringField(label='Shop Name', validators=[Length(min=3, max=30), DataRequired()])
    password = PasswordField(label="Password", validators=[Length(min=8), DataRequired()])

    submit = SubmitField(label='Create Shop')

class addProductForm(FlaskForm):
    title = StringField(label='Title', validators=[DataRequired()])
    price = FloatField(label='Price', validators=[DataRequired()])
    stock = IntegerField(label='Stock', validators=[DataRequired()])
    description = TextAreaField(label='Description')
    displayPic = FileField(label='Upload a display Picture', validators=[DataRequired(), FileAllowed(['jpg', 'png', 'jpeg'])])
    extraPics = MultipleFileField(label='Upload a display Picture', validators=[DataRequired(), FileAllowed(['jpg', 'png'])])

    submit = SubmitField(label='Submit')

class SearchForm(FlaskForm):
    productName = SearchField(validators=[DataRequired()])
    submit = SubmitField(label='Search')

class AddToCartForm(FlaskForm):
    submit1 = SubmitField(label='ADD TO CART')

class RemoveFromCartForm(FlaskForm):
    submit1 = SubmitField(label='REMOVE FROM CART')

class OrderForm(FlaskForm):
    address = StringField(label='Address', validators=[DataRequired()])
    town = StringField(label='Town', validators=[DataRequired()])
    county = StringField(label='County', validators=[DataRequired()])
    numberOfItems = IntegerField(label='Number of Items', validators=[DataRequired()])
    submit2 = SubmitField(label='ORDER')

class DetailsForm(FlaskForm):
    userName = StringField(label='User Name:', validators=[DataRequired()])
    email = StringField(label='Email', validators=[Email()])
    phoneNo = StringField(label='Phone No:', validators=[DataRequired()])
    submit1 = SubmitField(label='SAVE CHANGES')

class ShopDetailsForm(FlaskForm):
    def validate_userName(self, userName):
        if current_user.userName != userName.data:
            check_user = User.query.filter_by(userName=userName.data).first()
            if check_user:
                raise ValidationError('The User name already exists')

    def validate_shopName(self, shopName):
        current_shop = Shop.query.filter_by(ownerName=current_user.userName).first()
        if current_shop.shopName != shopName.data:
            check_shop = Shop.query.filter_by(shopName=shopName.data).first()
            if check_shop:
                raise ValidationError('The shop name already exist')

    def validate_email(self, email):
        if current_user.email != email.data:
            check_user = User.query.filter_by(email=email.data).first()
            if check_user:
                raise ValidationError('The User email already exists')

    def validate_phoneNo(self, phoneNo):
        if current_user.phoneNo != phoneNo.data:
            check_user = User.query.filter_by(phoneNo=phoneNo.data).first()
            if check_user:
                raise ValidationError('The phone Number already exists')

    userName = StringField(label='User Name:', validators=[Length(min=3, max=50), DataRequired()])
    shopName = StringField(label='Shop Name', validators=[Length(min=3, max=50), DataRequired()])
    email = StringField(label='Email', validators=[Length(min=3, max=60), Email()])
    phoneNo = StringField(label='Phone No', validators=[Length(min=10, max=13), DataRequired()])
    paybill = StringField(label='Paybill', validators=[DataRequired()])
    town = StringField(label='Town', validators=[DataRequired()])
    country = StringField(label='Country', validators=[DataRequired()])
    category = StringField(label='Category', validators=[Length(min=3, max=50), DataRequired()])
    displayPic = FileField(label='Change display Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit1 = SubmitField(label='SAVE CHANGES')

class ChangePasswordForm(FlaskForm):
    #validationschanchanchan
    def validate_oldPassword(self, oldPassword):
        if not current_user.check_password_correction(attempted_password=oldPassword.data):
            raise ValidationError('Wrong Password')
    
    def validate_confirmPassword(self, confirmPassword):
        if not self.newPassword.data == confirmPassword.data:
            raise ValidationError('This field must match the new password')

    oldPassword = PasswordField(label='Current password', validators=[DataRequired()])
    newPassword = PasswordField(label='New Password', validators=[Length(min=8), DataRequired()])
    confirmPassword = PasswordField(label='Confirm password', validators=[DataRequired(), EqualTo(newPassword)])
    submit2=SubmitField(label='SUBMIT')