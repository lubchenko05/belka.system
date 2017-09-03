import telebot
import string
import random
import urllib.request
import os.path
from hashlib import sha256
from flask import Flask, render_template, session, redirect, url_for, escape, request, jsonify


from logic.user import User
from logic.event import Event

global hashs_for_users
hashs_for_users = {}

TOKEN = '386962862:AAEJu5utZL-herHkyxVyVa9_YyNkf3bLMvo'

bot = telebot.TeleBot(TOKEN)

web = Flask(__name__)

web.secret_key = '6579af11e0922f02be35da90481274b93fc9b26c6c8a9602f34c6437'
web.config['SESSION_TYPE'] = 'memcache'

def render_main_page(username):
    data = {}
    try:
        total_users = len(User.all_user());
    except:
        total_users = 0
    try:
        total_events = len(Event.all_event());
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
    global hashs_for_users
    if request.method == 'POST':
        if (request.form['username'] != None ):
            cuser = User.get_user('username', f"{request.form['username']}")
            if (cuser != None):
                if (cuser.is_staff == True):
                    char_set = string.ascii_letters + string.digits;
                    hash = sha256((''.join(random.sample(char_set * 100, 256))).encode("utf-8")).hexdigest()
                    hashs_for_users[cuser.chat_id]= hash
                    bot.send_message(chat_id=cuser.chat_id, text=f'your key: {hash}')
                    return render_template('login2.html',username=f"{cuser.username}")
    return redirect(url_for('login'))

@web.route('/logout')
def logout():
    session.clear()
    return login()

@web.route('/', methods=['GET', 'POST'])
def index():
    global hashs_for_users
    if request.method == 'POST':
        if ((request.form['username'] != None)):
            cuser = User.get_user('username', f"{request.form['username']}")
            if (cuser != None):
                if ((hashs_for_users[cuser.chat_id] == request.form['rcode']) & (hashs_for_users[cuser.chat_id] != None) & (hashs_for_users[cuser.chat_id] != '')):
                    bot.send_message(chat_id=cuser.chat_id, text=f'success')
                    session['username'] = request.form['username']
                    hashs_for_users[cuser.chat_id] = None
                    return render_main_page(cuser.username)
        return redirect(url_for('login'), code=302)
    
    if request.method == 'GET':
        if 'username' in session:
            cuser = User.get_user('username',session['username'])
            if (cuser != None):
                if not os.path.isfile(f'./static/img/avatar/{cuser.username}.png'):
                    avatar = bot.get_user_profile_photos(cuser.chat_id, limit=1)
                    avatar_path = bot.get_file(avatar.photos[0][0].file_id).file_path
                    urllib.request.urlretrieve('https://api.telegram.org/file/bot{0}/{1}'.format(bot.token, avatar_path), f'./static/img/avatar/{cuser.username}.png')
                return render_main_page(cuser.username)
            return redirect(url_for('login'))
            session['username'] = None
        else:
            return redirect(url_for('login'),code=302)

@web.route('/users')
def users():
    users = User.all_user()
    if 'username' in session:
        cuser = User.get_user('username', session['username'])
        if (cuser != None):
            return render_template('users.html',username=f'{cuser.username}',users = users)
    return redirect(url_for('login'))

@web.route('/events')
def events():
    if 'username' in session:
        cuser = User.get_user('username', session['username'])
        if (cuser != None):
            events = Event.all_event()
            return render_template('events.html',username=f'{cuser.username}', events=events)
    return redirect(url_for('login'))

@web.route('/eventAdd')
def eventAdd():
    if 'username' in session:
        cuser = User.get_user('username', session['username'])
        if (cuser != None):
            return render_template('eventAdd.html',username=f'{cuser.username}')
    return redirect(url_for('login'))

@web.route('/sendtoall', methods=['GET', 'POST'])
def sendtoall():
    if request.method == 'POST':
        if (request.form['text'] != None):
            users = User.all_user()
            for user in users:
                bot.send_message(user.chat_id, f"{request.form['text']}")
    if 'username' in session:
        cuser = User.get_user('username', session['username'])
        if (cuser != None):
            return render_template('sendtoall.html',username=f'{cuser.username}')
    return redirect(url_for('login'))

###############
# API Methods #
###############
@web.route('/UserAddStaff', methods=['GET', 'POST'])
def UserAddStaff():
    if request.method == 'GET':
        users = User.all_user()
        if 'username' in session:
            cuser = User.get_user('username', session['username'])
            if (cuser != None):
                for user in users:
                    if (f"{user.chat_id}" == f"{request.args.get('chat_id')}"):
                        user.is_staff = 1
                        user.update()
                return "ok"
    return redirect(url_for('login'))

@web.route('/UserDelStaff', methods=['GET', 'POST'])
def UserDelStaff():
    if request.method == 'GET':
        users = User.all_user()
        if 'username' in session:
            cuser = User.get_user('username', session['username'])
            if (cuser != None):
                for user in users:
                    if (f"{user.chat_id}" == f"{request.args.get('chat_id')}"):
                        user.is_staff = 0
                        user.update()
                return "ok"
    return redirect(url_for('login'))

@web.route('/UserDelete', methods=['GET'])
def UserDelete():
    if request.method == 'GET':
        users = User.all_user()
        if 'username' in session:
            cuser = User.get_user('username', session['username'])
            if (cuser != None):
                for user in users:
                    if (f"{user.chat_id}" == f"{request.args.get('chat_id')}"):
                        user.delete_user()
    return redirect(url_for('login'))

@web.route('/EventAddNew', methods=['POST'])
def EventAddNew():
    if request.method == 'POST':
        users = User.all_user()
        if 'username' in session:
            cuser = User.get_user('username', session['username'])
            if (cuser != None):
                events = Event.all_event()
                for event in events:
                    if (f"{event._id}" == f"{request.args.get('id')}"):
                        event.delete_event()
    return redirect(url_for('login'))

@web.route('/EventDelete', methods=['GET'])
def EventDelete():
    if request.method == 'GET':
        users = User.all_user()
        if 'username' in session:
            cuser = User.get_user('username', session['username'])
            if (cuser != None):
                events = Event.all_event()
                for event in events:
                    if (f"{event._id}" == f"{request.args.get('id')}"):
                        event.delete_event()
    return redirect(url_for('login'))

web.run(debug=False, host='0.0.0.0',port=5000)