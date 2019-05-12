import os
from flask import Flask, url_for, redirect,make_response
from flask import request
from flask import render_template
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from datetime import datetime
from wtforms.ext.sqlalchemy.fields import QuerySelectField,QuerySelectMultipleField

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed,FileRequired
from wtforms import StringField, SubmitField,TextAreaField,FileField,SelectField,DateTimeField
from wtforms.validators import Required
from wtforms.validators import Email
from wtforms.fields import html5

from flask_uploads import UploadSet,configure_uploads,All,TEXT,DOCUMENTS,IMAGES


from flask import Flask, render_template, session, redirect, url_for,flash

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_

import random
import string

from PIL import Image, ImageFont, ImageDraw, ImageFilter
from io import BytesIO

#----------------vertify code--------------------------------------
def rndColor():
    '''随机颜色'''
    return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))

def gene_text():
    '''生成4位验证码'''
    return ''.join(random.sample(string.ascii_letters+string.digits, 4))

def draw_lines(draw, num, width, height):
    '''划线'''
    for num in range(num):
        x1 = random.randint(0, width / 2)
        y1 = random.randint(0, height / 2)
        x2 = random.randint(0, width)
        y2 = random.randint(height / 2, height)
        draw.line(((x1, y1), (x2, y2)), fill='black', width=1)

def get_verify_code():
    '''生成验证码图形'''
    code = gene_text()
    # 图片大小120×50
    width, height = 120, 50
    # 新图片对象
    im = Image.new('RGB',(width, height),'white')
    # 字体
    font = ImageFont.truetype('app/static/arial.ttf', 40)
    # draw对象
    draw = ImageDraw.Draw(im)
    # 绘制字符串
    for item in range(4):
        draw.text((5+random.randint(-3,3)+23*item, 5+random.randint(-3,3)),
                  text=code[item], fill=rndColor(),font=font )
    # 划线
    draw_lines(draw, 2, width, height)
    # 高斯模糊
    im = im.filter(ImageFilter.GaussianBlur(radius=1.5))
    return im, code

#----------------------------------SQLpath--------------------
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

#-------------------------------------files upload config------------------------
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024
app.config['UPLOADED_FILES_DEST'] = os.path.join(basedir+"\static")
app.config['UPLOADED_FILES_ALLOW' ]= ['pdf']
files = UploadSet('files')
configure_uploads(app,files)
#--------------------------------SQLalchemy------------------------
app.config['SQLALCHEMY_DATABASE_URI'] =\
'sqlite:///' + os.path.join(basedir, 'blog.db')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True


db = SQLAlchemy(app)
#--------------------------------------------------------------------
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = 'shuaiqisong'

#--------------------------------SQL CLASS-------------------------
#-------------------------------sqlcalss DEMO----------------------
# class Role(db.Model):
#     __tablename__ = 'roles'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(64), unique=True)
#     users = db.relationship('User', backref='role')

# class User(db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(64), unique=True, index=True)
#     role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
class admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer,primary_key=True)
    mail = db.Column(db.Text,unique=True)
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    mail = db.Column(db.Text,unique=True)

    articals  = db.relationship('Artical', backref='users')
    comments  = db.relationship('Comment',backref='users')

class Artical(db.Model):
    __tablename__ = 'articals'
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.Text)
    abstruct = db.Column(db.Text)
    time = db.Column(db.DateTime)
    path = db.Column(db.Text)
    likes = db.Column(db.Integer,default = 0)
    unlikes = db.Column(db.Integer,default = 0)
    populerity = db.Column(db.Integer,default = 0)
    visitis = db.Column(db.Integer,default = 0)

    user_id = db.Column(db.Integer,db.ForeignKey('users.id'))
    subject_id = db.Column(db.Integer,db.ForeignKey('subjects.id'))
    comments  = db.relationship('Comment',backref='articals')
    themes = db.relationship('Tag',backref='articals')

class Tag(db.Model):
    __tablename__= 'tags'
    artical_id = db.Column(db.Integer,db.ForeignKey('articals.id'),primary_key=True)
    theme_id =  db.Column(db.Integer,db.ForeignKey('themes.id'),primary_key=True)

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.Text,unique=True)

    articals = db.relationship('Artical',backref='subjects')
    themes = db.relationship('Theme',backref='subjects')

class Theme(db.Model):
    __tablename__ = 'themes'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.Text,unique=True)
    subject_id = db.Column(db.Integer,db.ForeignKey('subjects.id'))
    themes = db.relationship('Tag',backref='themes')

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer,primary_key=True)
    time = db.Column(db.DateTime)
    content = db.Column(db.Text)
    likes = db.Column(db.Integer,default = 0)
    unlikes = db.Column(db.Integer,default = 0)
    
    artical_id  = db.Column(db.Integer,db.ForeignKey('articals.id'))
    user_id  = db.Column(db.Integer,db.ForeignKey('users.id'))

#--------------------------------FORMs CLASS--------------------------------
# class NameForm(FlaskForm):
#     name = StringField('What is your name?', validators=[Required()])
#     submit = SubmitField('Submit')

#-------------------------------subject creat form-------------------------------

class subCeate(FlaskForm):
    name = StringField('new subject u wanto create',validators=[Required()])
    verify_code = StringField('VerifyCode', validators=[Required()])
    submit = SubmitField('submit')
#--------------------------------theme create form-----------------------------
class themecre(FlaskForm):
    def query_subject():
        return [r.name for r in db.session.query(Subject).all()]

    def get_pk(obj):
        return obj
    # theme = QuerySelectField(label=' theme select ',validators=[Required()],query_factory=query_factory,get_pk=get_pk)
    subselect = QuerySelectField(label='choose a subject it belong to',validators=[Required()],query_factory=query_subject,get_pk=get_pk)

    name = StringField('new theme u wanto create',validators=[Required()])
    verify_code = StringField('VerifyCode', validators=[Required()])
    submit = SubmitField('submit')

#-------------------------------mail form------------------------------------
class MailForm(FlaskForm):
    mail = html5.EmailField('E-mail Putting Please', validators=[Email(),Required()])
    submit = SubmitField('submit')


#----------------------------------subject form ---------------------------------
class SubjectForm(FlaskForm):
    def query_subject():
        return [r.name for r in db.session.query(Subject).all()]
    def get_pk(obj):
        return obj
    subject = QuerySelectField(label='Subject CHoose Please',validators=[Required()],query_factory=query_subject,get_pk=get_pk)
    submit = SubmitField('submit')


#-----------------------------------articals form---------------------------------
class ArticalForm(FlaskForm):
    artical  = StringField('Artical Putting Please',validators=[Required()])
    submit = SubmitField('submit')


#---------------------------------------indite form-----------------------------------
class InditeForm(FlaskForm):
    mail = html5.EmailField('E-mail Putting Please', validators=[Email(),Required()])
    title = StringField('Artical title',validators=[Required()])
    abstruct = TextAreaField('Artical in brief',validators=[Required()])
    artical_file = FileField('Artical in PDF please',validators=[Required(), FileAllowed(['pdf'], 'PDF only!'),FileRequired()])
    # subselect = SelectField(label='choose a subject',validators=[Required()],choices=[(1, 'test1'), (2, 'test2')],coerce=int)
    def query_subject():
        return [r.name for r in db.session.query(Subject).all()]
    def query_theme():
        return [r.name for r in db.session.query(Theme).all()]
    
    def get_pk(obj):
        return obj
    # theme = QuerySelectField(label=' theme select ',validators=[Required()],query_factory=query_factory,get_pk=get_pk)
    subselect = QuerySelectField(label='choose a subject',validators=[Required()],query_factory=query_subject,get_pk=get_pk)
    themeselect = QuerySelectMultipleField(label='choose themes u like PRESS CTRL + LEFT MOUSE to select many',query_factory=query_theme,get_pk=get_pk)
    submit = SubmitField('submit')

#-------------------------------------------comment form-------------------------------------
class CommentForm(FlaskForm):
    mail = html5.EmailField('E-mail Putting Please', validators=[Email(),Required()]) 
    comment = TextAreaField('comment in brief',validators=[Required()])
    verify_code = StringField('VerifyCode', validators=[Required()])
    submit = SubmitField('submit')

#-------------------------------------utilities class------------------------------


#---------------------------------VIEW CLASS----------------------


#-------------------------------VIEW FUNCTIONS--------------------
#-------------------------------vertify code---------------------------
@app.route('/code')
def get_code():
    image, code = get_verify_code()
    # 图片以二进制形式写入
    buf = BytesIO()
    image.save(buf, 'jpeg')
    buf_str = buf.getvalue()
    # 把buf_str作为response返回前端，并设置首部字段
    response = make_response(buf_str)
    response.headers['Content-Type'] = 'image/gif'
    # 将验证码字符串储存在session中
    session['image'] = code
    return response
#--------------------donate page-------------------------------------------
@app.route('/donation', methods=['GET', 'POST'])
def donate_page():
    return render_template('donation.html')

#---------------------------------vote for comments-------------------------
@app.route('/<id>/<artical_id>/voteup', methods=['GET', 'POST'])
def comment_up(id,artical_id):
   
    vote = session.get(id+'comvote')
    if vote is None and vote !=True:
        session[id+'comvote'] = True
        comment = Comment.query.filter_by(id = id).first()
        comment.likes+=1
        db.session.add(comment)
        db.session.commit()
        db.session.flush()
    else:
        flash('u have vote already')
    form = CommentForm()
    comments =  Comment.query.filter_by(artical_id=artical_id).all()
    artical= Artical.query.filter_by(id=artical_id).first()
   
    return redirect(url_for('show_page',artical_id=artical.id))

@app.route('/<id>/<artical_id>/votedown', methods=['GET', 'POST'])
def comment_down(id,artical_id):
   
    vote = session.get(id+'comvote')
    if vote is None and vote !=True:
        session[id+'comvote'] = True
        comment = Comment.query.filter_by(id = id).first()
        comment.unlikes+=1
        db.session.add(comment)
        db.session.commit()
        db.session.flush()
    else:
        flash('u have vote already')
    form = CommentForm()
    comments =  Comment.query.filter_by(artical_id=artical_id).all()
    artical= Artical.query.filter_by(id=artical_id).first()
   
    return redirect(url_for('show_page',artical_id=artical.id))

#---------------------------------vote function-------------------

@app.route('/<id>/voteup', methods=['GET', 'POST'])
def vote_up(id):
   
    vote = session.get(id+'vote')
    if vote is None and vote !=True:
        session[id+'vote'] = True
        vartical = Artical.query.filter_by(id = id).first()
        vartical.likes+=1
        db.session.add(vartical)
        db.session.commit()
        db.session.flush()
    else:
        flash('u have vote already')
    form = CommentForm()
    comments =  Comment.query.filter_by(artical_id=id).all()
    artical= Artical.query.filter_by(id=id).first()
   
    return redirect(url_for('show_page',artical_id=artical.id))

@app.route('/<id>/downcvote', methods=['GET', 'POST'])
def vote_down(id):
    vote = session.get(id+'vote')
    if vote is None and vote !=True:
        session[id+'vote'] = True
        vartical = Artical.query.filter_by(id = id).first()
        vartical.unlikes+=1
        db.session.add(vartical)
        db.session.commit()
        db.session.flush()
    else:
        flash('u have vote already')
    form = CommentForm()
    comments =  Comment.query.filter_by(artical_id=id).all()
    artical= Artical.query.filter_by(id=id).first()
   
    return redirect(url_for('show_page',artical_id=artical.id))


#--------------------------------sub create page---------------------------------
@app.route('/subCreate', methods=['GET', 'POST'])
def subCeate_page():
    form = subCeate()
    if form.validate_on_submit():
        sub = Subject.query.filter_by(name = form.name.data).first()
        if session.get('image').lower() != form.verify_code.data.lower():
            flash('Wrong verify code.')
            return render_template('subCreate.html',form=form)
        if sub==None:
            sub = Subject(name = form.name.data)
            db.session.add(sub)
            db.session.commit()
            db.session.flush()
            flash("create successfully")
        else:
            flash('there have a existed subject u want')
    return render_template('subCreate.html',form=form)
#----------------------------theme reate-------------------------------------

@app.route('/themecre', methods=['GET', 'POST'])
def themecre_page():
    form = themecre()
    if form.validate_on_submit():
        theme = Theme.query.filter_by(name = form.name.data).first()
        sub = Subject.query.filter_by(name = form.subselect.data).first()
        if session.get('image').lower() != form.verify_code.data.lower():
            flash('Wrong verify code.')
            return render_template('themecre.html',form=form)
        if theme==None:
            sub = Theme(name = form.name.data,subject_id = sub.id)
            db.session.add(sub)
            db.session.commit()
            db.session.flush()
            flash("create successfully")
        else:
            flash('there have a existed theme u want')
    return render_template('themecre.html',form=form)
#-----------------------------404 and 500 pages----------------------------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
@app.errorhandler(413)
def internal_server_error(e):
    return render_template('413.html'), 413


#------------------------------DEMO TEST----------------------------
# @app.route('/<name>', methods=['GET', 'POST'])
# def home_page(name):
#     return render_template('basement.html',name = name)

# @app.route('/', methods=['GET', 'POST'])
# def home():
#     name = None
#     form = NameForm()
#     if form.validate_on_submit():
#         old_name = session.get('name')
#         if old_name is not None and old_name != form.name.data:
#             flash('Looks like you have changed your name!')
#         session['name'] = form.name.data
#         return redirect(url_for('home'))

#     return render_template('nameform.html', form=form, name=session.get('name'))

#-----------------------------------home page--------------------------

@app.route('/', methods=['GET', 'POST'])
def home_page():
    list=[]
    articals = Artical.query.order_by(Artical.populerity.desc()).all()
    for artical in articals:
        if((datetime.now()-artical.time).total_seconds()<2678400):
            list.append(artical)
    tags  = Tag.query.all()
    print(tags)
    # articals = ["the first","the second"]
    return render_template('home.html',articals = list,tags = tags)

#---------------------------------indite articals-----------------------------
@app.route('/Indite', methods=['GET', 'POST'])
def indite_page():
    form = InditeForm()
    if form.validate_on_submit():
            # if len(request.files['artical_file'].stream.read())>20*1024*1024:
            #     flash('out size')
        # old_file = session.get('file')
        # if old_file==None and old_file != form.artical_file.data:
            # if len(form.artical_file.data.read()) >20*1024*1024:
            #     flash("file is outsize")
            #     return render_template('Indite.html', form=form)
            # print(len(form.artical_file.data.read()))
            filename = files.save(form.artical_file.data)   
            user = User.query.filter_by(mail=form.mail.data).first()
            subject = Subject.query.filter_by(name = form.subselect.data).first()
            if user==None :
                user = User(mail = form.mail.data)
                db.session.add(user)
                db.session.commit()
                db.session.flush()
            newartical = Artical(title=form.title.data,abstruct=form.abstruct.data,
            time = datetime.now(),path=filename,user_id=user.id,subject_id = subject.id )
            db.session.add(newartical)
            db.session.commit()
            for tag in form.themeselect.data:
                theme = Theme.query.filter_by(name = tag).first()
                newrela = Tag(artical_id = newartical.id,theme_id = theme.id)
                db.session.add(newrela)
                db.session.commit()
            flash('upload success')
            # session['file'] = form.artical_file.data
        # else:
        #     flash('not input same file overtimes')
    else:
        filename = None
    

    return render_template('Indite.html', form=form)

#------------------------------show artical-----------------------------
@app.route('/artical/<artical_id>',methods=['GET','POST'])
def show_page(artical_id):
    form = CommentForm()
    if form.validate_on_submit():
        if session.get('image').lower() != form.verify_code.data.lower():
            flash('Wrong verify code.')
            redirect(url_for('show_page',artical_id = artical_id))
        user = User.query.filter_by(mail=form.mail.data).first()
        if user==None:
            user = User(mail = form.mail.data)
            db.session.add(user)
            db.session.commit()
            db.session.flush()
        newcom = Comment(time=datetime.now(),content = form.comment.data,artical_id=artical_id
            ,user_id=user.id)
        db.session.add(newcom)
        db.session.commit()
        db.session.flush()
    comments =  Comment.query.filter_by(artical_id=artical_id).order_by(Comment.time.desc()).all()
    # hot = Comment.query.filter_by(artical_id=artical_id).order_by(Comment.likes.desc()).first()
    # rcomments = Comment.query.filter_by(and_(artical_id=artical_id,id!=hot.id)).order_by(Comment.time.desc()).all()
    comnum = len(comments)
    # list=[]
    # list.append(hot)
    # for comment in rcomments:
    #     list.append(comment)
    artical= Artical.query.filter_by(id=artical_id).first()
    artical.visitis+=1
    artical.populerity = artical.likes + artical.visitis - artical.unlikes + comnum
    db.session.add(artical)
    db.session.commit()
    db.session.flush()
    # print((datetime.now()-artical.time).total_seconds())
    return render_template('artical.html',comments=comments,form = form,artical=artical)

#-------------------three different search for articals-------------------

#----------------------------------email find-----------------------------
@app.route('/MailFind',methods=['GET','POST'])
def MailFind_page():
    form = MailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(mail = form.mail.data).first()
        articals = Artical.query.filter_by(user_id = user.id).all()
        tags  = Tag.query.all()
        return render_template('FindResult.html',articals = articals,tags = tags)
    return render_template('MailFind.html',form=form)

#------------------------articals find------------------------------------
@app.route('/ArticalFind',methods=['GET','POST'])
def ArticalFind_page():
    form = ArticalForm()
    if form.validate_on_submit():
        # articals = Artical.query.filter_by(title = form.artical.data).all()
        articals = Artical.query.filter(Artical.title.like('%'+form.artical.data+'%')).all()
        tags  = Tag.query.all()
        return render_template('FindResult.html',articals = articals,tags = tags)
    return render_template('ArticalFind.html',form=form)

#---------------------------subjects find------------------------------------
@app.route('/SubjectFind',methods=['GET','POST'])
def SubjectFind_page():
    form = SubjectForm()
    if form.validate_on_submit():
        subject = Subject.query.filter_by(name = form.subject.data).first()
        articals = Artical.query.filter_by(subject_id = subject.id).all()
        tags  = Tag.query.all()
        return render_template('FindResult.html',articals = articals,tags = tags)
    return render_template('SubjectFind.html',form=form)

#---------------------------comment delete------------------------------------
@app.route('/delete',methods=['GET','POST'])
def comment_delete():
    form = deletet()
    if form.validate_on_submit():
        subject = admin.query.filter_by(mail = form.subject.data).first()
        return render_template('delete_success.html')
    return render_template('delete_fail.html')


#-----------------------------download file--------------------------------
@app.route("/download/<filepath>", methods=['GET','POST'])
def download_file(filepath):
    return app.send_static_file(filepath)

#-------------------------------
#------------------------------main function----------------------------------
if __name__ == '__main__':
    app.run(debug=True)
  
