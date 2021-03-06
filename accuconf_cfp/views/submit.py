from flask import jsonify, render_template, request, session

from accuconf_cfp import app, db, year
from accuconf_cfp.utils import is_acceptable_route, is_logged_in, md

from models.user import User
from models.proposal import Presenter, Proposal, ProposalPresenter
from models.proposal_types import SessionType


def validate_presenters(presenters):
    """Presenter data is not invalid."""
    mandatory_keys = ["lead", "email", "name", "country", "state"]
    lead_found = False
    lead_presenter = ""
    for presenter in presenters:
        for key in mandatory_keys:
            if key not in presenter:
                return False, "{} attribute is mandatory for Presenters".format(key)
            if presenter[key] is None:
                return False, "{} attribute should have valid data".format(key)
        if "lead" in presenter and "email" in presenter:
            if presenter["lead"] and lead_found:
                return False, "{} and {} are both marked as lead presenters".format(presenter["email"], lead_presenter)
            elif presenter["lead"] and not lead_found:
                lead_found = True
                lead_presenter = presenter["email"]
    return True, "validated"


def validate_proposal_data(proposal_data):
    """Proposal data is not invalid."""
    mandatory_keys = ['title', 'abstract', 'session_type', 'presenters']
    for key in mandatory_keys:
        if key not in proposal_data:
            return False, '{} information is not present in proposal'.format(key)
        if proposal_data[key] is None:
            return False, '{} information should not be empty'.format(key)
    if type(proposal_data['presenters']) != list:
        return False, 'presenters data is malformed'
    if len(proposal_data['presenters']) < 1:
        return False, 'At least one presenter needed'
    if len(proposal_data.get('title')) < 5:
        return False, 'Title is too short'
    if len(proposal_data.get('abstract')) < 50:
        return False, 'Proposal too short'
    (result, message) = validate_presenters(proposal_data['presenters'])
    if not result:
        return result, message
    return True, 'validated'


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    check = is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    page = {
        'title': 'Submit',
        'year': year,
    }
    if is_logged_in():
        if request.method == 'POST':
            user = User.query.filter_by(email=session['email']).first()
            if user:
                proposal_data = request.json
                status, message = validate_proposal_data(proposal_data)
                response = {}
                if status:
                    proposal = Proposal(
                        user,
                        proposal_data.get('title').strip(),
                        SessionType(proposal_data.get('session_type')),
                        proposal_data.get('abstract').strip()
                    )
                    db.session.add(proposal)
                    presenters_data = proposal_data.get('presenters')
                    for presenter_data in presenters_data:
                        presenter = Presenter(
                            presenter_data['email'],
                            presenter_data['name'],
                            'A human being.',
                            presenter_data['country'],
                            presenter_data['state'],
                        )
                        ProposalPresenter(proposal, presenter, presenter_data['lead'])
                        db.session.add(presenter)
                    db.session.commit()
                    response['success'] = True
                    response['message'] = '''Thank you, you have successfully submitted a proposal for the ACCU {} conference!
If you need to edit it you can via the 'My Proposal' menu item.'''.format(year)
                    response['redirect'] = '/'
                else:
                    response['success'] = False
                    response['message'] = message
                return jsonify(**response)
        else:
            user = User.query.filter_by(email=session['email']).first()
            if user:
                return render_template('submit.html', page={
                    'title': 'Submit a proposal for ACCU {}'.format(year),
                    'name': user.name,
                    'proposer': {
                        'email': user.email,
                        'name': user.name,
                        'bio': 'A human being.',
                        'country': user.country,
                        'state': user.state,
                    }
                })
    return render_template('failure.html', page=md(page, {'data': 'Must be logged in to submit a proposal.'}))
