from items import items_bp
from flask import render_template, request, flash, redirect, url_for, jsonify
from flaskext.login import login_required, current_user
from werkzeug import secure_filename
import os
from models import get_categories, validate_item, create_category, create_new_item
from models import get_items, get_item, update_item_description, get_pricebreaks, update_pricebreaks
from models import split_form_data, update_item

from PIL import Image

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@items_bp.route('/addItem', methods=['GET', 'POST'])
@login_required
def add_item():
    if not current_user.isAdmin():
        flash(u'<strong>Error!</strong> You don\'t have permission to go there!', 'error')
        return redirect(url_for('main'))

    errors = {}
    pricebreaks = ()
    formdata = request.form.copy()
    if request.method == 'POST':
        print request.form
        pricebreaks = zip(request.form.getlist('pbThresh'), request.form.getlist('pbPct'))
        pricebreaks = [value for value in pricebreaks if value != ('', '')]
        errors = validate_item(request.form.get('name'), request.form.get('price'), request.form.get('qty'),
            request.form.get('addCategory'), pricebreaks)

        saveFilePath = None
        file = request.files['picture']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            try:
                file.save(os.path.join(UPLOAD_FOLDER, filename))
            except IOError:
                errors['file'] = "File failed to upload."
            saveFilePath = os.path.join(UPLOAD_FOLDER, filename)
            img = Image.open(saveFilePath)
            wpercent = (120. / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(wpercent)))
            img = img.resize((120, hsize), Image.ANTIALIAS)
            img.save(UPLOAD_FOLDER + 'thumbs/' + filename)


        if errors == {}:
            cat_id = request.form.get('category')
            print cat_id
            if int(cat_id) == -1:
                cat_id = create_category(request.form.get('addCategory'))
            create_new_item(request.form.get('name'), request.form.get('desc'), request.form.get('price'),
                request.form.get('qty'), cat_id, saveFilePath, pricebreaks)
            formdata.clear()
            pricebreaks = ()
            flash(u'<strong>Congratulations!</strong> Item was added successfully!', 'success')
        else:
            flash(u'<strong>Uh oh, Boss!</strong> Errors in the form below.', 'error')

    return render_template('add_item.html', categories=get_categories(), error_list=errors, pricebreaks=pricebreaks, formdata=formdata)


@items_bp.route('/modifyItems', methods=['GET', 'POST'])
@login_required
def modify_item():
    if not current_user.isAdmin():
        flash(u'<strong>Error!</strong> You don\'t have permission to go there!', 'error')
        return redirect(url_for('main'))

    if request.method == 'POST':
        data = split_form_data(request.form)
        for id, values in data.iteritems():
            update_item(id, values['name'], values['price'], values['qty'], values['categories'])


    items = get_items()
    if request.args.get('filter') and request.args.get('filter') != '-1':
        items = get_items(request.args.get('filter'))

    return render_template('bulk_modify.html', categories=get_categories(), items=items)


@items_bp.route('/modifyItems/addCategory', methods=['POST'])
@login_required
def add_category():
    if not current_user.isAdmin():
        flash(u'<strong>Error!</strong> You don\'t have permission to go there!', 'error')
        return redirect(url_for('main'))

    rv = create_category(request.form.get('addCat'))
    if rv != -1:
        flash('<strong>Success!</strong> Category Added!', 'success')
    else:
        flash('<strong>Failure!</strong> Category Not Added!', 'error')

    return redirect(url_for('.modify_item'))


@items_bp.route('/modifyItems/getEditModalContent')
@login_required
def get_edit_modal_content():
    if not current_user.isAdmin():
        flash(u'<strong>Error!</strong> You don\'t have permission to go there!', 'error')
        return redirect(url_for('main'))
    if request.args.get('modal') == 'description':
        if request.args.get('id'):
            return render_template('description_modal_content.html', item=get_item(request.args.get('id')))
    if request.args.get('modal') == 'pricebreaks':
        if request.args.get('id'):
            return render_template('pricebreak_modal_content.html', pricebreaks=get_pricebreaks(request.args.get('id')), id=request.args.get('id'))


@items_bp.route('/modifyItems/updateDescription', methods=['POST'])
@login_required
def edit_description():
    if not current_user.isAdmin():
        flash(u'<strong>Error!</strong> You don\'t have permission to go there!', 'error')
        return redirect(url_for('main'))

    saveFilePath = None
    file = request.files.get('picture')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        try:
            file.save(os.path.join(UPLOAD_FOLDER, filename))
        except IOError:
            flash("File failed to upload.", 'errors')
        saveFilePath = os.path.join(UPLOAD_FOLDER, filename)
        update_item_description(request.form.get('id'),
            request.form.get('desc'), saveFilePath)
    else:
        update_item_description(request.form.get('id'),
            request.form.get('desc'))

    return jsonify(status='success')


@items_bp.route('/modifyItems/updatePricebreaks', methods=['POST'])
@login_required
def update_pricebreaks_page():
    if not current_user.isAdmin():
        flash(u'<strong>Error!</strong> You don\'t have permission to go there!', 'error')
        return redirect(url_for('main'))

    pricebreaks = zip(request.form.getlist('pbThresh'), request.form.getlist('pbPct'))
    pricebreaks = [value for value in pricebreaks if value != ('', '')]

    print pricebreaks

    update_pricebreaks(request.form.get('id'), pricebreaks)

    return jsonify(status='success')
