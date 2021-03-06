from flask import (Flask, render_template, request,
                   redirect, jsonify, url_for, flash)
from flask import session as login_session
from flask import make_response
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Sport, Item
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import random
import requests
import string

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Sports Item Catalog Application"


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                                'Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['id']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['email']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; '
    output += 'height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;'
    output += '-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['email'])
    print "done!"
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session.
@app.route("/gdisconnect")
def gdisconnect():
    print 'Current login session info: '
    print login_session

    # only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
                                'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Execute HTTP GET request to revoke current token.
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    print 'Access token is: '
    print login_session['access_token']

    url = "https://accounts.google.com/o/oauth2/revoke?token=%s" % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'Result is: '
    print result

    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(json.dumps(
                                'Failed to revoke token for give user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Sport Information
@app.route('/sport/<int:sport_id>/items/JSON')
def sportSportJSON(sport_id):
    engine = create_engine('sqlite:///sportscatalog.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    sport = session.query(Sport).filter_by(id=sport_id).one()
    items = session.query(Item).filter_by(
        sport_id=sport_id).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/sport/<int:sport_id>/item/<int:item_id>/JSON')
def itemItemJSON(sport_id, item_id):
    engine = create_engine('sqlite:///sportscatalog.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Sport_Item = session.query(Item).filter_by(id=item_id).one()
    return jsonify(Sport_Item=Sport_Item.serialize)


@app.route('/sports/JSON')
def sportsJSON():
    engine = create_engine('sqlite:///sportscatalog.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    sports = session.query(Sport).all()
    return jsonify(sports=[r.serialize for r in sports])


# Show all sports
@app.route('/')
@app.route('/sport/')
def showSports():
    engine = create_engine('sqlite:///sportscatalog.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    sports = session.query(Sport).order_by(asc(Sport.name))
    return render_template('item_catalog.html', sports=sports)


# Create a new sport
@app.route('/sport/new/', methods=['GET', 'POST'])
def newSport():
    engine = create_engine('sqlite:///sportscatalog.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newSport = Sport(
                         name=request.form['name'],
                         username=login_session['username'])
        session.add(newSport)
        flash('New Sport %s Successfully Created' % newSport.name)
        session.commit()
        return redirect(url_for('showSports'))
    else:
        return render_template('newSport.html')


# Edit a sport
@app.route('/sport/<int:sport_id>/edit/', methods=['GET', 'POST'])
def editSport(sport_id):
    engine = create_engine('sqlite:///sportscatalog.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    """Allows user to edit an existing category"""
    editedSport = session.query(
        Sport).filter_by(id=sport_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedSport.username != login_session['username']:
        return ("""<script>function unauthorized()
                {alert('You are unauthorized to make this action.')}
                </script><body onload='unauthorized()'>""")
    if request.method == 'POST':
        if request.form['name']:
            editedSport.name = request.form['name']
            session.add(editedSport)
            session.commit()
            flash('Sport Successfully Edited %s' % editedSport.name)
            return redirect(url_for('showSports'))
    else:
        return render_template('editSport.html', sport=editedSport)


# Delete a sport
@app.route('/sport/<int:sport_id>/delete/', methods=['GET', 'POST'])
def deleteSport(sport_id):
    engine = create_engine('sqlite:///sportscatalog.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    editedSport = session.query(
        Sport).filter_by(id=sport_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedSport.username != login_session['username']:
        return ("""<script>function unauthorized()
                {alert('You are unauthorized to make this action.')}
                </script><body onload='unauthorized()'>""")
    sportToDelete = session.query(
        Sport).filter_by(id=sport_id).one()
    if request.method == 'POST':
        session.delete(sportToDelete)
        flash('%s Successfully Deleted' % sportToDelete.name)
        session.commit()
        return redirect(url_for('showSports', sport_id=sport_id))
    else:
        return render_template('deleteSport.html', sport=sportToDelete)


# Show a sport item
@app.route('/sport/<int:sport_id>/')
@app.route('/sport/<int:sport_id>/item/')
def showSport(sport_id):
    engine = create_engine('sqlite:///sportscatalog.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    sport = session.query(Sport).filter_by(id=sport_id).one()
    items = session.query(Item).filter_by(
        sport_id=sport_id).all()
    return render_template('sport.html', items=items, sport=sport)


# Create a new item item
@app.route('/sport/<int:sport_id>/item/new/', methods=['GET', 'POST'])
def newItem(sport_id):
    engine = create_engine('sqlite:///sportscatalog.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    editedSport = session.query(
        Sport).filter_by(id=sport_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedSport.username != login_session['username']:
        return ("""<script>function unauthorized()
                {alert('You are unauthorized to make this action.')}
                </script><body onload='unauthorized()'>""")
    sport = session.query(Sport).filter_by(id=sport_id).one()
    if request.method == 'POST':
        newItem = Item(name=request.form['name'], description=request.form[
                           'description'], sport_id=sport_id)
        session.add(newItem)
        session.commit()
        flash('New Sport %s Item Successfully Created' % (newItem.name))
        return redirect(url_for('showSport', sport_id=sport_id))
    else:
        return render_template('newsportitem.html', sport_id=sport_id)


# Edit a item item
@app.route('/sport/<int:sport_id>/item/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(sport_id, item_id):
    engine = create_engine('sqlite:///sportscatalog.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    editedSport = session.query(
        Sport).filter_by(id=sport_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedSport.username != login_session['username']:
        return ("""<script>function unauthorized()
                {alert('You are unauthorized to make this action.')}
                </script><body onload='unauthorized()'>""")
    editedItem = session.query(Item).filter_by(id=item_id).one()
    sport = session.query(Sport).filter_by(id=sport_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        flash('Sport Item Successfully Edited')
        return redirect(url_for('showSport', sport_id=sport_id))
    else:
        return render_template('editsportitem.html', sport_id=sport_id,
                               item_id=item_id, item=editedItem)


# Delete a item item
@app.route('/sport/<int:sport_id>/item/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(sport_id, item_id):
    engine = create_engine('sqlite:///sportscatalog.db')
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    editedSport = session.query(
        Sport).filter_by(id=sport_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedSport.username != login_session['username']:
        return ("""<script>function unauthorized()
                {alert('You are unauthorized to make this action.')}
                </script><body onload='unauthorized()'>""")
    sport = session.query(Sport).filter_by(id=sport_id).one()
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Sport Item Successfully Deleted')
        return redirect(url_for('showSport', sport_id=sport_id))
    else:
        return render_template('deleteItem.html', item=itemToDelete)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
