from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

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


if __name__ == '__main__':
    app.run(debug=True)