import telebot
import string
import random
import urllib.request
import os.path
from hashlib import sha256
from flask import Flask, render_template, session, redirect, url_for, escape, request, jsonify

from settings import *
from belkaBot.logic.user import User
from belkaBot.logic.event import Event

hash_for_users = {}

bot = telebot.TeleBot(TOKEN)

web = Flask(__name__)

web.secret_key = WEBSECRET
web.config['SESSION_TYPE'] = 'memcache'


def render_main_page(username):
    data = {}
    try:
        total_users = len(User.all_user())
    except:
        total_users = 0
    try:
        total_events = len(Event.all_event())
    except:
        total_events = 0
    data['total_users'] = total_users
    data['total_events'] = total_events
    data['username'] = username
    return render_template('index.html', data=data)


@web.route('/login')
def login():
    if 'username' in session:
        return index()
    return render_template('login.html')


@web.route('/login2', methods=['GET', 'POST'])
def login2():
    global hash_for_users
    if request.method == 'POST':
        if request.form['username']:
            cuser = User.get_user('username', f"{request.form['username']}")
            if cuser:
                if cuser.is_staff:
                    char_set = string.ascii_letters + string.digits
                    hash = sha256((''.join(random.sample(char_set * 100, 256))).encode("utf-8")).hexdigest()
                    hash_for_users[cuser.chat_id] = hash
                    bot.send_message(chat_id=cuser.chat_id, text=f'your key: {hash}')
                    return render_template('login2.html',username=f"{cuser.username}")
    return redirect(url_for('login'))


@web.route('/logout')
def logout():
    session.clear()
    return login()


@web.route('/', methods=['GET', 'POST'])
def index():
    global hash_for_users
    if request.method == 'POST':
        if request.form['username']:
            cuser = User.get_user('username', f"{request.form['username']}")
            if cuser:
                if (cuser.chat_id in hash_for_users and hash_for_users[cuser.chat_id] == request.form['rcode']
                        and hash_for_users[cuser.chat_id]):
                    bot.send_message(chat_id=cuser.chat_id, text=f'success')
                    session['username'] = request.form['username']
                    hash_for_users[cuser.chat_id] = None
                    return render_main_page(cuser.username)
        return redirect(url_for('login'), code=302)
    
    if request.method == 'GET':
        if 'username' in session:
            cuser = User.get_user('username',session['username'])
            if cuser:
                if not os.path.isfile(f'./static/img/avatar/{cuser.username}.png'):
                    avatar = bot.get_user_profile_photos(cuser.chat_id, limit=1)
                    avatar_path = bot.get_file(avatar.photos[0][0].file_id).file_path
                    urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{bot.token}/{avatar_path}',
                                               f'./static/img/avatar/{cuser.username}.png')
                    session['username'] = None
                return render_main_page(cuser.username)
            return redirect(url_for('login'))
        else:
            return redirect(url_for('login'), code=302)


@web.route('/users')
def users():
    users = User.all_user()
    if 'username' in session:
        cuser = User.get_user('username', session['username'])
        if cuser:
            return render_template('users.html', username=f'{cuser.username}', users=users)
    return redirect(url_for('login'))


@web.route('/events')
def events():
    if 'username' in session:
        cuser = User.get_user('username', session['username'])
        if cuser:
            events = Event.all_event()
            return render_template('events.html', username=f'{cuser.username}', events=events)
    return redirect(url_for('login'))


@web.route('/eventAdd')
def eventAdd():
    if 'username' in session:
        cuser = User.get_user('username', session['username'])
        if cuser:
            return render_template('eventAdd.html', data={'username': f'{cuser.username}', "error": ''})
    return redirect(url_for('login'))


@web.route('/eventEdit/(PK<pk>)', methods=["GET", ])
def eventEdit(pk):
    if 'username' in session:
        cuser = User.get_user('username', session['username'])
        if cuser:
            return render_template('eventEdit.html', username=f'{cuser.username}')
    return redirect(url_for('login'))


@web.route('/eventDelete')
def eventDelete():
    if 'username' in session:
        cuser = User.get_user('username', session['username'])
        if cuser:
            return render_template('eventDelete.html', username=f'{cuser.username}')
    return redirect(url_for('login'))


@web.route('/sendtoall', methods=['GET', 'POST'])
def sendtoall():
    if request.method == 'POST':
        if request.form['text']:
            users = User.all_user()
            for user in users:
                bot.send_message(user.chat_id, f"{request.form['text']}")
    if 'username' in session:
        cuser = User.get_user('username', session['username'])
        if (cuser != None):
            return render_template('sendtoall.html', username=f'{cuser.username}')
    return redirect(url_for('login'))
###############
# API Methods #
###############


@web.route('/api/UserAddStaff', methods=['GET', 'POST'])
def ApiUserAddStaff():
    if request.method == 'GET':
        users = User.all_user()
        if 'username' in session:
            cuser = User.get_user('username', session['username'])
            if cuser:
                for user in users:
                    if f"{user.chat_id}" == f"{request.args.get('chat_id')}":
                        user.is_staff = 1
                        user.update()
                return "ok"
    return redirect(url_for('login'))


@web.route('/api/UserDelStaff', methods=['GET', 'POST'])
def ApiUserDelStaff():
    if request.method == 'GET':
        users = User.all_user()
        if 'username' in session:
            cuser = User.get_user('username', session['username'])
            if cuser:
                for user in users:
                    if f"{user.chat_id}" == f"{request.args.get('chat_id')}":
                        user.is_staff = 0
                        user.update()
                return "ok"
    return redirect(url_for('login'))


@web.route('/api/UserDelete', methods=['GET'])
def ApiUserDelete():
    if request.method == 'GET':
        users = User.all_user()
        if 'username' in session:
            cuser = User.get_user('username', session['username'])
            if cuser:
                for user in users:
                    if f"{user.chat_id}" == f"{request.args.get('chat_id')}":
                        user.delete_user()
    return redirect(url_for('login'))


@web.route('/api/EventAddNew', methods=['POST'])
def ApiEventAddNew():
    if request.method == 'POST':
        users = User.all_user()
        if 'username' in session:
            cuser = User.get_user('username', session['username'])
            if cuser:
                if not (request.form['title']
                        or not request.form['description']
                        or not request.form['image']
                        or not request.form['date']
                        or not request.form['time']
                        or not request.form['descriptionshort']
                        ):
                    # TODO: download and upload image
                    Event.create_event(request.form['title'],
                                       request.form['description'],
                                       request.form['image'],
                                       request.form['date'].replace('.', '-'),
                                       request.form['time'],
                                       request.form['descriptionshort'])
                else:
                    return render_template('eventAdd.html',
                                           data={"username": f'{cuser.username}',
                                                 "error": 'All field must be zapolneni blyat!'})

    return redirect(url_for('login'))


@web.route('/api/EventDelete', methods=['GET'])
def ApiEventDelete():
    if request.method == 'GET':
        users = User.all_user()
        if 'username' in session:
            cuser = User.get_user('username', session['username'])
            if cuser:
                event = Event.get_event('id', f"{request.args.get('id')}")
                event.delete_event()
    return redirect(url_for('login'))


@web.route('/api/EventEdit', methods=['GET'])
def ApiEventEdit():
    if request.method == 'POST':
        users = User.all_user()
        if 'username' in session:
            cuser = User.get_user('username', session['username'])
            if cuser:
                if not (request.form['title']
                        or not request.form['description']
                        or not request.form['image']
                        or not request.form['date']
                        or not request.form['time']
                        or not request.form['descriptionshort']
                        ):
                    event = Event.get_event('id', f"{request.args.get('id')}")
                    event.name = request.form['name']
                    event.title = request.form['title']
                    event.description = request.form['description']
                    event.shortdescription = request.form['shortdescription']
                    event.photo = request.form['image']
                    event.date = request.form['date']
                    event.time = request.form['time']
                    event.update()

    return redirect(url_for('login'))

web.run(debug=False, host='0.0.0.0', port=5000)