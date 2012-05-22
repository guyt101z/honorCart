import whoosh.index
import os
from flask.ext.whooshalchemy import _get_whoosh_schema_and_primary_key
from flask.ext.whooshalchemy import _QueryProxy, _Searcher


def _get_whoosh_index(app, model):
    # gets the whoosh index for this model, creating one if it does not exist.
    # A dict of model -> whoosh index is added to the ``app`` variable.

    if not hasattr(app, 'whoosh_indexes'):
        app.whoosh_indexes = {}

    return app.whoosh_indexes.get(model.__name__,
                _create_index(app, model))


def _create_index(app, model):
    # a schema is created based on the fields of the model. Currently we only
    # support primary key -> whoosh.ID, and sqlalchemy.(String, Unicode, Text)
    # -> whoosh.TEXT.

    if not app.config.get('WHOOSH_BASE'):
        # XXX todo: is there a better approach to handle the absenSe of a
        # config value for whoosh base? Should we throw an exception? If
        # so, this exception will be thrown in the after_commit function,
        # which is probably not ideal.

        app.config['WHOOSH_BASE'] = 'whoosh_index'

    # we index per model.
    wi = os.path.join(app.config.get('WHOOSH_BASE'),
            model.__name__)

    schema, primary_key = _get_whoosh_schema_and_primary_key(model)

    if whoosh.index.exists_in(wi):
        indx = whoosh.index.open_dir(wi)
    else:
        if not os.path.exists(wi):
            os.makedirs(wi)
        indx = whoosh.index.create_in(wi, schema)

    app.whoosh_indexes[model.__name__] = indx
    searcher = _Searcher(primary_key, indx)
    model.query = _QueryProxy(model.query, primary_key,
            searcher, model)

    model.pure_whoosh = searcher

    return indx
