from flask import Flask, current_app, session, request
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user
from flask.ext.wtf import Form, TextField, PasswordField, Required, Email

app = Flask(__name__) 
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(userid):
    # TODO: get user from datastore
    return datastore.find_user(id=userid)

class LoginForm(Form):
    email = TextField()
    password = PasswordField()
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        # get user object and validate
        user = datastore.find_user(email=form.email.data)
        if bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(request.args.get('next') or '/') 
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(request.args.get('next') or '/')
