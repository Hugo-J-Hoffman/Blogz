
        #obj = Blog.query.order_by(Blog.id.desc()).first()
 #if request.method == 'POST':
  #      blog = str(request.args.get('id'))
   #     entry = Blog.query.get(blog)
    #    title = entry.title
     #   body = entry.body
      #  return render_template('/blog.html', title = title , body = body)
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogs:blogs@localhost:8889/blogs'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
       
    def __init__(self, title, body, author):
        self.title = title
        self.body = body
        self.author = author

    def __repr__(self):
        return '<Blog %r>' % id

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='author')
       
    def __init__(self, email, password):
        self.email = email
        self.password = password
    
    def __repr__(self):
        return '<User %r>' % id

def is_email(string):
    # for our purposes, an email string has an '@' followed by a '.'
    # there is an embedded language called 'regular expression' that would crunch this implementation down
    # to a one-liner, but we'll keep it simple:
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >= 0
        return domain_dot_present

@app.route('/index', methods=['POST', 'GET'])
def index():
    if request.args.get('id'):
        db.create_all()
        post = request.args.get('id')
        b_id = Blog.query.filter_by(id=post).first()
        title = b_id.title
        body = b_id.body
        author = b_id.author
        return render_template('/blog.html', title = title, body = body, author = author)
    if request.args.get('user-id'):
        db.create_all()
        post = request.args.get('user-id')
        blogs = Blog.query.filter_by(owner_id=post).all()
        return render_template('/blog-list.html', blogs = blogs)
    db.create_all()
    users = User.query.all()
    return render_template('/index.html', users=users)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        vpassword = request.form['vpassword']
        password_error=""
        vpassword_error=""
        email_error=""
        if len(password)>20 or len(password)<3:
            password_error= "That is not a valid password"
        if password != vpassword:
            password_error= "Passwords must match"
            vpassword_error= "Passwords must match"
        if len(email)>20 or len(email)<3:
            email_error= "That is not a valid email"
        if "@" not in email or "." not in email:
            email_error= "That is not a valid email"
        if User.query.filter_by(email=email).all():
            email_error= "That email is already taken"
        if password_error=="" and vpassword_error=="" and email_error=="":
            user = User(email=email, password=password)
            db.session.add(user)
            db.session.commit()
            session['user'] = user.email
            return redirect("/")
        return render_template('signup.html', password_error = password_error, vpassword_error = vpassword_error, email_error = email_error)
    else:
        return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = User.query.filter_by(email=email)
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['user'] = user.email
                flash('welcome back, '+user.email)
                return redirect("/")
            return render_template("login.html", password_error= "Incorrect Password")
        return render_template("login.html", email_error="Email does not match any accounts")


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    del session['user']
    return redirect("/")

@app.route('/', methods=['POST', 'GET'])
def newpost():
    return render_template('/newpost.html')

@app.route('/blog', methods=['POST', 'GET'])
def blogs():
    if request.method == 'POST':
        title = request.form['text']
        blog_body = request.form['body']
        author = User.query.filter_by(email=session['user']).first()
        if len(blog_body) == 0 and len(title) == 0:
            title_error = "Please enter more than one character"
            body_error = "Please enter more than one character"
            return render_template('/newpost.html', body_error=body_error, title_error = title_error, title = title, body = blog_body)
        if len(title) == 0:
            title_error = "Please enter more than one character"
            return render_template('/newpost.html', title_error = title_error, body = blog_body)
        if len(blog_body) == 0:
            body_error = "Please enter more than one character"
            return render_template('/newpost.html', body_error=body_error, title = title)
        new_blog = Blog(title=title, body=blog_body, author=author)
        db.session.add(new_blog)
        db.session.commit()
        return render_template('/blog.html', title = title, body = blog_body, author = author)
    return redirect('/index')

@app.before_request
def require_login():
    allowed_routes = ['blog', 'signup','login','index']
    if 'user' not in session and request.endpoint not in allowed_routes:
        return redirect('/login')

if __name__ == '__main__':
    app.run()
    
    