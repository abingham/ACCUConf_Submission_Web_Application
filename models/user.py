#  The accuconf name is created as an alias for the application package at run time.
from accuconf import db

from models.role_types import Role


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    passphrase = db.Column(db.String(400), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    role = db.Column(db.Enum(Role), nullable=False)
    street_address = db.Column(db.String(400), nullable=False)
    town_city = db.Column(db.String(30), nullable=False)
    state = db.Column(db.String(40), nullable=True)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(60), nullable=False)
    phone = db.Column(db.String(18), nullable=True)  # ITU E.165 limits numbers to 15 digits
    proposals = db.relationship('Proposal', back_populates='proposer')
    scores = db.relationship('Score', back_populates='scorer')
    comments = db.relationship('Comment', back_populates='commenter')

    def __init__(self, email, passphrase, name, street_address, town_city, postal_code, country, state=None, phone=None, role=Role.user):
        self.email = email
        self.passphrase = passphrase
        self.name = name
        self.role = role
        self.street_address = street_address
        self.town_city = town_city
        self.state = state
        self.postal_code = postal_code
        self.country = country
        self.phone = phone
