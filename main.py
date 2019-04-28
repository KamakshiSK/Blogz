from flask import Flask, redirect, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] =True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Blogz:launchcodelc101@localhost:8889/Blogz'

app.config['SQLALCHEMY_ECHO'] = True

db =SQLAlchemy(app)
app.secret_key = "k3nd3ybtje9J3saY"

class Blog(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    
    def __init__(self, title, content, owner, timestamp=None):
        self.title = title
        self.content =  content
        if timestamp == None:
            self.timestamp = datetime.utcnow()
        self.owner = owner

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable= False)
    password = db.Column(db.String(120), nullable = False)

    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, name, password):
        self.name = name
        self.password = password

@app.before_request
def require_login():
    allowed_route = ['login', 'signup','index', 'blog']
    if request.endpoint not in allowed_route and 'email' not in session:
        return redirect("/login")

@app.route('/login', methods=['GET', 'POST'])
def login():
    user_email=""
    if request.method == 'POST':
        user_email = request.form['email']
        user_password = request.form['password']

        user = User.query.filter_by(name=user_email).first()

        if not user_email.strip():
            flash('Username cannot be empty', category='error_email')
            return redirect('/login')

        elif not user_password.strip():
            flash('Password cannot be empty', category='error_password')
            return redirect('/login')

        elif not user:
            flash('User does not exits. Please check the user name or regiter new.', category='error_email')
            return redirect('/login')

        elif user.password != user_password:
            flash('Password is incorrect.', category='error_password')
            return redirect('/login')

        else:
            session['email'] = user_email
            flash('Logging successful.', category='success')
            return redirect('/newpost')

    return render_template("login.html", email=user_email)

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    user_email=""
    if request.method == 'POST':
        user_email = request.form['email']
        user_password = request.form['password']
        user_verify_pwd = request.form['verify']

        existing_user = User.query.filter_by(name=user_email).first()

        if not user_email.strip():
            flash("Email cannot be empty", category='email_error')
            redirect("/signup")
        elif not user_password.strip():
            flash("password cannot be empty", category="password_error")
            redirect("/signup")

        elif user_password.isspace():
            flash("Password cannot have space", category='password_error')
            redirect("/signup")

        elif len(user_email) < 3:
            flash("Invalid Email.", category='email_error')
        
        elif len(user_password) < 3:
            flash("Invalid Password.", category='password_error')


        elif user_password != user_verify_pwd:
            flash("Passwords don't match.", category='verify_password_error')
            redirect("/signup")

        elif not existing_user:
            new_user = User(user_email, user_password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = user_email

            flash('New user created successfully.', category='success')

            return redirect("/newpost")

        else:
            flash("Duplicate User.", category="email_error")

    return render_template("signup.html",email=user_email)

@app.route('/')
def index():
    all_users = User.query.all()
    return render_template("index.html", users = all_users)


@app.route('/blog')
def blog():
    user = request.args.get('user')
    selected_user = User.query.filter_by(name = user).first()

    id = request.args.get('id')

    if user:
        user_posts = Blog.query.filter_by(owner = selected_user).order_by(Blog.timestamp.desc()).all()
        return render_template("singleUser.html", title="All Blogs", user = selected_user, posts = user_posts )
    if id:
        post = Blog.query.filter_by(post_id=id).first()
        post_owner=User.query.join(Blog).filter_by(owner_id=User.user_id).filter_by(post_id=id).first()
        return render_template ("blog.html", user=post_owner, posts = [post])

    all_posts_with_user = Blog.query.join(User).filter_by(user_id=Blog.owner_id).order_by(Blog.timestamp.desc()).add_column(Blog.content).add_column(Blog.post_id).add_column(Blog.title).add_column(User.name).add_column(Blog.timestamp).all()
    return render_template("blog.html", title = "Build a Blog", posts = all_posts_with_user)

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    if request.method == 'POST':
        this_owner = User.query.filter_by(name=session['email']).first()

        post_title = request.form['title']
        post_content = request.form['content']

        if not post_title:
            flash("Please enter post title.", category="title_error")
            return render_template("newpost.html", title = post_title, content = post_content)

        if not post_content:
            flash("Please enter contents for the post.", category="content_error")
            return render_template("newpost.html", title = post_title)
            
        blog = Blog(post_title, post_content, this_owner)
        db.session.add(blog)
        db.session.commit()

        flash("Blog entry successful.", category='success')

        return redirect("/blog?id={}".format(blog.post_id))

    else:
        return render_template("newpost.html")  

if __name__ == '__main__':
    app.run()
