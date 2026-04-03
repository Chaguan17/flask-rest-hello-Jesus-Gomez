import os
from flask_admin import Admin
from models import db, User,People,Planet,Favorite
from flask_admin.contrib.sqla import ModelView

class FavoriteAdmin(ModelView):
    column_list = ("id", "user_email", "favorite_type", "favorite_name")

    def _user_email(view, context, model, name):
        return model.user.email if model.user else ""

    def _favorite_type(view, context, model, name):
        if model.people:
            return "People"
        elif model.planet:
            return "Planet"
        return ""

    def _favorite_name(view, context, model, name):
        if model.people:
            return model.people.name
        elif model.planet:
            return model.planet.name
        return ""

    column_formatters = {
        "user_email": _user_email,
        "favorite_type": _favorite_type,
        "favorite_name": _favorite_name
    }

    column_labels = {
        "user_email": "Usuario",
        "favorite_type": "Tipo",
        "favorite_name": "Nombre"
    }



def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')



    
    # Add your models here, for example this is how we add a the User model to the admin
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(People, db.session))
    admin.add_view(ModelView(Planet, db.session))
    admin.add_view(FavoriteAdmin(Favorite, db.session))

    # You can duplicate that line to add mew models
    # admin.add_view(ModelView(YourModelName, db.session))