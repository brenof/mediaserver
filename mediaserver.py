from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user
from flask.ext.wtf import Form, TextField, PasswordField, Required, Email
from flask.ext.bcrypt import Bcrypt

from mediaserver.datastore import Datastore 

# configuration
DEBUG = True
SECRET_KEY = 'development key'

ds = Datastore()

app = Flask(__name__) 
app.config.from_object(__name__)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.setup_app(app)

@login_manager.user_loader
def load_user(userid):
    # TODO: get user from datastore
    return ds.find_user(id=userid)

class LoginForm(Form):
    email = TextField()
    password = PasswordField()
    
    def validate(self):
        return self.email != None and self.password != None
    
@app.route('/', methods=['GET'])
def main():
    if current_user.is_authenticated():
        return render_template('main.html')
    else:
        return redirect('/login')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # get user object and validate
        print form.email.data
        user = ds.find_user(email=form.email.data)
        if bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            session['logged_in'] = True
            return redirect(request.args.get('next') or '/') 
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    logout_user()
    return redirect(request.args.get('next') or '/login')

if __name__ == '__main__':
    app.run()
