from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, logout_user, login_manager, LoginManager
from flask_security import current_user, login_required
from flask_mail import Mail, Message
from cryptography.fernet import Fernet
import re

# Regexes to verify proper aadhaar card nums, phone numbers
phone = re.compile(r'^([6-9])([0-9]{9})$')
aadhar = re.compile(r'^\d{12}')
emailReg = re.compile(
    r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
onlyChar = re.compile(r'[A-Za-z]+')

# MY db connection
local_server = True
app = Flask(__name__)
app.secret_key = b''                    #enter secrect key
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = ''            #enter your mail id
app.config['MAIL_PASSWORD'] = ''            #enter password for the mail id
app.config['MAIL_USE_TLS'] = True

# this is for getting unique user access
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# to send users forgot pw email
mail = Mail(app)

# To encrpyt and decrypt password
fernet = Fernet(app.secret_key)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# app.config['SQLALCHEMY_DATABASE_URL']='mysql://username:password@localhost/database_table_name'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/farmers'      #enter password for sql file
db = SQLAlchemy(app)

# here we will create db models that is tables


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    type = db.Column(db.String(5), nullable=False)
    password = db.Column(db.String(500), nullable=False)


class Register(db.Model):
    __tablename__ = 'register'
    rid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    farmername = db.Column(db.String(50), unique=True, nullable=False)
    adharnumber = db.Column(db.String(20), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(50), nullable=False)
    phonenumber = db.Column(db.String(12), unique=True, nullable=False)
    address = db.Column(db.String(50), nullable=False)
    id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Farming(db.Model):
    __tablename__ = 'farming'
    fid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    farmingtype = db.Column(db.String(200), unique=True, nullable=False)


class FarmingTypes(db.Model):
    __tablename__ = 'farmingtypes'
    dummyid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    rid = db.Column(db.Integer, db.ForeignKey('register.rid'), nullable=False)
    fid = db.Column(db.Integer, db.ForeignKey('farming.fid'), nullable=False)


class Addagroproducts(db.Model):
    __tablename__ = 'addagroproducts'
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    pid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    productname = db.Column(db.String(100), nullable=False)
    productdesc = db.Column(db.String(300), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    rid = db.Column(db.Integer, db.ForeignKey('register.rid'), nullable=False)
    fid = db.Column(db.Integer, db.ForeignKey('farming.fid'), nullable=False)


class Trig(db.Model):
    __tablename__ = 'trig'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    action = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.String(100), nullable=False)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/farmerdetails')
@login_required
def farmerdetails():
    query1 = db.engine.execute(
        f"SELECT r.*,GROUP_CONCAT(f.farmingtype) AS fts FROM ((register as r INNER JOIN user as u ON u.id = r.id) INNER JOIN farmingtypes as ft ON ft.rid = r.rid) INNER JOIN farming f ON f.fid = ft.fid where r.id = {current_user.id} GROUP BY r.rid;")
    return render_template('farmerdetails.html', query1=query1)


@app.route('/agroproducts')
def agroproducts():
    query = db.engine.execute(
        f"SELECT ag.*, farmingtype FROM ((user as u INNER JOIN register as r ON u.id = r.id) INNER JOIN addagroproducts as ag ON ag.rid = r.rid) INNER JOIN farming as f ON f.fid = ag.fid WHERE u.id != {current_user.id}")
    return render_template('agroproducts.html', query=query, mine=False)


@app.route('/myagroproducts')
def myagroproducts():
    query = db.engine.execute(
        f"SELECT ag.*, farmingtype FROM ((user as u INNER JOIN register as r ON u.id = r.id) INNER JOIN addagroproducts as ag ON ag.rid = r.rid) INNER JOIN farming as f ON f.fid = ag.fid WHERE u.id = {current_user.id}")
    return render_template('agroproducts.html', query=query, mine=True)


@app.route('/addagroproduct/<string:rid>', methods=['POST', 'GET'])
@login_required
def addagroproduct(rid):
    farmer = Register.query.filter_by(rid=rid).first()
    query = db.engine.execute(
        f"SELECT farmingtype FROM farmingtypes as ft, register r, farming f where r.rid = {rid} and ft.fid = f.fid and r.rid = ft.rid"
    )
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        productname = request.form.get('productname')
        productdesc = request.form.get('productdesc')
        price = request.form.get('price')
        type = request.form.get('farmingtypes')
        fid = list(db.engine.execute(
            f'SELECT fid FROM `farming` where farmingtype = \'{type}\''))[0].fid
        products = Addagroproducts(username=username, email=email,
                                   productname=productname, productdesc=productdesc, price=price, rid=rid, fid=fid)
        db.session.add(products)
        db.session.commit()
        flash(f"Product {productname} Added", "success")
        return render_template('addagroproducts.html', query=query, farmer=farmer, rid=rid)
    return render_template('addagroproducts.html', query=query, farmer=farmer, rid=rid)


@app.route('/triggers')
@login_required
def triggers():
    if current_user.type.lower() != 'admin':
        flash(f"You do not have permission to view this page", 'warning')
        return redirect('/')
    query = db.engine.execute(
        f"SELECT `action`, `timestamp` FROM `trig` ORDER BY `timestamp` desc")
    return render_template('triggers.html', query=query)


@app.route('/addfarming', methods=['POST', 'GET'])
@login_required
def addfarming():
    if current_user.is_authenticated and current_user.type.lower() != 'admin':
        flash(f"You do not have permission to view this page", 'warning')
        return redirect('/')
    if request.method == "POST":
        farmingtype = request.form.get('farming')
        query = Farming.query.filter_by(farmingtype=farmingtype).first()
        if query:
            flash("Farming Type Already Exists", "warning")
            return redirect('/addfarming')
        mo1 = onlyChar.match(farmingtype)
        if not mo1 or mo1.group() != farmingtype:
            flash("Enter valid username", 'danger')
            return redirect(url_for('addfarming'))
        dep = Farming(farmingtype=farmingtype)
        db.session.add(dep)
        db.session.commit()
        flash(f"Farming type: {farmingtype} successfully added", "success")
        return render_template('farming.html')
    return render_template('farming.html')


@app.route("/delete/<string:rid>")
@login_required
def delete(rid):
    fname = Register.query.filter(rid == rid).first().farmername
    db.engine.execute(f"DELETE FROM `register` WHERE `register`.`rid`={rid}")
    db.session.commit()
    flash(f"Farmer {fname} Deleted Successful", "danger")
    return redirect(url_for('farmerdetails', uid=current_user.id))


@app.route("/edit/<string:rid>", methods=['POST', 'GET'])
@login_required
def edit(rid):
    farming = db.engine.execute("SELECT * FROM `farming`")
    ftypes = db.engine.execute(
        f"SELECT farmingtype FROM ((register AS r INNER JOIN farmingtypes AS ft ON r.rid = ft.rid) INNER JOIN farming f ON ft.fid = f.fid) WHERE r.rid = {rid};")
    farmingtypes = [ftype.farmingtype for ftype in ftypes]
    posts = Register.query.filter_by(rid=rid).first()
    if request.method == "POST":
        farmername = request.form.get('farmername')
        user = Register.query.filter_by(farmername=farmername).first()
        if user and user.farmername != farmername:
            flash(f'Farmer name {farmername} already taken', 'warning')
            return redirect(f'edit/{rid}')
        mo1 = onlyChar.match(farmername)
        if not mo1 or mo1.group() != farmername:
            flash("Enter valid farmer name", 'danger')
            return redirect(url_for('edit', rid=rid))
        adharnumber = request.form.get('adharnumber')
        user = Register.query.filter_by(adharnumber=adharnumber).first()
        if user and user.adharnumber != adharnumber:
            flash(f'Aadhaar number {adharnumber} already present', 'warning')
            return redirect(f'edit/{rid}')
        mo1 = aadhar.match(adharnumber)
        if not mo1 or mo1.group() != adharnumber:
            flash("Enter valid 12 digit aadhaar number", 'danger')
            return redirect(url_for(f'edit', rid=rid))
        age = request.form.get('age')
        gender = request.form.get('gender')
        phonenumber = request.form.get('phonenumber')
        mo2 = phone.match(phonenumber)
        if not mo2 or ''.join(mo2.groups()) != phonenumber:
            flash("Enter valid 10 digit phone number", 'danger')
            return redirect(url_for('edit', rid=rid))
        address = request.form.get('address')
        farmingtypes = request.form.getlist('farmingtypes')
        db.engine.execute(
            f"UPDATE `register` SET `farmername`='{farmername}',`adharnumber`='{adharnumber}',`age`='{age}',`gender`='{gender}',`phonenumber`='{phonenumber}',`address`='{address}' WHERE `rid` = {rid}"
        )
        db.session.commit()
        db.engine.execute(
            f"DELETE FROM `farmingtypes` where rid = {rid}"
        )
        rid = Register.query.filter_by(farmername=farmername).first().rid
        for farmingtype in farmingtypes:
            fid = Farming.query.filter_by(farmingtype=farmingtype).first().fid
            db.session.add(FarmingTypes(rid=rid, fid=fid))
            db.session.commit()
        flash(f"Update successful", 'success')
        return redirect(f'/farmerdetails')

    return render_template('edit.html', posts=posts, farming=farming, farmingtypes=farmingtypes)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        type = 'user'
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exists", "warning")
            return render_template('signup.html')
        user = User.query.filter_by(username=username).first()
        if user:
            flash("Username Already Taken, please choose a different username", "warning")
            return render_template('signup.html')
        mo1 = onlyChar.match(username)
        if not mo1 or mo1.group() != username:
            flash("Enter valid username", 'danger')
            return redirect(url_for('signup'))
        mo1 = emailReg.match(email)
        if not mo1 or mo1.group() != email:
            flash("Enter valid email address", 'danger')
            return redirect(url_for('signup'))
        encpassword = fernet.encrypt(password.encode())
        newuser = User(username=username, email=email,
                       type=type, password=encpassword)
        db.session.add(newuser)
        db.session.commit()
        flash("Signup Success Please Login", "success")
        return render_template('login.html')

    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and (password == (fernet.decrypt(user.password).decode())):
            login_user(user)
            flash("Login Success", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid credentials", "danger")
            return render_template('login.html')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul", "success")
    return redirect(url_for('login'))


@app.route('/register', methods=['POST', 'GET'])
@login_required
def register():
    farming = db.engine.execute("SELECT * FROM `farming`")
    if request.method == "POST":
        farmername = request.form.get('farmername')
        user = Register.query.filter_by(farmername=farmername).first()
        if user:
            flash(f'Farmer name {farmername} already taken', 'warning')
            return redirect(url_for(f'register'))
        mo1 = onlyChar.match(farmername)
        if not mo1 or mo1.group() != farmername:
            flash("Enter valid farmer name", 'danger')
            return redirect(url_for('register'))
        adharnumber = request.form.get('adharnumber')
        user = Register.query.filter_by(adharnumber=adharnumber).first()
        if user:
            flash(f'Aadhaar number {adharnumber} already present', 'warning')
            return redirect(url_for(f'register'))
        mo1 = aadhar.match(adharnumber)
        if not mo1 or mo1.group() != adharnumber:
            flash("Enter valid 12 digit aadhaar number", 'danger')
            return redirect(url_for('register'))
        age = request.form.get('age')
        gender = request.form.get('gender')
        phonenumber = request.form.get('phonenumber')
        mo2 = phone.match(phonenumber)
        if not mo2 or ''.join(mo2.groups()) != phonenumber:
            flash("Enter valid 10 digit phone number", 'danger')
            return redirect(url_for('register'))
        address = request.form.get('address')
        farmingtypes = request.form.getlist('farmingtypes')
        farmer = Register(farmername=farmername, adharnumber=adharnumber, age=age,
                          gender=gender, phonenumber=phonenumber, address=address, id=current_user.id)
        db.session.add(farmer)
        db.session.commit()
        rid = Register.query.filter_by(farmername=farmername).first().rid
        for farmingtype in farmingtypes:
            fid = Farming.query.filter_by(farmingtype=farmingtype).first().fid
            db.session.add(FarmingTypes(rid=rid, fid=fid))
            db.session.commit()
        flash(f'Farmer {farmername} added successfully', 'success')
        return redirect(f'/farmerdetails')
    return render_template('farmer.html', farming=farming)


@app.route('/resetpassword/<string:email>')
def reset_password(email):
    query = db.engine.execute(
        f'SELECT * FROM `user` WHERE email = \'{email}\'')
    if not query:
        flash('Invalid email id entered', 'danger')
        return redirect(url_for('forgotpw'))
    query = tuple(query)
    user = query[0]
    msg = Message('Forgot Password Request',
                  sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'Your password is {fernet.decrypt(user.password).decode()}'
    mail.send(msg)
    flash('Email sent successfully', 'success')
    return redirect(url_for('login'))


@app.route('/forgotpw', methods=['POST', 'GET'])
def forgotpw():
    if request.method == 'GET':
        return render_template('forgotpw.html')
    email = request.form.get('email')
    return redirect(url_for('reset_password', email=email))


@app.route('/deleteuser/<string:id>')
@login_required
def deleteuser(id):
    if current_user.is_authenticated and current_user.type.lower() != 'admin':
        flash('You do not have permission to view this page', 'danger')
        return redirect('/')
    db.engine.execute(f"DELETE FROM `user` WHERE `id`={id}")
    flash("Slot Deleted Successful", "danger")
    return redirect('/viewusers')


@app.route('/viewusers')
@login_required
def viewuser():
    if current_user.is_authenticated and current_user.type.lower() != 'admin':
        flash('You do not have permission to view this page', 'danger')
        return redirect('/')
    users = User.query.filter_by(type='user').all()
    return render_template('viewusers.html', users=users)


@app.route("/deleteprod/<string:pid>")
@login_required
def deleteprod(pid):
    pname = Addagroproducts.query.filter_by(pid=pid).first().productname
    db.engine.execute(f"DELETE FROM `addagroproducts` WHERE `pid`={pid}")
    flash(f"Product {pname} Deleted Successful", "success")
    return redirect(f'/myagroproducts')


@app.route('/editprod/<string:pid>', methods=['POST', 'GET'])
@login_required
def editprod(pid):
    posts = Addagroproducts.query.filter_by(pid=pid).first()
    rid = Register.query.filter_by(rid=posts.rid).first().rid
    query = db.session.execute(
        f'SELECT farmingtype FROM (register as r INNER JOIN farmingtypes as ft ON ft.rid = r.rid) INNER JOIN farming f ON f.fid = ft.fid where r.rid = {rid}')
    farming = tuple(db.engine.execute(
        f"select farmingtype from addagroproducts as ag, farming as f where pid = {pid} and ag.fid = f.fid"))[0].farmingtype
    if request.method == "POST":
        username = request.form.get('username')
        mo1 = onlyChar.match(username)
        if not mo1 or mo1.group() != username:
            flash("Enter valid username", 'danger')
            return redirect(url_for('editprod', pid=pid))
        email = request.form.get('email')
        mo1 = emailReg.match(email)
        if not mo1 or mo1.group() != email:
            flash("Enter valid email", 'danger')
            return redirect(url_for('editprod', pid=pid))
        productname = request.form.get('productname')
        mo1 = onlyChar.match(productname)
        if not mo1 or mo1.group() != productname:
            flash("Enter valid product name", 'danger')
            return redirect(url_for('editprod', pid=pid))
        productdesc = request.form.get('productdesc')
        mo1 = onlyChar.match(productdesc)
        if not mo1 or mo1.group() != productdesc:
            flash("Enter valid product description ", 'danger')
            return redirect(url_for('editprod', pid=pid))
        price = request.form.get('price')
        type = request.form.get('farmingtypes')
        fid = list(db.engine.execute(
            f'SELECT fid FROM `farming` where farmingtype = \'{type}\''))[0].fid
        db.session.execute(
            f"UPDATE addagroproducts SET username = '{username}', email = '{email}', productname = '{productname}', productdesc = '{productdesc}', price = {price}, fid = {fid} WHERE pid = {pid}")
        db.session.commit()
        flash(f"Update successful", "success")
        return redirect(f'/myagroproducts')

    return render_template('editagro.html', posts=posts, farming=farming, query=query)


app.run(debug=True)
