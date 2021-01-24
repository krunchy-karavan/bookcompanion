from flask_wtf import Form, FlaskForm
from wtforms import StringField, PasswordField, SubmitField


# creating the class for a form for the inputs of the recommender algorithm.
class BaseFormTemplate(FlaskForm):
    pass

class recommender_inputs(BaseFormTemplate):
   def __init__(self,dictionary):
        for key,value in dictionary.items():
            setattr(self,key,value)
    
  
    


class Signupform(FlaskForm):
    classic = StringField('Username')  
    banter = PasswordField('Password')

