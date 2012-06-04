from database import db, Item, Category, User
from global_mail import mail, Message


def get_items(category):
    return Item.query.filter_by(category_id=category).filter(Item.inStock > 0).all()


def get_item(itemid):
    return Item.query.filter_by(id=itemid).first()


def send_admin_alert(problem_type, item_id, user_id, comments):
    user = User.query.filter_by(id=user_id).first()
    item = Item.query.filter_by(id=item_id).first()
    msg = Message("Alert from LVL1 Store", recipients=['BradLuyster@gmail.com'])
    msg.body = "This is an automated message from the LVL1 store\r\n\r\n"
    msg.body += "A complaint of type " + problem_type + " has been reported.\r\n"
    msg.body += "User " + user.username + " is complaining about item " + item.name + " with id " + str(item.id) + ".\r\n"
    msg.body += "They further state:\r\n" + comments + "\r\n"
    mail.send(msg)
