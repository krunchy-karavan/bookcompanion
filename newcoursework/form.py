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
    # a select field which has a choices parameter
    category = SelectField(u'Pick a category', choices=[])
    # a submit button to submit the form
    submit = SubmitField('submit')
    # an initialization function which will set the choices parameter to the list of categories
    def __init__(self, taglist=None):
        super().__init__()  
        if taglist: 
            # sets choices to all the categories in the list taglist
            self.category.choices = [(c[0],c[0]) for c in taglist]


class Signupform(FlaskForm):
    classic = StringField('Username')  
    banter = PasswordField('Password')

class PastebinEntry(FlaskForm):
    language = SelectField(u'Programming Language', choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')])

simpleList = ('hello', 'some string', 'hello 2')
searchTerm = 'so'
print(list(filter(lambda x: searchTerm in x, simpleList)))  