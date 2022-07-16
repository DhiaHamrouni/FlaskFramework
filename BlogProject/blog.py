from flask import Flask ,render_template,request,session,flash,redirect
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash,check_password_hash
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
import yaml
import os
app=Flask(__name__)
Bootstrap(app)
#configure db
db=yaml.safe_load(open('db.yaml'))
app.config['MYSQL_HOST']=db['mysql_host']
app.config['MYSQL_USER']=db['mysql_user']
app.config['MYSQL_PASSWORD']=db['mysql_password']
app.config['MYSQL_DB']=db['mysql_db']
app.config['MYSQL_CURSORCLASS']='DictCursor'
mysql=MySQL(app)

app.config['SECRET_KEY'] =os.urandom(24)
CKEditor(app)


#Home
@app.route('/')
def index():
    return render_template('index.html')
#About
@app.route('/about')
def about():
    return render_template('about.html')
#Blogs
@app.route('/blogs/<int:id>/')
def blogs(id):
    cur=mysql.connection.cursor()
    resultvalue=cur.execute("Select * from blog where blog_id = {}".format(id))
    if resultvalue>0:
        blog=cur.fetchone()
        return render_template('blogs.html',blog=blog)
    return 'Blog Not Found'
#Registration
@app.route('/register/',methods=['GET','POST'])
def register():
    if request.method=='POST':
        form=request.form
        first_name=form['first_name']
        last_name=form['last_name']
        username=form['username']
        email=form['email']
        password=form['password']
        check_pass=form['confirm_password']
        if (password != check_pass):
            flash('Passwords do not match, Try Again','danger')
            return render_template('register.html')
        cur=mysql.connection.cursor()
        password=generate_password_hash(password)
        cur.execute("INSERT INTO user(first_name,last_name,username,email,password) Values(%s, %s, %s, %s, %s)",(first_name,last_name,username,email,password))
        mysql.connection.commit()
        cur.close()
        flash('Registration Successful, You can now Login','success')
        return redirect('/login')
    return render_template('register.html')
#login
@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method=='POST':
        form=request.form
        username=form['username']
        cur=mysql.connection.cursor()
        ResultValue=cur.execute("select * from user where username=%s",([username]))
        if ResultValue>0:
            user=cur.fetchone()
            if check_password_hash(user['password'],form['password']):
                session['login']=True
                session['firstName']=user['first_name']
                session['lastName']=user['last_name']
                flash('Welcome'+session['firstName']+'! You have been successfully logged in','success')
            else:
                cur.close()
                flash('Password does not match','danger')
                return render_template('login.html')
        else:
            cur.close()
            flash('User not found','danger')
            return render_template('login.html')
        cur.close()
        return redirect('/my-blogs')
    return render_template('login.html')

#write_blog
@app.route('/write-blog/',methods=['GET','POST'])
def write_blog():
    if request.method=='POST':
        blogpost=request.form
        title=blogpost['title']
        body=blogpost['body']
        author=session['firstName']+' '+session['lastName']
        cur=mysql.connection.cursor()
        cur.execute("Insert into blog(title,author,body) values(%s,%s,%s)",(title,author,body))
        mysql.connection.commit()
        flash('Successfully posted the blog','success')
        return redirect('/my-blogs/')
    return render_template('write-blog.html')
#my-blogs
@app.route('/my-blogs/')
def my_blogs():
    cur=mysql.connection.cursor()
    resultValue= cur.execute("Select * from blog")
    if resultValue>0:
        blogs=cur.fetchall()
        cur.close()
        return render_template('my-blogs.html',blogs=blogs)
    cur.close()
    return render_template('my-blogs',blogs=None)
#edit_blog
@app.route('/edit-blogs/<int:id>',methods=['GET','POST'])
def edit_blogs(id):
    if session['login'] == True :
        if request.method == 'POST':
            cur = mysql.connection.cursor()
            title = request.form['title']
            body = request.form['body']
            cur.execute("UPDATE blog SET title = %s, body = %s where blog_id = %s",(title, body, id))
            mysql.connection.commit()
            cur.close()
            flash('Blog updated successfully', 'success')
            return redirect('/blogs/{}'.format(id))
    cur = mysql.connection.cursor()
    result_value = cur.execute("SELECT * FROM blog WHERE blog_id = {}".format(id))
    if result_value > 0:
        blog = cur.fetchone()
        blog_form = {}
        blog_form['title'] = blog['title']
        blog_form['body'] = blog['body']
        return render_template('edit-blogs.html', blog_form=blog_form)
    return 'Blog Not Found'

#delete blog

@app.route('/delete-blog/<int:id>',methods=['POST'])
def delete_blogs():
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM blog WHERE blog_id = {}".format(id))
    mysql.connection.commit()
    flash("Your blog has been deleted", 'success')
    return redirect('/my-blogs')
#logout
@app.route('/logout/')
def logout():
    session.clear()
    flash("You have been logged out", 'info')
    return redirect('/')






if __name__=='__main__':    
    app.run()
