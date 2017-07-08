from flask import Flask, redirect, render_template
from flask_bootstrap import Bootstrap
from flask_cors import cross_origin
from flask_sqlalchemy import SQLAlchemy

try:
    from accuconf_config import Config
except ImportError:
    from .configuration import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']
app.logger.info(app.url_map)

db = SQLAlchemy(app)

year = 2018


def presentation_to_json(presentation):
    result = {
        'id': presentation.id,
        'title': presentation.title,
        'text': presentation.text,
        'day': presentation.day.value,
        'session': presentation.session.value,
        'room': presentation.room.value,
        # 'track': presentation.track.value,
        'presenters': [presenter.presenter.id
                       for presenter
                       in presentation.presenters]
    }
    if presentation.quickie_slot:
        result['quickie_slot'] = presentation.quickie_slot.value
    return result


def presenter_to_json(presenter):
    return {
        'id': presenter.id,
        'last_name': presenter.last_name,
        'first_name': presenter.first_name,
        'bio': presenter.bio,
        'country': presenter.country,
        'state': presenter.state
    }


def scheduled_presentations():
    return Proposal.query.filter(Presentation.day != None, Presentation.session != None).all()


@app.route("/presentations", methods=['GET'])
@cross_origin()
def scheduled_presentations_view():
    prop_info = [presentation_to_json(prop) for prop in scheduled_presentations()]
    return jsonify(prop_info)


@app.route("/presenters", methods=["GET"])
@cross_origin()
def schedule_presenters_view():
    scheduled_presenter_ids = {
        presenter.presenter.id
        for prop in scheduled_presentations()
        for presenter in prop.presenters
    }
    json = [
        presenter_to_json(presenter)
        for presenter in Presenter.query.all()
        if presenter.id in scheduled_presenter_ids
    ]
    return jsonify(json)
