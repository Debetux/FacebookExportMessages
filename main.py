from app import app
from models import *
import views

if __name__ == '__main__':
    User.create_table(True)
    Conversation.create_table(True)
    Message.create_table(True)
    app.run(host='0.0.0.0', port=5151, debug=True)
