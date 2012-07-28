from flask.ext.wtf import Form, TextField, PasswordField

class LoginForm(Form):
    email = TextField()
    password = PasswordField()
    
    def validate(self):
        return self.email != None and self.password != None