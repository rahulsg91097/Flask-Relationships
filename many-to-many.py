from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///manyRelationship.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/flask_relation_db'

db = SQLAlchemy(app)

# Define the user_role table before the User class
user_role = db.Table('user_role',
                      db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                      db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
                      )

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    profile = db.relationship('Profile', uselist=False, back_populates='user')
    posts = db.relationship("Post", backref="author", lazy=True)
    roles = db.relationship('Role', backref="user", secondary=user_role)

# one to one
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bio = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    user = db.relationship('User', uselist=False, back_populates='profile')


# one to many
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# many to many
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)


with app.app_context():
    # db.drop_all()
    db.create_all()


@app.route('/post-add')
def addPost():
    user = User.query.get(2)
    posts = [
        Post(title='My motto1', description="I am going to be king of the pirates!!!", author=user),
        Post(title='My motto2', description="I am going to be king of the pirates!!!", author=user),
        Post(title='My motto3', description="I am going to be king of the pirates!!!", author=user)
    ]
    for post in posts:
        db.session.add(post)

    db.session.add(post)
    db.session.commit()
    return jsonify({'message': 'Post added Successfully'})


@app.route('/posts')
def getPosts():
    posts = Post.query.all()
    post_list = []
    for post in posts:
        post_data = {
            'id': post.id,
            'title': post.title,
            'description': post.description,
            'author': post.author.name
        }
        post_list.append(post_data)

    return jsonify(post_list)


@app.route('/user-add')
def addUser():
    user = User(name='Luffy')
    profile = Profile(bio='Pirate King')

    roles = [
        Role(name="Captain"),
        Role(name="Admin"),
        Role(name="User")
    ]
    for role in roles:
        user.roles.append(role)

    user.profile = profile
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User added Successfully'})

@app.route('/users')
def getUser():
    users = User.query.all()
    user_list = []
    for user in users:
        user_data = {
            'id': user.id,
            'name': user.name,
            'bio': user.profile.bio,
            'roles': [],
            'posts': []
        }
        for post in user.posts:
            post_data = {
                'title':post.title,
                'description':post.description,
            }
            user_data['posts'].append(post_data)


        for role in user.roles:
            role_data = {
                'name':role.name,
            }
            user_data['roles'].append(role_data)

        user_list.append(user_data)

    return jsonify(user_list)

@app.route('/profiles')
def getProfiles():
    profiles = Profile.query.all()
    profile_list = []
    for profile in profiles:
        profile_data = {
            'id': profile.id,
            'bio': profile.bio,
            'user_name': profile.user.name
        }
        profile_list.append(profile_data)

    return jsonify(profile_list)

@app.route('/roles')
def getRoles():
    roles = Role.query.all()
    role_list = []
    for role in roles:
        role_data = {
            'id': role.id,
            'name': role.name,
            'users': []
        }

        for user in role.user:
            user_data = {
                'name': user.name,
            }
            role_data['users'].append(user_data)
        role_list.append(role_data)
    return jsonify(role_list)




@app.route('/')
def index():
    return jsonify({"message": "Home page"})

if __name__ == "__main__":
    app.run(debug=True)