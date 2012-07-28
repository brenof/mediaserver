import os.path

from flask import Flask, request, session, g, redirect, \
     render_template, jsonify
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user
from flask.ext.wtf import Form, TextField, PasswordField, Required, Email
from flask.ext.bcrypt import Bcrypt

from mediaserver.datastore import Datastore 
from mediaserver.filesystem import FileSystem
from model import LoginForm
from flask.helpers import make_response, send_from_directory

# configuration
DEBUG = True
SECRET_KEY = 'development key'
BASEDIR = '/home/breno/tmp'


# some globals
ds = Datastore()
fs = FileSystem(BASEDIR)
app = Flask(__name__)
 
 
# run some app configuration
app.config.from_object(__name__)
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.setup_app(app)

@login_manager.user_loader
def load_user(userid):
    return ds.find_user(id=userid)


### PATHS

## views
# main view
@app.route('/', methods=['GET'])
def main():
    if current_user.is_authenticated():
        return render_template('inside.html')
    else:
        return redirect('/login')
    
# login view
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

# logout pseudo-view
@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    logout_user()
    return redirect(request.args.get('next') or '/login')

## restful api
# list a dir or download a file
@app.route('/media/', methods=['GET'])
@app.route('/media/<path:p>', methods=["GET"])
#@login_required
def read(p="."):
    if not os.path.exists(p):
        return make_response(jsonify(description="The path does not exists."), 404)
    if fs.is_dir(p) or '*' in p:
        return jsonify(content=fs.ls(p))
    else:
        return send_from_directory(fs.split(p)[0], fs.split(p)[1])

# create a dir or a file
@app.route('/media/', methods=['PUT', 'POST'])
@app.route('/media/<path:p>', methods=['PUT', 'POST'])
def write(p='.'):
    
    if request.json:
        if not request.json.has_key('params'):
            return make_response(jsonify(description='The key "params" is missing.'), 400)
        params = request.json['params']
        if (not params.has_key('path') or not params.has_key('name')):
            return make_response(jsonify(description='The "mkdir" operation requires the "path" and "name" parameters.'), 400)
        try:
            fs.mkdir(params['path'], params['name'])
        except OSError:
            return make_response(jsonify(description='The fil exists already.'), 500)
    
    else:
        
        fil = request.files['file']
        if fil:
            if request.method == 'PUT':
                fs.save(p, fil, True)
            else:
                fs.save(p, fil, False)
            
    return jsonify(description="ok")

# delete a dir or a file
@app.route('/media/', methods=['DELETE'])
@app.route('/media/<path:p>', methods=['DELETE'])
def delete(p='.'):
    fs.delete(p)
    return jsonify(description="ok")
    
# touch -- only for testing
@app.route('/touch', methods=["POST", "PUT"])
#@login_required
def touch():
    path = request.json['path']
    filename = request.json['filename']
    fs.touch(filename, path)
    return jsonify(status='ok')

if __name__ == '__main__':
    app.run()
