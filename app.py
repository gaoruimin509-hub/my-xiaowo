from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

from flask import request, Response
from functools import wraps

def check_auth(username, password):
    return username == 'GG' and password == '0627'

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        import os
        if os.environ.get('IS_PRIVATE') == 'true':
            auth = request.authorization
            if not auth or not check_auth(auth.username, auth.password):
                return Response(
                    '需要密码才能进入哦！', 401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'}
                )
        return f(*args, **kwargs)
    return decorated
    
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(
        db.String(500),
        nullable=False
    )

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    read = db.Column(
        db.Boolean,
        default=False
    )


with app.app_context():
    db.create_all()


@app.route('/')
@requires_auth
def index():
    messages = (
        Message.query
        .order_by(Message.timestamp.desc())
        .limit(100)
        .all()
    )
    return render_template(
        'index.html',
        messages=messages
    )


@app.route('/')
@requires_auth
def index():
    return render_template('index.html')

@app.route('/post', methods=['POST'])
def post():

    data = request.json

    content = data.get('content', '').strip()

    if not content:
        return jsonify({
            "success": False
        })

    msg = Message(
        content=content
    )

    db.session.add(msg)
    db.session.commit()

    return jsonify({
        "success": True
    })


@app.route('/read/<int:id>', methods=['POST'])
def mark_read(id):

    msg = Message.query.get_or_404(id)

    msg.read = True

    db.session.commit()

    return jsonify({
        "success": True
    })


app.run(host='0.0.0.0', port=10000, debug=True)
