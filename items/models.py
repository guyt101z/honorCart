from database import db, Item, Category, Pricebreak
from werkzeug import secure_filename
import os

from PIL import Image


def get_categories():
    return Category.query.all()


def create_new_item(name, desc, price, qty, catId, image, pricebreaks, thumb=None):
    print "trying to create item"
    category = Category.query.filter_by(id=catId).first()

    new_item = Item(name, desc, price, qty, image, category, thumb)
    for thresh, pct in pricebreaks:
        new_item.pricebreaks.append(Pricebreak(thresh, pct))
    db.session.add(new_item)
    db.session.commit()


def validate_item(name, price, qty, category, pricebreaks):
    error = {}
    if is_name_duplicate(name):
        error['name'] = "Duplicate Name!"
    if name == '':
        error['name'] = "Name must not be blank!"
    try:
        if float(price) < 0:
            error['price'] = "Negative Prices aren't allowed!"
    except ValueError:
        error['price'] = "Enter a valid number!"
    try:
        if int(qty) < 0:
            error['qty'] = "Negative Prices aren't allowed!"
    except ValueError:
        error['qty'] = "Enter a valid integer!"
    if category and is_category_duplicate(category):
        error['addCat'] = "Duplicate Category!"
    if category == '':
        error['addCat'] = "Enter a Category!"
    for index, (thresh, pct) in enumerate(pricebreaks):
        error['pricebreak'] = {}
        error['pricebreak'][index] = {}
        try:
            if float(thresh) < 0:
                error['pricebreak'][index]['thresh'] = "Negative Price Thresholds aren't allowed!"
        except ValueError:
            error['pricebreak'][index]['thresh'] = "Enter a valid threshold!"
        try:
            if int(pct) < 0:
                error['pricebreak'][index]['pct'] = "Negative Percents aren't allowed!"
        except ValueError:
            error['pricebreak'][index]['pct'] = "Enter a valid percent!"
        if error['pricebreak'][index] == {}:
            del error['pricebreak'][index]
    if error.get('pricebreak') == {}:
        del error['pricebreak']
    return error


def create_category(category):
    if not is_category_duplicate(category):
        new_category = Category(category)
        db.session.add(new_category)
        db.session.commit()
        return new_category.id
    else:
        return -1


def is_name_duplicate(name):
    items = Item.query.filter_by(name=name).all()
    if len(items) == 0:
        return False
    else:
        return True


def is_category_duplicate(category):
    categories = Category.query.filter_by(name=category).all()
    if len(categories) == 0:
        return False
    else:
        return True


def get_items(category=None):
    if category:
        return Item.query.filter_by(category_id=category).all()
    else:
        return Item.query.all()


def get_item(id):
    return Item.query.filter_by(id=id).first()


def get_pricebreaks(id):
    return Item.query.filter_by(id=id).first().pricebreaks


def update_item_description(id, desc, picture=None):
    item = get_item(id)
    if item:
        item.description = desc
        if picture:
            item.picture = picture
        db.session.add(item)
        db.session.commit()


def update_pricebreaks(id, pricebreaks):
    item = get_item(id)
    if item:
        oldPricebreaks = item.pricebreaks.all()
        for pricebreak in oldPricebreaks:
            item.pricebreaks.remove(pricebreak)
        for thresh, pct in pricebreaks:
            item.pricebreaks.append(Pricebreak(thresh, pct))
        db.session.add(item)
        db.session.commit()


def split_form_data(input):
    output = dict()
    for key, value in input.iteritems(multi=True):
        (id, outKey) = key.split('-', 1)
        if id not in output:
            output[id] = {}
        output[id][outKey] = value
    return output


def update_item(id, name, price, qty, catId):
    item = Item.query.filter_by(id=id).first()
    item.name = name
    item.price = price
    item.inStock = qty
    item.category = Category.query.filter_by(id=catId).first()
    db.session.add(item)
    db.session.commit()

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def upload_image(file):
    errors = {}
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        try:
            file.save(os.path.join(UPLOAD_FOLDER, filename))
        except IOError:
            errors['file'] = "File failed to upload."
        saveFilePath = os.path.join(UPLOAD_FOLDER, filename)
        saveThumbPath = os.path.join(UPLOAD_FOLDER, 'thumbs', filename)
        img = Image.open(saveFilePath)
        wpercent = (120. / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((120, hsize), Image.ANTIALIAS)
        img.save(saveThumbPath)
    return {'errors': errors, 'image': saveFilePath, 'thumb': saveThumbPath}
