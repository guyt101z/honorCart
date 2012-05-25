from database import db, Item, Category, Pricebreak
from werkzeug import secure_filename
import os
import uuid

from thumbnail import prepare_image

from PIL import Image


def get_categories():
    cats = Category.query.all()
    db.session.remove()
    return cats


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
    db.session.commit()
    if len(items) == 0:
        return False
    else:
        return True


def is_category_duplicate(category):
    categories = Category.query.filter_by(name=category).all()
    db.session.commit()
    if len(categories) == 0:
        return False
    else:
        return True


def get_items(category=None):
    if category:
        item = Item.query.filter_by(category_id=category).all()
        db.session.commit()
        return item
    else:
        return Item.query.all()


def get_item(id):
    item = Item.query.filter_by(id=id).first()
    db.session.commit()
    return item


def get_pricebreaks(id):
    breaks = Item.query.filter_by(id=id).first().pricebreaks
    db.session.commit()
    return breaks


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
        oldPricebreaks = item.pricebreaks
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
    if float(catId) != item.category_id:
        cat = Category.query.filter_by(id=catId).first()
        item.category = cat
    db.session.commit()

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_image(file):
    errors = {}
    saveFilePath = ""
    saveThumbPath = ""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filename, fileext = os.path.splitext(filename)
        # File names set to UUID to avoid duplicated image names.
        # Not fast, but easy here.
        fileUuid = str(uuid.uuid1())
        saveFilePath = os.path.join(UPLOAD_FOLDER, fileUuid + fileext)
        saveThumbPath = os.path.join(UPLOAD_FOLDER, 'thumbs', filename + fileext)
        try:
            file.save(saveFilePath)
        except IOError:
            errors['file'] = "File failed to upload."
        img = Image.open(saveFilePath)
        thumbnail = prepare_image(img, (120, 120))
        thumbnail.save(saveThumbPath)
    return {'errors': errors, 'image': saveFilePath, 'thumb': saveThumbPath}


def delete_item(itemid):
    item = get_item(itemid)
    db.session.delete(item)
    db.session.commit()
