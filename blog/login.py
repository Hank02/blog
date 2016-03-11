from flask.ext.login import LoginManager
from blog import app
from .database import session, User

# create instance of login manager
login_manager = LoginManager()
# initialize instance of login manager
login_manager.init_app(app)

# object attribute: view to which authorized user is redirectred
login_manager.login_view = "login_get"
# object attribute: classify any error message from Flask-login
login_manager.login_message_category = "danger"

@login_manager.user_loader
def load_user(id):
    return session.query(User).get(int(id))