from requests import session
from sqlalchemy import null
from market import app
import secrets
from PIL import Image
import os
from market import login_manager
from flask import request
from werkzeug.utils import secure_filename
from market.models import *
from random import randint
from flask import render_template, redirect, flash, url_for
from flask_login import current_user, login_user, logout_user, login_required
from market.forms import *
import pathlib

@login_manager.user_loader#for the login manager to remember that the user was already logged in even after a refresh
def load_user(user_id):
    return User.query.get(int(user_id))


#sellers functions
#function to get the specific product type
def getProductType(productCode):
    product=''
    if productCode[0]=='B' or productCode[0]=='1':
        product=Book.query.filter_by(code=productCode).first()
    elif productCode[0]=='S':
        product=Stationery.query.filter_by(code=productCode).first()
    elif productCode[0]=='L':
         product=Lab.query.filter_by(code=productCode).first()
    elif productCode[0]=='U':
        product=Uniform.query.filter_by(code=productCode).first()
    return product

@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user=User(userName=form.userName.data, email=form.email.data,
                    password=form.password.data, phoneNo=form.phoneNo.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Account successfully created', category='success')
        login_user(new_user)
        return redirect(url_for('market_page'))
    
    else:
        print(form.errors)
        
    return render_template('register.html', form=form, errors=form.errors)

def save_profile_pic(form_picture):
    random_hex = secrets.token_hex(10)
    _, file_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + file_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size=(170, 170)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_fn

def save_product_pic(form_picture):
    random_hex = secrets.token_hex(10)
    _, file_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + file_ext
    picture_path = os.path.join(app.root_path, 'static/products', picture_fn)

    output_size=(250, 250)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_fn

@app.route('/createShop', methods=['POST', 'GET'])
def create_shop():
    form = CreateShop()
    if form.validate_on_submit():
        #checking if the password is correct
        attempting_user = User.query.filter_by(userName=form.userName.data).first()
        if attempting_user.check_password_correction(attempted_password=form.password.data):
            check_owner = Owner.query.filter_by(user_id=attempting_user.id).first()
            if not check_owner:
                new_owner= Owner(user_id=attempting_user.id)
                db.session.add(new_owner)
                db.session.commit()
            
            #loading the owner
            owner = Owner.query.filter_by(user_id=attempting_user.id).first()
            
            if form.uploadPic.data:
                picture_fn = save_profile_pic(form.uploadPic.data)
                new_shop = Shop(shopName=form.shopName.data, owner_id=owner.id, 
                                category=form.category.data, country=form.country.data, town=form.town.data,
                                profilePic=picture_fn
                            )
                db.session.add(new_shop)
                db.session.commit()
                login_user(attempting_user)
                return redirect(url_for('manage_home', shop_id = new_shop.id))
        else:
            print('Wrong password')
            flash('Invalid User password', category='error')

    return render_template('createShop.html', form=form, errors=form.errors)

@app.route('/openShop', methods=['POST', 'GET'])
def open_shop():
    form = OpenShop()
    if form.validate_on_submit():
        check_user = User.query.filter_by(userName=form.ownerName.data).first()
        if check_user:
            check_owner=Owner.query.filter_by(user_id=check_user.id).first()
            if check_owner:
                check_shop = Shop.query.filter_by(shopName=form.shopName.data, owner_id=check_owner.id).first()
                if check_shop:
                    if check_user.check_password_correction(attempted_password=form.password.data):
                        login_user(check_user)
                        flash('Successful Login', category='success')
                        return redirect(url_for('manage_home', shop_id=check_shop.id))
                    else:
                        flash('Invalid Password', category='error')
                else:
                    flash('Invalid shop name', category='error')
            else:
                flash('The account is not registered as a Shop owner', category='error')
        else:
            flash('Invalid User Name', category='error')

    return render_template('openShop.html', form=form, errors=form.errors)

@app.route('/manageShop/<shop_id>', methods=['POST', 'GET'])
@login_required
def manage_home(shop_id):
    owner = Owner.query.filter_by(user_id=current_user.id).first()
    current_shop = Shop.query.filter_by(owner_id=owner.id, id=shop_id).first()
    if not current_shop:#to redirect users who have no shops to the create shop url
        return redirect(url_for('open_shop'))
    
    print(current_shop.products)
    products = current_shop.products
    profile_pic_fn=url_for('static', filename='profile_pics/'+current_shop.profilePic)
    return render_template('manageShop/manage_home.html', current_shop=current_shop, profile_pic=profile_pic_fn, products=products)

@app.route('/manageShop/<shop_id>/addProduct', methods=['POST', 'GET'])
def add_product(shop_id):
    print('Test id')
    form = addProductForm()
    owner = Owner.query.filter_by(user_id=current_user.id).first()
    current_shop = Shop.query.filter_by(owner_id=owner.id, id=shop_id).first()
    if not current_shop:#to redirect users who have no shops to the create shop url
        return redirect(url_for('open_shop'))
    
    if form.validate_on_submit():
        display_pic = save_product_pic(form.displayPic.data)
        new_product=Product(productCode=secrets.token_hex(10), shop_id=current_shop.id, title=form.title.data,
                             price=form.price.data, stock=form.stock.data, displayPic=display_pic, description=form.description.data)
        
        print(type(form.extraPics.data))
        if len(form.extraPics.data)>0:
            if len(form.extraPics.data)==1:
                new_product.pic1=save_product_pic(form.extraPics.data[0])
            elif len(form.extraPics.data)==2:
                new_product.pic1=save_product_pic(form.extraPics.data[0])
                new_product.pic2=save_product_pic(form.extraPics.data[1])
            elif len(form.extraPics.data)==3:
                new_product.pic1=save_product_pic(form.extraPics.data[0])
                new_product.pic2=save_product_pic(form.extraPics.data[1])
                new_product.pic3=save_product_pic(form.extraPics.data[2])
            elif len(form.extraPics.data)==4:
                new_product.pic1=save_product_pic(form.extraPics.data[0])
                new_product.pic2=save_product_pic(form.extraPics.data[1])
                new_product.pic3=save_product_pic(form.extraPics.data[2])
                new_product.pic4=save_product_pic(form.extraPics.data[3])
        
        db.session.add(new_product)
        db.session.commit()
        flash('Product Successfully added', category='success')
        return redirect(url_for('add_product', shop_id=current_shop.id))
    else:
        print(form.errors)
        
    profile_pic_fn=url_for('static', filename='profile_pics/'+current_shop.profilePic)
    return render_template('manageShop/addProduct.html', form=form, current_shop=current_shop, profile_pic=profile_pic_fn, errors=form.errors)

@app.route('/manageShop/<shop_id>/changeDetails', methods=['POST', 'GET'])
@login_required
def change_shop_details(shop_id):
    detailsForm = ShopDetailsForm()
    changePasswordForm=ChangePasswordForm()
    owner = Owner.query.filter_by(user_id=current_user.id).first()
    current_shop = Shop.query.filter_by(owner_id=owner.id, id=shop_id).first()
    if not current_shop:#to redirect users who have no shops to the create shop url
        return redirect(url_for('open_shop'))
    
         
    if detailsForm.submit1.data and detailsForm.validate_on_submit():
        if current_shop.shopName != detailsForm.shopName.data:
            check_shop = Shop.query.filter_by(shopName=detailsForm.shopName.data).first()
            if check_shop:
                flash('Shop Name already exists', category='error')
                return redirect(url_for('change_shop_details', shop_id=shop_id))
                
        current_user.userName = detailsForm.userName.data
        current_user.email = detailsForm.email.data
        current_user.phoneNo = detailsForm.phoneNo.data
        current_shop.shopName = detailsForm.shopName.data
        current_shop.paybill = detailsForm.paybill.data
        current_shop.towm = detailsForm.town.data
        current_shop.country = detailsForm.country.data
        current_shop.category = detailsForm.category.data

        if detailsForm.displayPic.data:
            os.unlink(os.path.join(app.root_path, 'static/profile_pics/'+current_shop.profilePic))#deleting the previous dp
            current_shop.profilePic = save_profile_pic(detailsForm.displayPic.data)
        
        db.session.commit()

        flash('Details successfully updated', category='success')
        return redirect(url_for('change_shop_details', shop_id=shop_id))

    if changePasswordForm.submit2.data and changePasswordForm.validate_on_submit():
        current_user.password=changePasswordForm.newPassword.data
        db.session.commit()
        flash('Your password has been successfully updated', category='success')
        return redirect(url_for('change_shop_details', shop_id=shop_id))

    
    profile_pic_fn=url_for('static', filename='profile_pics/'+current_shop.profilePic)
    return render_template('manageShop/change_details.html', current_shop=current_shop,detailsForm=detailsForm, changePasswordForm=changePasswordForm,
        profile_pic=profile_pic_fn, details_errors = detailsForm.errors,
        password_errors = changePasswordForm.errors)


@app.route('/manageShop/<shop_id>/<product_code>', methods=['GET', 'POST'])
@login_required
def specific_product_page(shop_id, product_code):
    owner = Owner.query.filter_by(user_id=current_user.id).first()
    current_shop = Shop.query.filter_by(owner_id=owner.id, id=shop_id).first()
    if not current_shop:#to redirect users who have no shops to the create shop url
        return redirect(url_for('open_shop'))
    
    product = Product.query.filter_by(productCode=product_code).first()
    if product:
        print('Product found')
    else:
        print('Not found')

    profile_pic_fn=url_for('static', filename='profile_pics/'+current_shop.profilePic)
    return render_template('manageShop/seller_product.html', product=product, profile_pic=profile_pic_fn, 
                    current_shop=current_shop)


@app.route('/manageShop/<shop_id>/update_product/<product_code>', methods=['POST', 'GET'])
@login_required
def update_product_details(shop_id, product_code):
    owner = Owner.query.filter_by(user_id=current_user.id).first()
    current_shop = Shop.query.filter_by(owner_id=owner.id, id=shop_id).first()
    if not current_shop:#to redirect users who have no shops to the create shop url
        return redirect(url_for('open_shop'))
    
    form = UpdateProductDetails()
    errors = form.errors
    product = Product.query.filter_by(productCode=product_code).first()

    
    if form.validate_on_submit():
        product.title = form.title.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.description = form.description.data

        if form.displayPic.data:
            print('there is dp')
            os.unlink(os.path.join(app.root_path, 'static/products/'+product.displayPic))#deleting the previous dp
            product.displayPic = save_product_pic(form.displayPic.data)
        
        if len(form.extraPics.data)>0 and form.extraPics.data[0].filename!='':
            # #deleting the pictures
            if product.pic1:
                os.unlink(os.path.join(app.root_path, 'static/products/'+product.pic1))
            
            if product.pic2:
                os.unlink(os.path.join(app.root_path, 'static/products/'+product.pic2))
            
            if product.pic3:
                os.unlink(os.path.join(app.root_path, 'static/products/'+product.pic3))
            
            if product.pic4:
                os.unlink(os.path.join(app.root_path, 'static/products/'+product.pic4))
            
            #updating the pictures
            if len(form.extraPics.data)>0:
                if len(form.extraPics.data)==1:
                    product.pic1=save_product_pic(form.extraPics.data[0])
                    product.pic2=None
                    product.pic3=None
                    product.pic4=None
                elif len(form.extraPics.data)==2:
                    product.pic1=save_product_pic(form.extraPics.data[0])
                    product.pic2=save_product_pic(form.extraPics.data[1])
                    product.pic3=None
                    product.pic4=None
                elif len(form.extraPics.data)==3:
                    product.pic1=save_product_pic(form.extraPics.data[0])
                    product.pic2=save_product_pic(form.extraPics.data[1])
                    product.pic3=save_product_pic(form.extraPics.data[2])
                    product.pic4=None
                elif len(form.extraPics.data)==4:
                    product.pic1=save_product_pic(form.extraPics.data[0])
                    product.pic2=save_product_pic(form.extraPics.data[1])
                    product.pic3=save_product_pic(form.extraPics.data[2])
                    product.pic4=save_product_pic(form.extraPics.data[3])

        db.session.commit()
        flash('Product details successfully updated', category='success')
        return redirect(url_for('update_product_details', product_code=product.productCode, shop_id=shop_id))


    profile_pic_fn=url_for('static', filename='profile_pics/'+current_shop.profilePic)
    return render_template('manageShop/product_update.html', product=product, profile_pic=profile_pic_fn, form=form, errors=errors,
                    current_shop= current_shop, description=product.description)

@app.route('/manageShop/<shop_id>/delete_product/<product_code>', methods=['POST', 'GET'])
@login_required
def delete_product(shop_id, product_code):
    owner = Owner.query.filter_by(user_id=current_user.id).first()
    current_shop = Shop.query.filter_by(owner_id=owner.id, id=shop_id).first()
    if not current_shop:#to redirect users who have no shops to the create shop url
        return redirect(url_for('open_shop'))
    
    product = Product.query.filter_by(productCode=product_code).first()
    #product.delete()
    try:
        db.session.delete(product)
        db.session.commit()
        flash('product successfully deleted', category='success')
    except:
        print('Could not delete product')
    
    return redirect(url_for('manage_home', shop_id=shop_id))


# beginning of buyers functions
@app.route('/market/searchshop', methods=['POST', 'GET'])
@login_required
def searchShop():
    shops = Shop.query.all()
    print(type(shops))
    print(shops[0].products)
    return render_template('visit_shop/search_shop.html', shops=shops)

@app.route('/market/visitShop/<shop_id>', methods=['POST', 'GET'])
@login_required
def visit_shop(shop_id):
    shop = Shop.query.filter_by(id=shop_id).first()
    
    profile_pic_fn=url_for('static', filename='profile_pics/'+shop.profilePic)
    return render_template('visit_shop/visit_shop_home.html', shop=shop, profile_pic=profile_pic_fn)

@app.route('/market/visitShop/<shop_id>/makeOrder/<product_code>', methods=['POST', 'GET'])
@login_required
def make_shop_order(shop_id, product_code):
    shop = Shop.query.filter_by(id=shop_id).first()
    order_form = MakeShopOrderForm()
    product = Product.query.filter_by(productCode=product_code).first()

    if order_form.validate_on_submit():
        new_order = Shop_order(code=secrets.token_hex(10), product_code=product_code, shop_id=shop_id, user_id=current_user.id,
                            address=order_form.address.data, town=order_form.town.data, county=order_form.county.data, numberOfItems=order_form.numberOfItems.data)
        product.stock=product.stock-order_form.numberOfItems.data
        db.session.add(new_order)
        db.session.commit()
        flash('Order made successfully', category='success')
        return redirect(url_for('make_shop_order', shop_id=shop_id, product_code=product_code))

    profile_pic_fn=url_for('static', filename='profile_pics/'+shop.profilePic)
    product_dp = url_for('static', filename='products/'+product.displayPic)
    return render_template('visit_shop/make_order.html', shop=shop, profile_pic=profile_pic_fn, product_dp=product_dp, 
                    errors=order_form.errors, form=order_form, product=product)


@app.route('/market/visitShop/viewProduct/<shop_id>/<product_code>')
@login_required
def view_product_page(shop_id, product_code):
    shop = Shop.query.filter_by(id=shop_id).first()
    product = Product.query.filter_by(productCode=product_code).first()

    profile_pic_fn=url_for('static', filename='profile_pics/'+shop.profilePic)
    return render_template('visit_shop/view_product.html', shop=shop, profile_pic=profile_pic_fn, product=product)

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
    #image_file = f'static/{book.code}.png'
    searchForm=SearchForm()
    return render_template('market_index.html', searchForm=searchForm, products=products)

@app.route('/market/<product_code>/<cart_code>', methods=['GET', 'POST'])
@login_required
def product_page(product_code, cart_code):
    print(product_code)
    product=getProductType(product_code)

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
        return redirect(url_for('product_page', product_code=product_code, cart_code='none'))
        #return redirect(url_for("product_page", product_code=product_code, cart_code='none'))
    searchForm = SearchForm()
    orderForm = OrderForm()

    if orderForm.submit2.data and orderForm.validate_on_submit:
        code = randint(1000000000, 9999999999)#generating a random number for the order code
        newOrder = Order(code=code, product_code=product_code,
                            address=orderForm.address.data, town=orderForm.town.data,
                            county=orderForm.county.data, numberOfItems=orderForm.numberOfItems.data)
        current_user.orders.append(newOrder)
        product.numberOfItems-=orderForm.numberOfItems.data
        db.session.commit()
        flash('Order has been made. Check your order details in the orders page', category='success')
        print('order made')

    return render_template('product.html', searchForm=searchForm, product=product, orderForm=orderForm)


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
    return render_template('all_products.html', products=products, searchForm=searchForm, product_category=product_category)

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
    
    #checking if all the carts category are empty
    is_products_cart_empty=0
    for key in products_cart:
        if len(products_cart[key])>0:
            is_products_cart_empty+=1 #if any cart is has a product, then we update is_product_cart_empty variable
            break

    if is_products_cart_empty==0:
        products_cart='empty'

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

@app.route('/Myorders/<order_code_to_cancel>/<product_code_to_cancel>', methods=['GET', 'POST'])
@login_required
def order_page(order_code_to_cancel, product_code_to_cancel):
    products=[]
    orders=[]
    for order in current_user.orders:
        product=getProductType(order.product_code)        
        products.append(product)
        orders.append(order)
    
    #order_cancellation
    if order_code_to_cancel !='none':
        product_to_remove=getProductType(product_code_to_cancel)
        order_to_remove = Order.query.filter_by(code=order_code_to_cancel).first()
        current_user.orders.remove(order_to_remove)
        product_to_remove.numberOfItems+=order_to_remove.numberOfItems#adding back the stock that was added
        db.session.commit()
        return redirect(url_for('order_page', order_code_to_cancel='none', product_code_to_cancel='none'))
    
    #changing the order details
    orderForm=OrderForm()

    if orderForm.submit2.data and orderForm.validate_on_submit:
        order_code_to_change=orderForm.submit2._value()[13:]
        order_to_change=Order.query.filter_by(code=order_code_to_change).first()
        product_ordered = getProductType(order_to_change.product_code)

        #updates
        product_ordered.numberOfItems+=order_to_change.numberOfItems#updating the number of items of the specific product
        product_ordered.numberOfItems-=orderForm.numberOfItems.data
        order_to_change.address, order_to_change.county=orderForm.address.data, orderForm.county.data
        order_to_change.town, order_to_change.numberOfItems=orderForm.town.data, orderForm.numberOfItems.data
        db.session.commit()
        
        return redirect(url_for('order_page', order_code_to_cancel='none', product_code_to_cancel='none'))
        
    return render_template('orders.html', products=products, orders=orders, orderForm=orderForm)

@app.route('/myDetails', methods=['POST', 'GET'])
@login_required
def details_page():
    detailsForm = DetailsForm()
    changePasswordForm = ChangePasswordForm()

    if detailsForm.submit1.data and detailsForm.validate_on_submit:
        print('Passes through this')
        userByName = User.query.filter_by(userName=detailsForm.userName.data).first()
        userByEmail = User.query.filter_by(email=detailsForm.email.data).first()
        userByPhone = User.query.filter_by(phoneNo=detailsForm.phoneNo.data).first()
        if userByName and current_user.userName != detailsForm.userName.data:
            flash("A user already exists with given User name", category="error")
        if userByEmail and current_user.email != detailsForm.email.data:
            flash("A user already exists with given Email", category="error")
        if userByPhone and current_user.phoneNo != detailsForm.phoneNo.data:
            flash("A user already exists with given phone number", category="error")
        else:
            if current_user.userName != detailsForm.userName.data or current_user.email != detailsForm.email.data or current_user.phoneNo != detailsForm.phoneNo.data:
                current_user.userName=detailsForm.userName.data
                current_user.email=detailsForm.email.data
                current_user.phoneNo=detailsForm.phoneNo.data
                db.session.commit()
                flash("Your details have been successfully updated", category="success")
        redirect(url_for('details_page'))

    errors = {'oldPassword':[], 'newPassword':[], 'confirmPassword':[]}
    if changePasswordForm.validate_on_submit and changePasswordForm.submit2.data:
        if not current_user.check_password_correction(attempted_password=changePasswordForm.oldPassword.data):
            errors['oldPassword'].append('Wrong Password')
        if changePasswordForm.confirmPassword.data!=changePasswordForm.newPassword.data:
            errors['confirmPassword'].append('This field must match the new Password')
        else:
            current_user.password=changePasswordForm.newPassword.data
            db.session.commit()
            flash('Your password has been successfully updated', category='success')
        redirect (url_for('details_page'))

    return render_template('details.html', detailsForm=detailsForm, changePasswordForm=changePasswordForm, errors=errors)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("Successful log out!", category='success')
    return redirect(url_for("home_page"))

@app.route('/favicon.ico')
def favicon():
    return 'dummy', 200