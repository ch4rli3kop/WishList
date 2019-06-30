#!/usr/bin/python3
from flask import Flask, url_for, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'TESTKEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __table_name__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    notes = db.relationship('Note', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Note(db.Model):
    __table_name__ = 'note'
    id = db.Column(db.Integer, primary_key=True)
    summary = db.Column(db.String(30), nullable=False)
    detail = db.Column(db.String(200), nullable=True)
    category = db.Column(db.Integer, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


@app.route('/', methods=['GET', 'POST'])
def home():
    if session.get('logged_in'):
        resp_note = Note.query.filter_by(user_id=session.get('user_id')).all()
        print('return note test')
        print(dir(resp_note[0]))
        # print(resp_note[0])
        return render_template('home.html', notes=resp_note, isLogin=True)

    print('Dummy Context!')
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        new_user = User(username=request.form['username'], password=request.form['password'])
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        resp = User.query.filter_by(username=username, password=password).first()
        if resp is not None:
            session.clear()
            session['user_id'] = resp.id
            session['logged_in'] = True
            print(dir(session))
            print(session)
            return redirect(url_for('home'))
        else:
            error = 'Incorrect ID or Password!'
            flash(error)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    if request.method == 'POST':
        print('add request')
        print(dir(request))
        print(request.form['summary'])
        print(request.form['detail'])
        new_note = Note(
            summary = request.form['summary'],
            detail = request.form['detail'],
            category = id,
            user_id = session['user_id']
        )
        db.session.add(new_note)
        db.session.commit()
        return redirect(url_for('home'))

@app.route('/delete/<int:id>')
def delete(id):
    note = Note.query.filter_by(user_id=session['user_id'], id=id).first()
    if not note is None:
        print(note)
        db.session.delete(note)
        db.session.commit()
    print('delete' + str(id))
    return redirect(url_for('home'))

if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', port=5000 ,debug=True)