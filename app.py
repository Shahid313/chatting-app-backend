from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from sqlalchemy import text
from werkzeug.utils import secure_filename
import os
import socket
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/chatting_app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma= Marshmallow(app)
Migrate(app,db)

app.app_context().push()

def save_file(file, type):
    file_name = secure_filename(file.filename)
    file_ext = file_name.split(".")[1]
    folder = os.path.join(app.root_path, "static/" + type + "/")
    file_path = os.path.join(folder, file_name)
    try:
        file.save(file_path)
        return True, file_name
    except:
        return False, file_name

class Users(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(100),nullable=False) 
    password = db.Column(db.String(200),nullable=False)
    name = db.Column(db.String(100))
    profile_image = db.Column(db.String(100))


class UsersSchema(ma.Schema):
    class Meta:
        fields = ('id','name','email','password', 'profile_image')

user_schema = UsersSchema()
users_schema = UsersSchema(many=True)

class Rooms(db.Model):
    room_id = db.Column(db.Integer(), primary_key=True)
    room_name = db.Column(db.String(100),nullable=False) 
    created_by = db.Column(db.ForeignKey('users.id'),nullable=False)
   
class RoomsSchema(ma.Schema):
    class Meta:
        fields = ('room_id','room_name','created_by')

class RoomMessages(db.Model):
    room_message_id = db.Column(db.Integer(), primary_key=True)
    room_id = db.Column(db.ForeignKey('rooms.room_id'),nullable=False) 
    msg_by = db.Column(db.ForeignKey('users.id'),nullable=False)
    message = db.Column(db.String(1000))
    profile_image = db.Column(db.String(100))

class RoomMessagesSchema(ma.Schema):
    class Meta:
        fields = ('room_message_id','room_id','msg_by','message','id','name','is_favorite','my_message','profile_image')

class Messages(db.Model):
    message_id = db.Column(db.Integer(), primary_key=True)
    reciever = db.Column(db.Integer,db.ForeignKey('users.id',ondelete='CASCADE'))
    sended_by = db.Column(db.Integer,db.ForeignKey('users.id',ondelete='CASCADE'))
    message = db.Column(db.String(1000))
    profile_image = db.Column(db.String(100))
class MessagesSchema(ma.Schema):
    class Meta:
        fields = ('message_id','reciever','sended_by','message','my_message','name','is_favorite','id','profile_image')



class FavoriteMessages(db.Model):
    favorite_id = db.Column(db.Integer(), primary_key=True)
    favorite_message_id = db.Column(db.ForeignKey('messages.message_id'),nullable=False)
    favorite_by = db.Column(db.ForeignKey('users.id'),nullable=False)

class FavoriteMessagesSchema(ma.Schema):
    class Meta:
        fields = ('favorite_id','favorite_message_id','favorite_by','message','name')


class RoomFavoriteMessages(db.Model):
    room_favorite_id = db.Column(db.Integer(),primary_key=True)
    room_favorite_message_id = db.Column(db.ForeignKey('room_messages.room_message_id'),nullable=False)

    favorite_by = db.Column(db.ForeignKey('users.id'),nullable=False)
class RoomFavoriteMessagesSchema(ma.Schema):
    class Meta:
        fields = ('room_favorite_id','room_favorite_message_id','favorite_by','message','name')
   


@app.route('/register_user',methods=['POST'])
def Register():
    email = request.form.get('email')
    
    name = request.form.get('name')
    password = request.form.get("password")
    profile_image = request.files.get("profile_image")
  
   
    hash_password = generate_password_hash(password)
   
    check_email_exist = Users.query.filter_by(email=email).first()

    if check_email_exist:
        return jsonify({'is_registered':0})
    else:
        isSaved, file_name = save_file(profile_image,"uploads")
        user = Users(name=name,password=hash_password,email=email, profile_image=file_name)
      
        db.session.add(user)
        db.session.commit()
        return jsonify({'is_registered':1})


@app.route('/login_user',methods=['POST'])
def Login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = Users.query.filter_by(email=email).first()

    if user and check_password_hash(user.password,password):
        user_schema = UsersSchema()
        user_info = user_schema.dump(user)
        return jsonify({'is_loggedin':1,'user':user_info})
    else:
        return jsonify({'is_loggedin':0})


@app.route('/favorite_or_unfavorite_message',methods=['POST'])
def FavoriteOrUnfavoriteMessage():
    user_id = request.form.get('user_id')
    msg_id = request.form.get('msg_id')
    print(user_id)
    print(msg_id)

    check = FavoriteMessages.query.filter_by(favorite_by=user_id,favorite_message_id=msg_id).first()

    if check:
        db.session.delete(check)
        db.session.commit()
    else:
        new_favorite = FavoriteMessages(favorite_by=user_id,favorite_message_id=msg_id)
        db.session.add(new_favorite)
        db.session.commit()


    return jsonify({
        "status":"success"
    })


@app.route('/favorite_or_unfavorite_room_message',methods=['POST'])
def FavoriteOrUnfavoriteRoomMessage():
    user_id = request.form.get('user_id')
    msg_id = request.form.get('msg_id')
    print(user_id)
    print(msg_id)

    check = RoomFavoriteMessages.query.filter_by(favorite_by=user_id,room_favorite_message_id=msg_id).first()

    if check:
        db.session.delete(check)
        db.session.commit()
    else:
        new_favorite = RoomFavoriteMessages(favorite_by=user_id,room_favorite_message_id=msg_id)
        db.session.add(new_favorite)
        db.session.commit()


    return jsonify({
        "status":"success"
    })

@app.route('/unfavorite_message',methods=['POST'])
def UnfavoriteMessage():
    favorite_id = request.form.get('favorite_id')
    favorite = FavoriteMessages.query.filter_by(favorite_id=favorite_id).first()
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({
        "status":"success"
    })

@app.route('/unfavorite_room_message',methods=['POST'])
def UnfavoriteRoomMessage():
    favorite_id = request.form.get('favorite_id')
    favorite = RoomFavoriteMessages.query.filter_by(room_favorite_id=favorite_id).first()
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({
        "status":"success"
    })



@app.route('/get_favorite_msgs')
def GetFavoriteMsgs():
    user_id = request.args.get('user_id')
  
    msgs_query = text("SELECT * FROM favorite_messages LEFT JOIN messages on messages.message_id=favorite_messages.favorite_message_id WHERE favorite_by="+str(user_id))
    msg_engine = db.engine.execute(msgs_query)
    
    
    schema = FavoriteMessagesSchema(many=True)
    msgs = schema.dump(msg_engine)
  
    print(msgs)
    return jsonify({
        "status": "success",
        "data": msgs,
       
    })

@app.route('/get_room_favorite_msgs')
def GetRoomFavoriteMsgs():
    user_id = request.args.get('user_id')
    room_messages_query = text("SELECT * FROM room_favorite_messages LEFT JOIN room_messages on room_messages.room_message_id=room_favorite_messages.room_favorite_message_id  WHERE favorite_by="+str(user_id))
    room_messages_engine =db.engine.execute(room_messages_query)

    schema = RoomFavoriteMessagesSchema(many=True)
    msgs = schema.dump(room_messages_engine)
    print(msgs)
    return jsonify({
        "data":msgs
    })

@app.route('/insert_message', methods=['POST'])
def InsertMessage():
    user_id = request.form.get('user_id')
    my_id = request.form.get('my_id')
    msg = request.form.get('msg')
    user = Users.query.filter_by(id=my_id).first()
    result = user_schema.dump(user)
    new_msg = Messages(sended_by=my_id,reciever=user_id,message=msg, profile_image=result['profile_image'])
    db.session.add(new_msg)
    db.session.commit()
    return jsonify({
        "status": "success"
    })

@app.route('/insert_room_message', methods=['POST'])
def InsertRoomMessage():
    user_id = request.form.get('user_id')
    msg = request.form.get('msg')
    room_id = request.form.get('room_id')
    user = Users.query.filter_by(id=user_id).first()
    result = user_schema.dump(user)
    new_message = RoomMessages(room_id=room_id, message=msg,msg_by=user_id, profile_image=result['profile_image'])
    db.session.add(new_message)
    db.session.commit()
    return jsonify({
        "status": "success"
    })

@app.route('/add_room',methods=['POST'])
def AddGroup():
    room_name = request.form.get('room_name')
    user_id = request.form.get('user_id')
    new_room = Rooms(room_name=room_name,created_by=user_id)
    db.session.add(new_room)
    db.session.commit()
    return jsonify({
        "status":"success"
    })

@app.route('/get_room_messages')
def GetRoomMessages():
    room_id = request.args.get('room_id')
    user_id = request.args.get('user_id')
    msgs_query = text("SELECT *,(SELECT count(*) FROM room_favorite_messages WHERE room_favorite_messages.room_favorite_message_id=room_messages.room_message_id AND room_favorite_messages.favorite_by="+str(user_id)+") as is_favorite FROM room_messages LEFT JOIN users on users.id=room_messages.msg_by  WHERE room_id="+str(room_id))
    engine = db.engine.execute(msgs_query)
    schema = RoomMessagesSchema(many=True)
    msgs = schema.dump(engine)
    return jsonify({
        "status": "success",
        "data": msgs
    })

@app.route('/get_messages')
def GetMessages():
    user_id = request.args.get('user_id')
    my_id = request.args.get('my_id')
    get_msg_sql = text("SELECT *,(SELECT count(*) FROM favorite_messages WHERE favorite_messages.favorite_message_id=messages.message_id AND favorite_messages.favorite_by="+str(user_id)+") as is_favorite FROM messages LEFT JOIN users on id=messages.sended_by  WHERE  (reciever="+str(my_id)+" AND sended_by="+str(user_id)+") OR (reciever="+str(user_id)+" AND sended_by="+str(my_id)+")")
    get_msg_query = db.engine.execute(get_msg_sql)
    msgSchema = MessagesSchema(many=True)
    msgs = msgSchema.dump(get_msg_query)
    return jsonify({
        "data":msgs,
        "status":"success"
    })

@app.route('/get_all_rooms')
def GetAllRooms():
    all_Rooms_query = Rooms.query.all()
    schema = RoomsSchema(many=True)
    all_Rooms = schema.dump(all_Rooms_query)
    return jsonify({
        "status":"success",
        "data":all_Rooms
    })


@app.route('/get_users')
def GetUsers():
    my_id = request.args.get('my_id')
    users_query = Users.query.filter(Users.id != my_id).all()
    schema = UsersSchema(many=True)
    users = schema.dump(users_query)
    return jsonify({
        "status":"success",
        "data":users
    })



## getting the hostname by socket.gethostname() method
hostname = socket.gethostname()
## getting the IP address using socket.gethostbyname() method
ip_address = socket.gethostbyname(hostname)

if __name__ == '__main__':
    app.run(host=ip_address,debug=True)