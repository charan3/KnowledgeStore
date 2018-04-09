from flask import Flask, request, session, redirect, url_for, abort, render_template, flash
from flask_sqlalchemy import SQLAlchemy
import datetime

from sqlalchemy import Table
import json
import random
app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SECRET_KEY'] ='super-secret-key'
app.config['USERNAME'] = 'admin'
app.config['PASSWORD'] = '12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///booksmart.db'

db=SQLAlchemy(app)

class Login(db.Model):
    # __tablename__ = 'users'
    email = db.Column(db.String(100), primary_key=True)
    name=db.Column(db.String(30))
    password = db.Column(db.String(240))
    phone = db.Column(db.String(20))
    address=db.Column(db.String(200))

    def __init__(self, name,email, password, phone, address):
        self.email = email
        self.password = password
        self.phone = phone
        self.address = address
        self.name=name

    def __repr__(self):
        return '<Entry %r %r %r %r>' % (self.email, self.password, self.phone, self.address)

class CustOrders(db.Model):
    # __tablename__ = 'users'
    order_id = db.Column(db.String(100),primary_key=True)
    email = db.Column(db.String(100), db.ForeignKey('login.email'))
    datetime = db.Column(db.DateTime)
    isbn=db.Column(db.String(100))
    quantity=db.Column(db.Integer)
    price=db.Column(db.Integer)
    book_id=db.Column(db.String(100))
    quants=db.Column(db.String(100))

    def __init__(self, email, order_id, datetime, isbn, quantity, price,book_id,quants):
        self.email = email
        self.order_id = order_id
        self.datetime = datetime
        self.isbn = isbn
        self.quantity = quantity
        self.price = price
        self.book_id=book_id
        self.quants=quants

    def __repr__(self):
        return '<Entry %r %r %r %r %r %r>' % (self.email, self.order_id, self.datetime, self.isbn, self.quantity, self.price)

class CurrentCart(db.Model):
    # __tablename__ = 'users'
    serial = db.Column(db.Integer, primary_key=True)
    id=db.Column(db.Integer)
    email = db.Column(db.String(100), db.ForeignKey('login.email'))
    isbn = db.Column(db.String(20))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Integer)

    def __init__(self, id,email, datetime, isbn, quantity, price):
        self.email = email
        self.isbn = isbn
        self.quantity = quantity
        self.price = price
        self.id=id

    def __repr__(self):
        return '<Entry %r %r %r %r>' % (
        self.email, self.isbn, self.quantity, self.price)

# Create the table
db.create_all()


def authenticate(e, p):
    print(e)
    details=Login.query.filter_by(email=e).filter_by(password=p).all()
    print(details)
    if(len(details)>0):
        return True
    else:
        return False

@app.route('/')
def homepage():
    return render_template('homepage.html', size=len(data['items']), data=data)

@app.route('/logout')
def logout():
	session['logged_in']=False
	return render_template('homepage.html', size=len(data['items']), data=data)

@app.route('/signup',methods=['GET','POST'])
def signup():
	error=None
	if request.method=='POST':
		email=request.form['username']
		name=request.form['name']
		password=request.form['password']
		phone=request.form['phone']
		address=request.form['address']
		user=Login(email=email,name=name,password=password,phone=phone,address=address)
		count=Login.query.filter_by(email=email).count()
		if(count>0):
			error="User Already exists"
		else:
			db.session.add(user)
			db.session.commit()
			flash("You are signed up successfully")
			return redirect(url_for('login'))
	return render_template('signup.html',error=error)

@app.route('/book/<int:id>/', methods=['GET','POST'])
def book(id):
	flag=0
	if request.method == 'GET':
		return render_template('book.html', id = id, data=data, flag=flag,size=len(data['items']))
	else:
		quantity=request.form.get('comp_select')
		isbn = 'ISBN' + str(data['items'][id]["volumeInfo"]["industryIdentifiers"][0]["identifier"])

		detail = CurrentCart.query.filter_by(id=id).filter_by(email=session['log_email']).all()
		sum=0
		for d in detail:
			sum+=(d.__dict__["quantity"])
		if sum+int(quantity)<4:
			record=CurrentCart.query.filter_by(id=id).filter_by(email=session['log_email']).all()
			s=0
			if len(record)>0:
				for r in record:
					s+=int(r.quantity)
					db.session.delete(r)
					db.session.commit()			
			cart=CurrentCart(id=id,email=session['log_email'], datetime=datetime.datetime.now(),isbn=isbn , quantity=int(quantity)+s, price=data['items'][id]["saleInfo"]["listPrice"]["amount"])
			db.session.add(cart)
			db.session.commit()
			flag = 1
		else:
			flag = 2
		return render_template('book.html', id=id, data=data, flag=flag, size=len(data['items']))


@app.route('/login',methods=['GET','POST'])
def login():

    error = None
    if request.method == 'POST':

        if(authenticate(request.form['username'], request.form['password'])):
            session['logged_in'] = True
            session['log_email'] = request.form['username']
            flash("You are logged in")
            return redirect(url_for('homepage'))
        else:
            error='Invalid credentials'
    return render_template('login.html', error=error)


@app.route('/cart', methods=['GET','POST'])
def cart():
    customerCart = CurrentCart.query.filter_by(email=session['log_email']).all()
    customer = Login.query.filter_by(email=session['log_email']).one()
    return render_template('cart.html',customerCart=customerCart,customer=customer,data=data,message="")

@app.route('/del/<int:id>/',methods=['GET','POST'])
def deleteproduct(id):
	product=CurrentCart.query.filter_by(id=id).filter_by(email=session['log_email']).one()
	db.session.delete(product)
	db.session.commit()
	return redirect(url_for('cart'))



@app.route('/user',methods=['GET','POST'])
def showdetails():
	if request.method=='POST':
		flag=1

	else:
		flag=0
	logged_email=session['log_email']
	details=Login.query.filter_by(email=logged_email).first()
	orders=CustOrders.query.filter_by(email=logged_email).all()
	return render_template('showorders.html',user=details,flag=flag,orders=orders)






@app.route('/payment',methods=['GET','POST'])
def payment():
	user=Login.query.filter_by(email=session['log_email']).first()
	customerCart = CurrentCart.query.filter_by(email=session['log_email']).all()
	cost=0
	for product in customerCart:
		cost+=product.quantity*product.price
	cgst=0.14*cost
	sgst=0.14*cost
	return render_template('checkoutform.html',cost=cost,cgst=cgst,sgst=sgst,orders=customerCart,user=user,data=data,count=len(customerCart))

@app.route('/confirmation',methods=['GET','POST'])
def confirmation():
	customerCart = CurrentCart.query.filter_by(email=session['log_email']).all()
	for order in customerCart:
		db.session.delete(order)
		db.session.commit()

	cost=0
	isbns=""
	ids=""
	qs=""
	tquantity=0
	for product in customerCart:
		cost+=product.quantity*product.price
		tquantity+=product.quantity
		qs+=str(product.quantity)+","
		isbns+=str(product.isbn)+","
		ids+=str(product.id)+","
	isbns=isbns[:-1]
	ids=ids[:-1]
	qs=qs[:-1]
	cgst=0.14*cost
	sgst=0.14*cost
	tcost=cost+cgst+sgst
	confirmorder=CustOrders(order_id=str(random.randint(0,100000)),email=session['log_email'],datetime=datetime.datetime.now(),isbn=isbns,quantity=tquantity,price=tcost,book_id=ids,quants=qs)
	db.session.add(confirmorder)
	db.session.commit()
	return render_template('confirmation.html',orders=customerCart,corder=confirmorder,count=len(customerCart),cost=cost,cgst=cgst,sgst=sgst,data=data)

with open("data\ooks.json") as data_file:
    data = json.loads(data_file.read())
    print(data['items'][0]['volumeInfo']['title'])

if __name__ == '__main__':
    app.run(debug=True)
