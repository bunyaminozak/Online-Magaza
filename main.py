import ast
import itertools
import math
import pickle
from operator import attrgetter
from markupsafe import Markup
from sqlalchemy import or_
from datetime import datetime
import json
from flask_socketio import SocketIO, join_room, leave_room, emit
from jinja2 import Environment
from sqlalchemy import text
import xml.etree.ElementTree as ET
import requests
from flask import Flask,session, render_template, request, url_for, redirect, flash, send_from_directory, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import base64
from flask import Flask, request
from flask_migrate import Migrate
from flask_ckeditor import CKEditor,CKEditorField
from wtforms import SubmitField
from wtforms.validators import DataRequired,Email,Length,InputRequired
from flask_wtf import FlaskForm

from werkzeug.utils import secure_filename
import os
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import LargeBinary

from flask_bootstrap import Bootstrap



app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CKEDITOR_PKG_TYPE'] = 'basic '


ckeditor = CKEditor(app)

bootstrap = Bootstrap(app)


db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
socketio = SocketIO(app)

env = Environment()

# Register the custom filter

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    parent = db.relationship('Category', remote_side=[id], backref=db.backref('children', lazy='dynamic'))
    posts = db.relationship('Post', backref='category', lazy='dynamic')

class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    posts = db.relationship('Post', back_populates='user')



    def __repr__(self):
        return '<User %r>' % self.name





class Post(db.Model):
    __tablename__ = 'Posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=True, server_default=text('NULL'))
    content = db.Column(db.Text, nullable=True, server_default=text('NULL'))
    images = db.relationship('Image', backref='post', lazy=True)
    state = db.Column(db.String(50), nullable=True, server_default=text('NULL'))
    price = db.Column(db.Integer, nullable=True, server_default=text('NULL'))
    para_birim = db.Column(db.Text, nullable=True, server_default=text('NULL'))
    takas_kategori = db.Column(db.Text, nullable=True, server_default=text('NULL'))

    year = db.Column(db.Integer, nullable=True, server_default=text('NULL'))
    sale_type = db.Column(db.String(50), nullable=True, server_default=text('NULL'))
    release_date = db.Column(db.String(50), nullable=True, server_default=text('NULL'))
    ilçe = db.Column(db.String(50), nullable=True, server_default=text('NULL'))
    city = db.Column(db.String(50), nullable=True, server_default=text('NULL'))

    # telefon
    marka = db.Column(db.String(50), nullable=True, server_default=text('NULL'))
    model = db.Column(db.String(50), nullable=True, server_default=text('NULL'))

    hafıza = db.Column(db.String(50), nullable=True, server_default=text('NULL'))
    ekran = db.Column(db.String(50), nullable=True, server_default=text('NULL'))
    ram = db.Column(db.Integer, nullable=True, server_default=text('NULL'))
    kamera = db.Column(db.String(50), nullable=True, server_default=text('NULL'))
    ön_kamera = db.Column(db.String(50), nullable=True, server_default=text('NULL'))
    renk = db.Column(db.String(50), nullable=True, server_default=text('NULL'))
    garanti = db.Column(db.String(50), nullable=True, server_default=text('NULL'))  # Seçim li yap

    # vasıta
    yıl = db.Column(db.Integer, nullable=True, server_default=text('NULL'))
    km = db.Column(db.Integer, nullable=True, server_default=text('NULL'))
    motor_hacmi = db.Column(db.String(50), nullable=True, server_default=text('NULL'))
    hp = db.Column(db.Integer, nullable=True, server_default=text('NULL'))
    vites = db.Column(db.String(50), nullable=True, server_default=text('NULL'))  # Seçim li yap
    yakıt = db.Column(db.String(50), nullable=True, server_default=text('NULL'))
    ağır_hasar = db.Column(db.String(50), nullable=True, server_default=text('NULL'))

    # emlak
    brüt_metre = db.Column(db.Integer, nullable=True, server_default=text('NULL'))
    net_metre = db.Column(db.Integer, nullable=True, server_default=text('NULL'))
    oda = db.Column(db.Integer, nullable=True, server_default=text('NULL'))
    yaş = db.Column(db.Integer, nullable=True, server_default=text('NULL'))
    kat = db.Column(db.Integer, nullable=True, server_default=text('NULL'))
    bina_kat_sayı = db.Column(db.Integer, nullable=True, server_default=text('NULL'))
    banyo_sayısı = db.Column(db.Integer, nullable=True, server_default=text('NULL'))
    balkon = db.Column(db.String(50), nullable=True, server_default=text('NULL'))
    eşyalı = db.Column(db.String(50), nullable=True, server_default=text('NULL'))
    site = db.Column(db.String(50), nullable=True, server_default=text('NULL'))
    aidat = db.Column(db.Integer, nullable=True, server_default=text('NULL'))
    depozito = db.Column(db.Integer, nullable=True, server_default=text('NULL'))


    pasif =  db.Column(db.Boolean, nullable=True , default=False)
    items_list = db.Column(db.Text , nullable=True)


    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, server_default=text('NULL'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False, server_default=text('NULL'))
    user = db.relationship('User', back_populates='posts')



    def __repr__(self):
        return '<Post %r>' % self.title

class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.LargeBinary, nullable=True)

    post_id = db.Column(db.Integer, db.ForeignKey('Posts.id'), nullable=True)





#Yap  Message.add(id,gönderen_user_id, ilan_sahibi_id, post_id , takas_teklifi_post_id ,mesaj)
class Message(db.Model):
    __tablename__ = 'Messages'
    id = db.Column(db.Integer , primary_key=True)
    user_id = db.Column(db.Integer , nullable=True, server_default=text('NULL'))
    to_user_id = db.Column(db.Integer , nullable=True, server_default=text('NULL'))
    post_id = db.Column(db.Integer , nullable=True, server_default=text('NULL'))
    deal_post_id = db.Column(db.Integer , nullable=True, server_default=text('NULL'))
    message = db.Column(db.Text , nullable=True, server_default=text('NULL'))
    release_date = db.Column(db.Text, nullable=True, server_default=text('NULL'))
    kabul = db.Column(db.Text, nullable=True, server_default=text('NULL'))


class Chat_Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[user_id], backref=db.backref('sent_messages', lazy=True))
    recipient = db.relationship('User', foreign_keys=[to_user_id], backref=db.backref('received_messages', lazy=True))

    def __repr__(self):
        return '<Message %r>' % self.id




with app.app_context():
    db.create_all()

class User_login:
    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id



def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

def add_messages_to_database(user_id, to_user_id, content):
    with app.app_context():
        new_message = Chat_Messages(user_id=current_user.id, to_user_id=to_user_id, content=content)
        db.session.add(new_message)
        db.session.commit()

class LoginForm(FlaskForm):
    cke = CKEditorField(validators=[DataRequired()])



body = CKEditorField(validators=[DataRequired()])


is_message= False
@app.route('/chat' , methods=['GET', 'POST'])
def sessions():
    global is_message
    session['user'] = info_default
    is_speaking = False
    to_user_id = request.form.get('to_user_id_FORM')
    to_user_id_ = request.form.get('to_user_id')

    user_id = current_user.id

    messages_history = []
    messages_history_me = []
    combined_list = []
    room=0
    if "to_user_id_FORM" in request.form:
        is_message = True

        # YAP KİŞİ SEÇİLMİŞ VE JOİN_ROOM KISMI
        # EĞER Kİ ZATEN KİŞİ SEÇİLMİŞ İSE LEAVE AND JOİN

        room = str(min(str(user_id), to_user_id)) + "-" + str(max(str(user_id), to_user_id))
        print("room", room)


        to_user_id = request.form.get('to_user_id_FORM')



        messages_history.append(Chat_Messages.query.filter_by(user_id=to_user_id,to_user_id=user_id).all())
        messages_history_me.append(Chat_Messages.query.filter_by(user_id=user_id, to_user_id=to_user_id).all())
        combined_list =  [message for pair in zip(messages_history, messages_history_me) for message in pair]

        flattened_list = [item for sublist in combined_list for item in
                          (sublist if isinstance(sublist, list) else [sublist])]

        combined_list = sorted(flattened_list, key=lambda sublist: sublist.timestamp)


    spoken_with = set()
    #Kişilerimi Bulmak

    query = db.session.query(Chat_Messages.to_user_id.distinct()).filter_by(user_id=user_id)
    results = query.all()

    query_from = db.session.query(Chat_Messages.user_id.distinct()).filter_by(to_user_id=user_id).all()
    for q in query_from:
        results.append(q)


    for result in results:
        spoken_with.add(result[0])

    spoken_with = list(spoken_with)

    kişilerim= []
    for ids in spoken_with:
        user = User.query.filter_by(id=ids).first()
        kişilerim.append(user)

    # Kişilerimi Bulmak

    if "to_user_id_FORM" not in request.form:
        is_speaking = False
    else:
        is_speaking = True

    return render_template('chat.html',kişilerim=kişilerim,room=room,is_speaking=is_speaking,user_id=current_user.id,messages_history=combined_list,current_user_id = current_user.id,to_user_id=to_user_id, is_user=is_current_user)


@app.route('/process_form', methods=['POST'])
def process_form():
    user_id_form = request.form.get('user_id_FORM')
    to_user_id_form = request.form.get('to_user_id_FORM')

    # Perform session-related operations
    session['user_id'] = user_id_form
    session['to_user_id'] = to_user_id_form

    # Continue with other processing or redirect to another page
    # ...

    return 'Form submitted successfully'





@socketio.on('join')
def on_join(data):
    print("data", data)
    if data["room"] != '0' :
        room = data["room"]  # Generate a unique room identifier
        join_room(room)
        print("katıldım : " , room)
        socketio.send(data, to=room)


@socketio.on('leave')
def on_leave(data):
    print("data", data)
    if data["room"] != '0':
        room = data["room"]  # Generate a unique room identifier
        leave_room(room)
        print("Ayrıldım : ", room)
        socketio.send(data, to=room)





@socketio.on('my event')
def handle_my_custom_event(data):
    if 'to_user_id' in data:
        print("mesaj içerik" , data)
        user_id = current_user.id
        to_user_id = data['to_user_id']
        message = data['message']
        add_messages_to_database(user_id, to_user_id, message)
        socketio.emit('my response', data, room=data["room"], callback=messageReceived)


















fake_user_id=0

@app.route('/profil',methods=['GET', 'POST']) # İlan Sahibinin Profil Sayfasını Göstermek
def profil():
    #Yap user.id Bilgilerini Profil Göstericez
    global fake_user_id
    is_user = False



    if type(current_user) != None:
        is_user = True

    if "names" in request.form:
        user_id = int(request.form.get("names"))
        fake_user_id = user_id
    else:
        user_id = fake_user_id


    user_posts = Post.query.filter(Post.user_id == user_id, or_(Post.pasif == 0, Post.pasif == "0")).all()

    user=User.query.filter_by(id=user_id).first()
    post_sayı = len(user_posts)

    a = len(user_posts) / 10
    nav_number = int(custom_round(a))
    page = 0
    if "page" in request.form:
        if int(request.form["page"]) != 1:
            page = int(request.form["page"])
            user_posts = user_posts[(page * 10) - 10:page * 10]
        else:
            user_posts = user_posts[0:10]
    else:
        user_posts = user_posts[0:10]

    take = Message.query.filter_by(to_user_id=user_id).all()
    send = Message.query.filter_by(user_id=user_id).all()

    take_number = len(take)
    send_number = len(send)




    return render_template("profil.html",page=page,nav_number=nav_number,user_posts=user_posts,current_user=current_user,is_user=is_user,user=user,post_sayı=post_sayı,take_number=take_number,send_number=send_number)







@app.route('/message-data-base',methods=['GET', 'POST']) #Kişilerime eklemek için Post kısmından Mesaj
def add_message_to_database():
    data = request.get_json()
    print("say po" , data)
    user_id=current_user.id
    to_user_id= data["to_user_id"]
    message= data["form"]

    add_messages_to_database(user_id,to_user_id,message)


    return redirect(url_for("choose_category"))

    # yap Mesajlar.add(user_id=user_id,to_user_id,message_content=message,time=release_date_find_minute()




def release_date_find():
    current_time = datetime.now()
    release_date = current_time.strftime("%Y-%m-%d")
    return release_date




is_current_user="a"

@app.template_filter('getattr')
def get_attribute(obj, attr):
    return getattr(obj, attr)

@app.template_filter('b64encode')
def base64_encode(value):
    return base64.b64encode(value).decode('utf-8')

def custom_round(number):
    decimal_part = number - int(number)
    if decimal_part != 0.0:
        return math.ceil(number)
    else:
        return number

kategori_list=[]

info_default= {
    'name': 0,
}



is_edit=False
is_şehir= False
@app.route('/' , methods=['POST' , 'GET'] )
@app.route('/<city>' , methods=['POST' , 'GET'] )
def home(city=None):
    global is_edit,is_message,is_şehir
    session['user'] = info_default
    is_message = False
    is_edit = False
    is_şehir= False
    is_search=False
    posts_by_john = Post.query.filter_by(user_id=1).all()

    şehir = 0

    all_posts = Post.query.filter(or_(Post.pasif == 0, Post.pasif == "0"))
    all_posts = all_posts.order_by(Post.release_date.desc()).all()





    if city != 'favicon.ico' and city != None:
        şehir=city
        is_şehir=True
        all_posts = Post.query.filter(Post.city == şehir, or_(Post.pasif == 0, Post.pasif == "0"))
        all_posts = all_posts.order_by(Post.release_date.desc()).all()
    if "şehir" in request.args :
        is_şehir = True
        şehir = request.args["şehir"]

        if şehir == "0":
            print("tüm türkiye" ,şehir)
            return redirect(url_for("home"))
        else:
            all_posts = Post.query.filter(Post.city == şehir, or_(Post.pasif == 0, Post.pasif == "0"))
            all_posts = all_posts.order_by(Post.release_date.desc()).all()


    a = len(all_posts) / 20
    nav_number = int(custom_round(a))
    page = 0
    if "page" in request.form:

        if int(request.form["page"]) != 1:
            page = int(request.form["page"])
            all_posts = all_posts[(page * 20) - 20:page * 20]

        else:
            all_posts = all_posts[0:20]
    else:
        all_posts = all_posts[0:20]



    global kategori_list
    kategori_list=[]

    #yap post içerisindeki null olmayan veya "" olmayan değerleri bul
    global is_current_user
    current_user_=current_user if current_user !=None else False
    is_current_user = current_user.is_authenticated

    filter = False
    search_query = request.args.get('search', default='', type=str)
    if search_query:
        filtered_posts = [post for post in all_posts if search_query.lower() in post.title.lower()]
        filter=True
        b = len(filtered_posts) / 20
        nav_number = int(custom_round(b))
        page = 0
        if "page" in request.form:

            if int(request.form["page"]) != 1:
                page = int(request.form["page"])
                filtered_posts = filtered_posts[(page * 20) - 20:page * 20]
    else:
        filter=False
        filtered_posts=all_posts



    return render_template("index.html",user=current_user_,page=page,nav_number=nav_number,is_şehir=is_şehir,şehir=şehir,is_user=is_current_user, posts=all_posts,filtered_posts=filtered_posts,filter=filter,filter_post_sayi=len(filtered_posts),search_query=search_query,is_edit=is_edit)




@app.route('/submit', methods=['POST'])
def submit():

    data = request.get_json()
    message = data.get('form')

    infos_split =data.get("post")


    infos = infos_split.split("/")

    print("aaaaaa" , data)

    #Yap  Message.add(id,gönderen_user_id, ilan_sahibi_id, post_id , takas_teklifi_post_id ,mesaj)

    with app.app_context():
        new_book = Message(user_id=int(infos[0]),
                           to_user_id=int(infos[1]),
                           post_id=int(infos[2]),
                           deal_post_id=int(infos[3]),
                           message=message,
                           release_date=release_date_find(),

        )

        post_choosen = Post.query.filter_by(id=int(infos[3])).first()
        if post_choosen.items_list is None or post_choosen.items_list == "":
            items = []
        else:
            items = json.loads(post_choosen.items_list)

        items.append(int(infos[2]))
        post_choosen.items_list = str(items)

        db.session.add(new_book)
        db.session.commit()

    # Normalde Takasta Olmayan Ürün Deflaut
    # Submit Deyince Takasta Oluyor
    # Takas iptal veya 'mesaj' edilirse takastan Çıkıyor


    return jsonify({'message': 'Data submitted successfully'})







# Add the custom filter to the Jinja environment
@app.route('/takas_cevap-<cevap>-<int:message_id>', methods=['POST','GET'])
def takas_cevap(cevap,message_id):
    print(cevap)
    session['user'] = info_default
    message = Message.query.filter_by(id=message_id).first()

    if cevap == 'False':
        with app.app_context():
            post_choosen = Post.query.filter_by(id=int(message.deal_post_id)).first()
            post_choosen.items_list
            items = json.loads(post_choosen.items_list)

            items.remove(int(message.post_id))
            post_choosen.items_list = str(items)
            db.session.commit()

    with app.app_context():
        message = Message.query.filter_by(id=message_id).first()
        message.kabul = cevap

        db.session.commit()


    return redirect(url_for("takas" , take="True"))



@app.route('/takas_cevap', methods=['POST', 'GET'])
def takas_cevap_mesaj():
    session['user'] = info_default
    message_id = request.get_json()["post"]
    mesaj = request.get_json()["form"]
    message = Message.query.filter_by(id=message_id).first()

    with app.app_context():
        post_choosen = Post.query.filter_by(id=int(message.deal_post_id)).first()
        post_choosen.items_list
        items = json.loads(post_choosen.items_list)
        items.remove(int(message.post_id))
        post_choosen.items_list = str(items)
        db.session.commit()

    #Yap Sıra ile message.user_id değiştiği için aynı oluyor farklı bir kaynağa kaydet geri gel değiştir
    with app.app_context():
        user_id = message.user_id
        message.user_id= message.to_user_id
        message.to_user_id = user_id
        message.message=mesaj
        db.session.commit()

    return redirect(url_for("takas", take="True"))







fake_post_id = 0

@app.route('/ilan-detay', methods=["GET" , "POST"])
def post_detail():
    session['user'] = info_default
    global is_edit,fake_post_id


    if "post_id" in request.form:
        post_id = request.form["post_id"]
        fake_post_id = post_id
    else:
        post_id = fake_post_id




    post = Post.query.filter_by(id=post_id).first()
    user=post.user



    post_image_sayi = len(post.images)

    user_id=None
    is_user = False
    if current_user.is_authenticated:
        user_id = current_user.id
        is_user=True

    images = post.images if post else []

    image_data_list = [image.data for image in images]
    image_base64_list = [base64.b64encode(data).decode('utf-8') for data in image_data_list]

    konum=[post.ilçe,post.city]

    takas_kategorileri=post.takas_kategori.split(",")

    if "edit" in request.args:
        is_edit = True


    posts=0
    post_sayi=0
    if current_user.is_authenticated:
        posts = Post.query.filter_by(user_id=current_user.id,pasif=False).all()


        post_sayi=len(posts)

    choosen_post=post


    im = Image.query.filter_by(post_id=choosen_post.id).first()


    son = Category.query.filter_by(id=post.category_id).first()
    ortanca = Category.query.filter_by(id=son.parent_id).first()
    root = Category.query.filter_by(id=ortanca.parent_id).first()



    title = post.title.split(" ")

    num_tittle =len(title)
    all_posts = Post.query.filter(or_((Post.city == post.city),(Post.title.contains(title[0]))) & or_((Post.pasif == 0),(Post.pasif == "0")))
    all_posts = all_posts.order_by(Post.release_date.desc()).all()

    num = round(len(all_posts)/6)





    if num == 0:
        all_posts = get_posts_recursive(category=root,city=None,search=None)


        if num == 0 :
            all_posts = Post.query.filter(or_((Post.pasif == 0), (Post.pasif == "0")))
            all_posts = all_posts.order_by(Post.release_date.desc()).all()


    num = round(len(all_posts) / 6)
    print(num)
    print(all_posts)



    return render_template("post_detail.html",posts=posts,num=num,is_user=is_user,current_user_id=user_id,post_sayi=post_sayi,choosen_post=choosen_post, post=post , images=images, image_base64_list=image_base64_list,user=user,konum=konum,takas_kategorileri=takas_kategorileri,is_edit=is_edit,post_image_sayi=post_image_sayi,all_posts=all_posts)

def parse_list(value):
    value = value.strip('[]')  # Remove brackets
    items = [item.strip() for item in value.split(',') if item.strip()]  # Split and remove empty items
    return items


env.filters['parse_list'] = parse_list

def get_posts_recursive(category,city,search):

    posts = []

    if search == None:

        if city is None:
            posts = category.posts.filter(or_((Post.pasif == 0), (Post.pasif == "0"))).all()


            for sub_category in category.children:
                posts += get_posts_recursive(sub_category, city=None, search=None)




        else:
            posts = category.posts.filter((Post.city == city) & or_((Post.pasif == 0), (Post.pasif == "0"))).all()


            for sub_category in category.children:
                posts += get_posts_recursive(sub_category,city=city ,search=None)



    else:

        if city == None:
            posts = category.posts.filter(or_((Post.pasif == 0), (Post.pasif == "0"))).all()

            for sub_category in category.children:


                posts += get_posts_recursive(sub_category, city=None , search=search )
            posts = [post for post in posts if search.lower() in post.title.lower()]


        else:
            posts = category.posts.filter((Post.city == city) & or_((Post.pasif == 0), (Post.pasif == "0"))).all()

            for sub_category in category.children:
                posts += get_posts_recursive(sub_category, city=city ,search=search)
            posts = [post for post in posts if search.lower() in post.title.lower()]

    posts = sorted(posts, key=lambda post: post.release_date, reverse=True)
    return posts

# Find the category
@app.route('/Takas-sil')
def delete_takas():
    message_id = request.args.get("selam")
    take = request.args.get("take")

    message = Message.query.filter_by(id=message_id).first()

    with app.app_context():
        post_choosen = Post.query.filter_by(id=int(message.deal_post_id)).first()
        items = json.loads(post_choosen.items_list)
        items.remove(int(message.post_id))
        post_choosen.items_list = str(items)
        db.session.commit()


    with app.app_context():
        message = Message.query.get_or_404(message_id)
        db.session.delete(message)
        db.session.commit()


    return redirect(url_for("takas" , take=take))

@app.route('/Takas-Tekflifleri')
def takas():
    session['user'] = info_default
    take= request.args.get("take")

    # if take == True
    #Yap To_user_id == Current User
        #Alınan Teklifler

    took_messages = Message.query.filter_by(to_user_id=current_user.get_id()).all()
    took_messages_list=[]


    for message in took_messages:

        gonderen = User.query.filter_by(id= message.user_id).first()
        p = Post.query.filter_by(id=message.post_id).first()
        t = Post.query.filter_by(id=message.deal_post_id).first()
        msg=message.message
        message_id = message.id
        message = Message.query.filter_by(id=message_id).first()
        kabul = message.kabul
        took_messages_list.append([t, msg, p,message, kabul, message_id])



    # print(took_messages_list)

    #if take == False
    # Yap user_id == Current User
        # Verilan Teklifler

    gave_messages = Message.query.filter_by(user_id=current_user.id).all()


    #yap Mesajı data base liste ekle

    gave_messages_list = []
    for message in gave_messages:
        p = Post.query.filter_by(id=message.post_id).first()
        t = Post.query.filter_by(id=message.deal_post_id).first()
        msg = message.message
        message_id = message.id
        message = Message.query.filter_by(id=message_id).first()
        kabul = message.kabul


        gönderen = User.query.filter_by(id=message.user_id).first()
        sender_name = [gönderen.name,gönderen.id]
        gave_messages_list.append([sender_name,t, msg, p,message, kabul,message_id])



    #
    # print(took_messages_list)
    #
    # print(gave_messages_list)
    is_kategori = False

    return render_template("Takas-Teklifleri.html",take=take,is_kategori = is_kategori,took_messages_list=took_messages_list,gave_messages_list=gave_messages_list ,  is_user=is_current_user)





@app.route('/kategori-<kategori>')
@app.route('/kategori-<kategori>-<city>')
@app.route('/kategori-<kategori>-<city>-<search_query>')
def kategori(kategori,city=None,search_query=None):
    session['user'] = info_default
    global kategori_list
    is_şehir = False
    is_search=False
    şehir = 0

    print(request.form)
    print(request.args)
    if city != None:
        is_şehir = True
        şehir = city

    search = ""

    if search_query != None :
        is_search = True
        search = search_query
        print("selam", search)

    if "search_query" in request.args:
        is_search = True
        search = request.args["search_query"]
        print("selam" ,search)



    if len(request.url.split("-")) >= 3:
        şehir = request.url.split("-")[2]

    if "şehir" in request.args:
        is_şehir = True
        şehir = request.args["şehir"]

        if şehir == "0" or şehir == 0:

            return redirect(url_for("kategori" ,kategori=kategori))
        else:
            all_posts = Post.query.filter(Post.city == şehir, or_(Post.pasif == 0, Post.pasif == "0"))
            all_posts = all_posts.order_by(Post.release_date.desc()).all()

    big_category =  Category.query.filter_by(name=kategori.capitalize()).all()




    sub_categories = big_category[0].children.all()
    ufak_kategori=[]
    for sub_category in sub_categories:

        ufak_kategori.append(sub_category.name)

    big_category = Category.query.filter_by(name=kategori.capitalize()).first()



    if big_category not in kategori_list:
        kategori_list.append(big_category)

    root_kategori = kategori_list[0].name

    category_1=0
    category_2=0
    category_3=0



    if big_category is not None:
        print("kategori", big_category)
        category_1 = big_category
        if big_category.parent_id != None:

            category_2 = Category.query.filter_by(id=big_category.parent_id).first()
            print("2", category_2)
            if category_2.parent_id != None:
                category_3 = Category.query.filter_by(id=category_2.parent_id).first()
                print("3", category_3)

    kategori_order = [category_1, category_2, category_3]


    category_posts=[]
    if big_category is not None:
        # Retrieve the posts for the category and its subcategories

        if len(request.url.split("-")) >= 3 or "search_query" in request.args :
            if "search_query" in request.args and len(request.url.split("-")) < 3 :
                    search = request.args["search_query"]
                    print("selam")
                    posts = get_posts_recursive(big_category, city=None,search=search)

            if "search_query" not in request.args and len(request.url.split("-")) >= 3:
                şehir = request.url.split("-")[2]
                if şehir == "0" or şehir == 0:
                    return redirect(url_for("kategori", kategori=kategori))
                posts = get_posts_recursive(big_category, city=şehir, search=None)

            if "search_query" in request.args and len(request.url.split("-")) >= 3:
                şehir = request.url.split("-")[2].split("?")[0]
                search = request.args["search_query"]
                if şehir == "0" or şehir == 0:
                    return redirect(url_for("kategori", kategori=kategori))
                else:
                    print("selam")
                    posts = get_posts_recursive(big_category,city=şehir ,search=search)

            if len(request.url.split("-")) == 4:
                şehir = request.url.split("-")[2]
                search = request.url.split("-")[3]
                print("selam")
                posts = get_posts_recursive(big_category, city=şehir, search=search)
        else:
            posts = get_posts_recursive(big_category, city=None ,search=None)

        if posts:
            # Iterate over the posts and do something with them
            for post in posts:

                category_posts.append(post)


        else:
            print("No posts found for the category:", big_category.name)
    else:
        print("Category not found.")



    kategori_search = kategori
    is_kategori = False
    if kategori_search != None:
        is_kategori= True

    aktegori_urun_bulunamadi=False
    if len(category_posts)==0:
        aktegori_urun_bulunamadi=True
        kategori_search = kategori

    a = len(category_posts) / 20
    nav_number = int(custom_round(a))
    page = 0
    if "page" in request.form:

        if int(request.form["page"]) != 1:
            page = int(request.form["page"])
            category_posts = category_posts[(page * 20) - 20:page * 20]
        else:
            category_posts = category_posts[0:20]
    else:
        category_posts = category_posts[0:20]

    return render_template("kategori.html",is_şehir=is_şehir,nav_number=nav_number,page=page,kategori_order=kategori_order,is_search = is_search,şehir=şehir,search=search,is_kategori=is_kategori,is_user=is_current_user,kategori_search=kategori_search,ufak_kategori=ufak_kategori,posts=category_posts,kategori_urun_bulunamadi=aktegori_urun_bulunamadi,root_kategori=root_kategori,kategori_list=kategori_list)







@app.route('/ilan' , methods= ["GET","POST"])
def ilan():
    session['user'] = info_default


    posts_by_john = Post.query.filter(Post.user_id == current_user.id, or_(Post.pasif == 0, Post.pasif == "0")).all()

    posts=posts_by_john



    if "pasif" in request.args:
        pasif_posts = Post.query.filter_by(user_id=current_user.id,pasif=True).all()

        a = len(pasif_posts) / 10
        nav_number = int(custom_round(a))
        page = 0

        if "page" in request.form:

            if int(request.form["page"]) != 1:
                page = int(request.form["page"])
                pasif_posts = pasif_posts[(page * 10) - 10:page * 10]
            else:
                pasif_posts = pasif_posts[0:10]
        else:
            pasif_posts = pasif_posts[0:10]


        return render_template("ilanlarım.html",page=page,nav_number=nav_number, is_user=is_current_user,pasif=True ,  posts=pasif_posts)

    a = len(posts) / 10
    nav_number = int(custom_round(a))
    page = 0

    if "page" in request.form:

        if int(request.form["page"]) != 1:
            page = int(request.form["page"])
            posts = posts[(page * 10) - 10:page * 10]
        else:
            posts = posts[0:10]
    else:
        posts = posts[0:10]

    print(request.form)
    return render_template("ilanlarım.html",is_user=is_current_user,page=page,nav_number=nav_number,posts=posts ,pasif=False)

@app.route('/delete' , methods=['GET', 'POST'])
def delete():
    post_id = request.form.get('post_id')
    with app.app_context():
        post = Post.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()

    return redirect(url_for("ilan"))


@app.route('/kullanıcı-bilgileri' , methods=['GET', 'POST'])
def user_detail():
    user_info = session.get('user')
    if "post_id" in request.form or user_info["name"] != 0 :
        user_id = current_user.id
        user =User.query.filter_by(id=user_id).first()
        user_name = user.name
        user_last_name = user.last_name

        user_password = user.password
        user_email = user.email

        user_info = session.get('user')  # Retrieve user data from session

        if user_info["name"] != 0 and "iptal" not in request.form :
            print("user_info", user_info)
            return render_template('kullanıcı-bilgileri.html', user_name=user_info['name'], user_last_name=user_info['last_name'],user_email=user_info['email'], user_password=user_info['password'], değiştir=True,is_user=is_current_user)

        return render_template("kullanıcı-bilgileri.html" , user_name=user_name,user_last_name=user_last_name,user_email=user_email,user_password=user_password , değiştir=False ,is_user=is_current_user)


    return  redirect(url_for("home"))


@app.route('/user-info-change' , methods=['GET', 'POST'])
def change_user_details():
    print("user_info-change",request.form)

    if "save" in request.form:
        with app.app_context():
            user =User.query.filter_by(id=current_user.id).first()
            user.name = request.form["name"]
            user.last_name = request.form["last_name"]
            password = generate_password_hash(password=request.form["password"], method='pbkdf2:sha256', salt_length=8)
            user.password = password
            user.email = request.form["email"]
            db.session.commit()



        return render_template("kullanıcı-bilgileri.html" , user_name=request.form["name"],user_last_name=request.form["last_name"],user_email=request.form["email"],user_password=password , değiştir=False)

    return  redirect(url_for("home"))











@app.route('/hide' , methods=['GET', 'POST'])
def hide():
    post_id = request.form.get('post_id')

    if request.form["edit"] == "hide":
        print("hide dedi")
        with app.app_context():
            post = Post.query.filter_by(id=post_id).first()
            post.pasif = True
            db.session.commit()
        return redirect(url_for("ilan"))

    if request.form["edit"] == "show":
        print("show dedi")
        with app.app_context():
            post = Post.query.filter_by(id=post_id).first()
            post.pasif = False
            db.session.commit()

        return redirect(url_for("ilan", pasif=True))




@app.route('/edit_post-<int:post_id>')
def edit_post(post_id):


    return redirect(url_for("ilan"))


@app.route('/login_choise')
def login_choise():
    session['user'] = info_default
    return render_template("login_choise.html")

def translate(word):
    api_key = "12337be60292be50d57e"
    endpoint = "https://api.mymemory.translated.net/get"

    response = requests.get(endpoint, params={"q": word, "langpair": "en|tr", "key": api_key})
    result = response.json()["responseData"]["translatedText"]
    return result


def find_makes_by_year(selected_year):
    global marka_list
    response = requests.get(f'https://www.fueleconomy.gov/ws/rest/vehicle/menu/make?year={selected_year}')

    root = ET.fromstring(response.content)

    for menuItem in root.findall('menuItem'):
        text = menuItem.find('text').text
        value = menuItem.find('value').text
        marka_list.append(value)



def find_models_by_year_and_make(selected_year,selected_make):
    global model_list
    model_find_model = requests.get(f"https://www.fueleconomy.gov/ws/rest/vehicle/menu/model?year={selected_year}&make={selected_make}")
    root_model = ET.fromstring(model_find_model.content)

    for menuItem in root_model.findall('menuItem'):
        text = menuItem.find('text').text
        value = menuItem.find('value').text
        model_list.append(value)

def find_vehicle_models_by_year_make_vehicletype(selected_year,selected_make,vehicle_type):
    if vehicle_type=="Motosiklet":
        vehicle_type=            "moto"
    if vehicle_type=="Dorse":
        vehicle_type=          "trailer"
    if vehicle_type=="Suv,Pic-up":
        vehicle_type=           "mpv"
    if vehicle_type=="Kamyon":
        vehicle_type =           "truck"
    if vehicle_type=="Minibüs":
        vehicle_type=             "bus"
    global model_list
    model_find_model_url = f'https://vpic.nhtsa.dot.gov/api/vehicles/getmodelsformakeyear/make/{selected_make}/modelyear/{selected_year}/vehicleType/{vehicle_type}?format=json'
    response = requests.get(model_find_model_url)

    my_list = [response.content]

    result_dict = json.loads(my_list[0].decode())

    results = result_dict['Results']
    for a in results:
        model_name = a['Model_Name']
        model_list.append(model_name)



def find_details_by_year_make_and_model(selected_year,selected_make,selected_model):
    detail_find= requests.get(f"https://www.fueleconomy.gov/ws/rest/vehicle/menu/options?year={selected_year}&make={selected_make}&model={selected_model}")
    root_detail = ET.fromstring(detail_find.content)
    for menuItem in root_detail.findall('menuItem'):
        text = menuItem.find('text').text
        value = menuItem.find('value').text

        detail_list.append(translate(text))


def find_makes_vehicles_by_year_and_make(vehicle_type,year,make):
    import requests
    import json
    if vehicle_type=="Motosiklet":
        vehicle_type=            "moto"
    if vehicle_type=="Dorse":
        vehicle_type=          "trailer"
    if vehicle_type=="Suv,Pic-up":
        vehicle_type=           "mpv"
    if vehicle_type=="Kamyon":
        vehicle_type =           "truck"
    if vehicle_type=="Minibüs":
        vehicle_type=             "bus"


def find_allmakes_by_vehicletype(vehicle_type):
    if vehicle_type=="Motosiklet":
        vehicle_type=            "moto"
    if vehicle_type=="Dorse":
        vehicle_type=          "trailer"
    if vehicle_type=="Suv,Pic-up":
        vehicle_type=           "mpv"
    if vehicle_type=="Kamyon":
        vehicle_type =           "truck"
    if vehicle_type=="Minibüs":
        vehicle_type=             "bus"

    api_url = f'https://vpic.nhtsa.dot.gov/api/vehicles/GetMakesForVehicleType/{vehicle_type}?format=json'
    response = requests.get(api_url)

    my_list = [response.content]

    result_dict = json.loads(my_list[0].decode())

    results = result_dict['Results']
    for a in results:
        model_name = a['MakeName']
        vehicle_marka_list.append(model_name)


def create_category(category_names,image_files,post_veri,is_emlak,is_telefon,is_vasıta):
    #yap kesin olanlar
    title=post_veri[0]
    content = post_veri[1]
    price = post_veri[2]
    para_birim = post_veri[3]
    takas_kategori=post_veri[4]
    if takas_kategori == "":
        #Yap ilanı gösterir iken , ile ayır like : [iphone,apple]
        takas_kategori="Herhangi bir şey ile TAKAS olabilir"

    state = post_veri[5]
    şehir = post_veri[6]
    ilçe = post_veri[7]

    print("KATEGORİ KONTROL","EMLAK:",is_emlak,"Vasıta:",is_vasıta,"Telefon:",is_telefon)
    if is_vasıta == True:
        yıl = post_veri[8]
        km = post_veri[9]
        motor_hacmi = post_veri[10]
        hp = post_veri[11]
        vites = post_veri[12]
        yakıt = post_veri[13]
        ağır_hasar = post_veri[14]

    if is_emlak ==True:
        brüt_metre = post_veri[8]
        net_metre = post_veri[9]
        oda = post_veri[10]
        yaş = post_veri[11]
        kat = post_veri[12]
        bina_kat_sayı = post_veri[13]
        banyo_sayısı = post_veri[14]
        balkon = post_veri[15]
        eşyalı = post_veri[16]
        site = post_veri[17]
        aidat = post_veri[18]
        depozito = post_veri[19]

    if is_telefon == True:
        marka = post_veri[8]
        ram = post_veri[9]
        model = post_veri[10]
        kamera = post_veri[11]
        hafıza = post_veri[12]
        ön_kamera = post_veri[13]
        ekran = post_veri[14]
        renk = post_veri[15]
        garanti = post_veri[16]





    # print(f"{para_birim}, {şehir} ,{ilçe}")
    with app.app_context():
        # Set parent_category to the root category
        parent_category = None

        # Loop over the category names
        for category_name in category_names:
            # Check if the category already exists
            category = Category.query.filter_by(name=category_name.capitalize(), parent=parent_category).first()
            print(category)
            if category is None:
                # Create a new category if it doesn't exist
                category = Category(name=category_name.capitalize(), parent=parent_category)
                db.session.add(category)
                db.session.commit()
            else:
                print(f"{category_name} already exists")

            # Set the parent category for the next iteration
            parent_category = category

        # Retrieve the last category
        last_category = category
        user = User.query.filter_by(id=current_user.id).first()

        if last_category is not None:
            if is_vasıta:
                yıl = post_veri[8]
                km = post_veri[9]
                motor_hacmi = post_veri[10]
                hp = post_veri[11]
                vites = post_veri[12]
                yakıt = post_veri[13]
                ağır_hasar = post_veri[14]
                new_post = Post(title=title, content=content, price=price, ilçe=ilçe, city=şehir,
                                release_date=release_date_find(), state=state, para_birim=para_birim,
                                takas_kategori=takas_kategori, user=user, yıl=yıl, km=km, motor_hacmi=motor_hacmi,
                                hp=hp, vites=vites, yakıt=yakıt, ağır_hasar=ağır_hasar, user_id=user.id,
                                category_id=last_category.id)
                db.session.add(new_post)
                db.session.commit()
            elif is_emlak:
                brüt_metre = post_veri[8]
                net_metre = post_veri[9]
                oda = post_veri[10]
                yaş = post_veri[11]
                kat = post_veri[12]
                bina_kat_sayı = post_veri[13]
                banyo_sayısı = post_veri[14]
                balkon = post_veri[15]
                eşyalı = post_veri[16]
                site = post_veri[17]
                aidat = post_veri[18]
                depozito = post_veri[19]
                print("Post Verileri" , post_veri)
                new_post = Post(title=title, content=content, price=price, ilçe=ilçe, city=şehir,
                                release_date=release_date_find(), state=state, para_birim=para_birim,
                                takas_kategori=takas_kategori, user=user, brüt_metre=brüt_metre, net_metre=net_metre,
                                oda=oda, yaş=yaş, kat=kat, bina_kat_sayı=bina_kat_sayı, banyo_sayısı=banyo_sayısı,
                                balkon=balkon, eşyalı=eşyalı, site=site, aidat=aidat, depozito=depozito,
                                user_id=user.id, category_id=last_category.id)
                db.session.add(new_post)
                db.session.commit()
                print("İlan Eklendi")
            elif is_telefon:
                marka = post_veri[8]
                ram = post_veri[9]
                model = post_veri[10]
                kamera = post_veri[11]
                hafıza = post_veri[12]
                ön_kamera = post_veri[13]
                ekran = post_veri[14]
                renk = post_veri[15]
                garanti = post_veri[16]

                new_post = Post(title=title, content=content, price=price, ilçe=ilçe, city=şehir,
                                release_date=release_date_find(), state=state, para_birim=para_birim,
                                takas_kategori=takas_kategori, user=user, marka=marka, model=model, ram=ram,
                                kamera=kamera, ön_kamera=ön_kamera, hafıza=hafıza, ekran=ekran, renk=renk,
                                garanti=garanti, user_id=user.id, category_id=last_category.id)
                db.session.add(new_post)
                db.session.commit()
            else:
                new_post = Post(title=title, content=content, price=price, ilçe=ilçe, city=şehir,
                                release_date=release_date_find(), state=state, para_birim=para_birim,
                                takas_kategori=takas_kategori, user=user, user_id=user.id, category_id=last_category.id)
                db.session.add(new_post)
                db.session.commit()



            for image in image_files:
                image_data = image.read()
                if len(image_data) == 0 :
                    print("söylee")
                else:
                    image_entry = Image(post_id=new_post.id, data=image_data, post=new_post)
                    db.session.add(image_entry)
                db.session.commit()

            print("New post added to the last category:", last_category.name)

            redirect(url_for("ilan"))
        else:
            print("Last category does not exist.")





is_make=False
is_model=False
marka_list=[]
vehicle_marka_list=[]
model_list=[]
detail_list=[]
little_title=False
car=False
is_otomobil=False# Eğer ki vasıta seçilirse durumu veya olmayan durumu select ile ayarla
is_detail=True

finish_categories_for_car=False
finish_categories_for_everything=False

is_emlak=False
is_telefon= False
is_vasıta= False
category_list=0

change_post=0


@app.route('/add_post',methods=["GET","POST"])
def add_post():
    global is_emlak,is_vasıta,is_telefon,category_list,is_edit,change_post
    login_form = LoginForm()

    if "edit" in request.form:
        is_edit = True
        print(request.form)
        post_id=int(request.form["post_id"])
        change_post=Post.query.filter_by(id=post_id).first()

        print(change_post)


        attributes = change_post.__table__.columns.keys()  # Get attribute/column names
        values = [getattr(change_post, attr) for attr in attributes]  # Get attribute values
        print(values)

        ufak_category = Category.query.filter_by(id=change_post.category_id).first()
        root_category = ufak_category.parent.parent
        ortanca_category = ufak_category.parent
        kategor_listesi=[root_category.name,ortanca_category.name,ufak_category.name]

        otomobil_kateogri = "a"
        vasıta_kateogri= "a"
        pp = int(root_category.name)

        if pp > 1500:
            otomobil_kateogri= Category.query.filter_by(id=root_category.parent_id).first()
            vasıta_kateogri= Category.query.filter_by(id=otomobil_kateogri.parent_id).first()


        if kategor_listesi != []:
            print("Categry List", kategor_listesi)
            print(vasıta_kateogri)
            if len(kategor_listesi) >= 3 and kategor_listesi[1] == "Telefonlar" and kategor_listesi[2] not in (
            "Ev telefonlar", "Telefon aksesuarları"):
                is_telefon = True

            if len(kategor_listesi) >= 3 and kategor_listesi[1] == "Konut":
                is_emlak = True
            if otomobil_kateogri != "a":
                if len(kategor_listesi) >= 3 and vasıta_kateogri.name == "Vasıta" and otomobil_kateogri.name not in (
                "Tarım Araçları ve Ekipmanları", "Parçalar ve Aksesuarlar", "İnşaat Araçları ve Ekipmanları"):
                    is_vasıta = True
                    print("is_vasıta True")



        images=Image.query.filter_by(post_id=post_id).all()


        title = values[1]
        content = values[2]
        state = values[3]
        price = values[4]
        para_birim = values[5]
        takas_kategori = values[6]
        şehir = values[10]
        ilçe = values[11]




        return render_template("add_post.html", is_edit=is_edit, is_user=is_current_user, is_telefon=is_telefon,
                               is_vasıta=is_vasıta, is_emlak=is_emlak,
                               title=title,
                               content=content, state=state, price=price, para_birim=para_birim,
                               takas_kategori=takas_kategori
                               , şehir=şehir, ilçe=ilçe, images=images)


    if 'change' in request.form:  # Değiştir butonuna tıklanır ise
        form_data = request.form.to_dict()  # Get all form data as a dictionary
        files = request.files.getlist('files')
        print(files)


        post_bilgileri = [value.strip() for value in form_data.values()]


        print(post_bilgileri)

        with app.app_context():
            change_post = Post.query.filter_by(id=change_post.id).first()
            change_post.title = post_bilgileri[0]
            change_post.content = post_bilgileri[1]
            change_post.price = post_bilgileri[2]
            change_post.para_birim = post_bilgileri[3]
            change_post.takas_kategori = post_bilgileri[4]
            change_post.state = post_bilgileri[5]
            change_post.şehir = post_bilgileri[6]
            change_post.ilçe = post_bilgileri[7]

            images = Image.query.filter_by(post_id=change_post.id).all()


            for image in images:
                db.session.delete(image)
                db.session.commit()


            if files is not None:
                for image in files:
                    image_data = image.read()
                    image_entry = Image(post_id=change_post.id, data=image_data, post=change_post)
                    db.session.add(image_entry)


            db.session.commit()

        return redirect("/ilan")


    is_vasıta =False
    is_emlak = False
    is_telefon = False

    print(is_vasıta, is_emlak, is_telefon)

    print("FORM_data", request.args.getlist('form_data') )
    if request.args.getlist('form_data') != []:
        category_list = request.args.getlist('form_data')
        print("Categry List",category_list)
        if len(category_list) >= 3 and  category_list[1] in  ("Telefonlar","Telefon") and category_list[2] not in ("Ev telefonlar" ,"Telefon aksesuarları","Aksesuar","Yedek Parça","Numara","Giyilebilir Teknoloji"):
            is_telefon=True

        if len(category_list) >= 3 and  category_list[1] == "Konut" :
            is_emlak=True
        if len(category_list) >= 3 and  category_list[0] == "Vasıta" and category_list[1] not in ("Tarım Araçları ve Ekipmanları","Parçalar ve Aksesuarlar","İnşaat Araçları ve Ekipmanları"):
            is_vasıta=True


        print(is_vasıta,is_emlak,is_telefon)



    if 'finish' in request.form: #yap TAMAMLAYA BASILIR İSE DATA BASE E KAYDEDİYOR
        print("tamamla  ya tıklandı")

        veriler=[]





        files = request.files.getlist('files')

        print("KATEGORİ CHECK",category_list)

        post_bilgileri=list(request.form.values())

        post_bilgileri.pop()
        print(is_vasıta,is_emlak,is_telefon)


        create_category(image_files=files,category_names=category_list,is_vasıta=is_vasıta,is_telefon=is_telefon,is_emlak=is_emlak,post_veri=post_bilgileri)

        veriler.append(files)
        veriler.append(post_bilgileri)


        print(post_bilgileri)
        print(category_list)



        return redirect("/ilan")


        #Yap  HER SAYFADA BİLGİLERİ AL VE BİRİKTİREREK DİĞER SAYFAYA YÖNLENDİR
        # eN SONUNDA
        #create_category(category_names=kategoriler_listesi,image_files=image_files)

        redirect(url_for("ilan"))




    return render_template("add_post.html",is_edit=False,is_user=is_current_user,is_telefon=is_telefon,is_vasıta=is_vasıta,is_emlak=is_emlak,form=login_form)















@app.route('/choose_category',methods=["GET","POST"])
def choose_category():
    session['user'] = info_default
    global is_make, little_title, is_model, marka_list, model_list, detail_list, car, is_otomobil, is_detail,finish_categories_for_car,finish_categories_for_everything
    car = False
    is_otomobil = False
    is_detail = False
    finish_categories_for_car=False
    if 'country' in request.form:
        marka_list.clear()
        model_list.clear()
        vehicle_marka_list.clear()
        detail_list.clear()

        selected_value = request.form["country"]
        selected_topic = request.form["county"]
        selected_year = request.form["town"]
        if selected_topic == "Otomobil" or selected_topic == "Kiralık Araç":
            is_otomobil = True
            find_makes_by_year(selected_year)
        elif selected_topic == "Motosiklet" or selected_topic == "Suv,Picup" or selected_topic == "Kamyon" or selected_topic == "Minibüs" :
            is_otomobil = False
            find_allmakes_by_vehicletype(selected_topic)

        # else:
        #     find_makes_vehicles_by_year_and_make(vehicle_type=selected_topic,year=selected_year)

        is_make = True
        if selected_value == "Vasıta" and selected_topic not in ("Kiralık Araç",
        "Tekneler ve Jet Skiler", "Tarım Araçları ve Ekipmanları", "Parçalar ve Aksesuarlar",
        "İnşaat Araçları ve Ekipmanları"):
            car = True
        else:
            finish_categories_for_car = True



        if 'finish' in request.form:

            form_data = list(request.form.values())[:-1]
            print("Form-Data,KAtegroi Seçimi",form_data)
            return redirect(url_for('add_post', form_data=form_data))


        print(f"{selected_value}, {selected_topic}, {selected_year} ,")

        if 'little_title' in request.form:
            little_title = True
            print(little_title)
            selected_alt = request.form['little_title']
            if selected_topic == "Otomobil":
                find_models_by_year_and_make(selected_year=selected_year, selected_make=selected_alt)
            else:
                find_vehicle_models_by_year_make_vehicletype(selected_year=selected_year, selected_make=selected_alt,
                                                             vehicle_type=selected_topic)

            print(f"{selected_value}, {selected_topic}, {selected_year} , {selected_alt}")

            if 'model' in request.form:
                is_model = True
                selected_model = request.form['model']
                # // BU KISIMA FUNCTİON()
                print(f"{selected_value}, {selected_topic}, {selected_year} , {selected_alt} , {selected_model}")

                find_details_by_year_make_and_model(selected_year, selected_alt, selected_model)
                if len(detail_list) == 0:
                    is_detail = False
                else:
                    is_detail = True


                finish_categories_for_car=True





                if 'detail' in request.form:
                    selected_detail = request.form['detail']
                    print(f"{selected_value}, {selected_topic}, {selected_year} , {selected_alt} , {selected_model},{selected_detail}")



                    finish_categories_for_car=True

                    return render_template("choose_category.html", vehicle_marka_list=vehicle_marka_list,
                                           is_otomobil=is_otomobil, car=car, selected_detail=selected_detail,
                                           selected_alt=selected_alt, selected_value=selected_value, is_make=is_make,
                                           is_model=is_model, little_title=little_title, selected_topic=selected_topic,
                                           selected_year=selected_year, marka_list=marka_list, model_list=model_list,
                                           selected_model=selected_model, detail_list=detail_list,
                                           is_user=is_current_user,is_detail=is_detail,finish_categories_for_car=finish_categories_for_car)

                return render_template("choose_category.html", vehicle_marka_list=vehicle_marka_list, is_otomobil=is_otomobil,
                                       car=car, selected_alt=selected_alt, selected_value=selected_value,
                                       is_make=is_make, is_model=is_model, little_title=little_title,
                                       selected_topic=selected_topic, is_detail=is_detail, selected_year=selected_year,
                                       marka_list=marka_list, model_list=model_list, selected_model=selected_model,
                                       detail_list=detail_list, is_user=is_current_user,finish_categories_for_car=finish_categories_for_car)

            return render_template("choose_category.html", vehicle_marka_list=vehicle_marka_list, is_otomobil=is_otomobil,
                                   car=car, selected_value=selected_value, is_make=is_make, little_title=little_title,
                                   selected_topic=selected_topic, selected_year=selected_year, marka_list=marka_list,
                                   selected_alt=selected_alt, model_list=model_list, is_user=is_current_user,finish_categories_for_car=finish_categories_for_car)

        return render_template("choose_category.html", selected_value=selected_value, is_make=is_make,
                               selected_topic=selected_topic, selected_year=selected_year, marka_list=marka_list,
                               car=car
                               , vehicle_marka_list=vehicle_marka_list, is_otomobil=is_otomobil,
                               is_user=is_current_user,finish_categories_for_car=finish_categories_for_car)



    return render_template("choose_category.html", is_model=False, is_user=is_current_user,finish_categories_for_car = finish_categories_for_car)





@app.route('/register',methods=["GET","POST"])
def register():
    if request.method=="POST":
        name=request.form['name']
        last_name = request.form['last_name']
        email = request.form['email']
        password_text = request.form['password']
        user = User.query.filter_by(email=email).first()

        if not user:
            password=generate_password_hash(password=password_text,method='pbkdf2:sha256', salt_length=8)



            with app.app_context():
                new_user = User(email=email,
                                password=password,
                                name=name,
                                last_name=last_name)
                db.session.add(new_user)
                db.session.commit()

            return redirect(url_for("ilan",user=new_user))
        else:

            flash("Bu Email zaten kayıtlı Giriş yapabilirsiniz")
            return redirect(url_for('login'))
    return render_template("register.html")




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_text = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(pwhash=user.password, password=password_text):
            session_cookie_name = 'session_' + email  # Unique session cookie name for each user
            session[session_cookie_name] = True

            login_user(user)
            logged_in = True
            return redirect(url_for('ilan', user=user.name))
        elif user and check_password_hash(pwhash=user.password, password=password_text) == False:
            flash("Şifre Yanlış ")
            return render_template("login.html")
        else:
            flash("Email Kayıtlı Değil")
            return render_template("login.html")
    return render_template("login.html")







@app.route("/hesap-kontrol" , methods = ["GET","POST"])
def hesap_kontrol():


    email = request.form["email"]
    password = request.form["password"]

    if "tamamla" in request.form:


        user = User.query.filter_by(id=current_user.id).first()

        if user.email == email and  check_password_hash(pwhash=user.password, password=password):
            user_id = current_user.id
            user = User.query.filter_by(id=user_id).first()
            print("form", request.form)
            user_info = {
                'name': user.name,
                'last_name': user.last_name,
                'email': user.email,
                'password': password,
                'post_id' : 0,
            }

            session['user'] = user_info

            return redirect(url_for('user_detail'))


        else:
            flash("Şifren Yanlış")

            return render_template("hesap-kontrol.html" ,email=email)


    return render_template("hesap-kontrol.html" ,email=email)










@app.route('/secrets/<user>')
@login_required
def secrets(user):
    logged_in=True
    return render_template("secrets.html",user=user,
                           logged_in=logged_in)



@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))



if __name__ == "__main__":
    socketio.run(app ,debug=True)
    app.run(debug=True)
