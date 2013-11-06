from wtforms import Form, TextField, DateField, PasswordField, validators

class LoginForm(Form):
    email = TextField("Email", [validators.Required(), validators.Email()])
    password = PasswordField("Password", [validators.Required()])

class NewPlanForm(Form):
    name = TextField("name", [validators.Required()])
    start_date = DateField("start_date", [validators.Required()])
    end_date = DateField("end_date", [validators.Required()])
