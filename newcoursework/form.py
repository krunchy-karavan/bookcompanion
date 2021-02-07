from flask_wtf import Form, FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField


# creating the class for a form for the inputs of the recommender algorithm.
class BaseFormTemplate(FlaskForm):
    pass

class recommender_inputs(BaseFormTemplate):
   def __init__(self,dictionary):
        for key,value in dictionary.items():
            setattr(self,key,value)
    
  
class CategorySelect(FlaskForm):
    category = SelectField(u'Pick a category', choices=[])
    def __init__(self, taglist=None):
        super().__init__()  # calls the base initialisation and then...
        if taglist: 
            self.category.choices = [(c[0],c[0]) for c in taglist]


class Signupform(FlaskForm):
    classic = StringField('Username')  
    banter = PasswordField('Password')

class PastebinEntry(FlaskForm):
    language = SelectField(u'Programming Language', choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')])

