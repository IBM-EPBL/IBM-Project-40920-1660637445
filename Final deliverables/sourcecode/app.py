
import re
import ibm_db
import ibm_db_dbi

from flask_mail import Mail, Message

from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase


app = Flask(__name__)
mail = Mail(app)
app.secret_key = 'a'

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'sridevi032002@gmail.com'
app.config['MAIL_PASSWORD'] = 'srichlmdevi9236'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


conn=ibm_db.connect("DATABASE=bludb;HOSTNAME=ba99a9e6-d59e-4883-8fc0-d6a8c9f7a08f.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=31321;SECURITY=SSL;SSLServerCertificate=Certificate.crt;UID=fqd68289;PWD=Pt7Lr9FUjtzoM73p",'','')
connection=ibm_db_dbi.Connection(conn)
#homepage
@app.route("/home")
def home():
    return render_template("homepage.html")
@app.route("/")
def add():
    return render_template("home.html")


#signup or reg
@app.route("/signup")
def signup():
    return render_template("signup.html")
@app.route('/register', methods =['GET', 'POST'])
def register():
    global userid
    global email
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        sql="SELECT * FROM data WHERE username=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
                    msg = 'name must contain only characters and numbers !'
        else:
            insert_sql = "INSERT INTO Data VALUES (?, ?, ?)"
            stmt = ibm_db.prepare(conn,insert_sql)
            ibm_db.bind_param(stmt, 1, username)
            ibm_db.bind_param(stmt, 2, email)
            ibm_db.bind_param(stmt, 3, password)
            ibm_db.execute(stmt)
            msg = 'You have successfully registered !'
    return render_template('signup.html', msg = msg)





#login
@app.route("/signin")
def signin():
    return render_template("login.html")
@app.route('/login',methods =['GET', 'POST'])
def login():
    global userid
    global useremail
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
        stmt = ibm_db.prepare(conn,'SELECT * FROM Data WHERE username= ?AND password = ?')
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print (account)
        if account:
            session['loggedin']=True
            session['id']=account['USERNAME']
            userid=account['USERNAME']=account['USERNAME']
            useremail=account["EMAIL"]
            msg='logged in successfully'
            return redirect('/home')
        else:
            msg ='Incorrect username / password !'
    return render_template('login.html', msg = msg)
@app.route('/base')
def base():
    uid = session['id']
    return render_template('base.html',name=uid)


#add

@app.route("/add")
def adding():
    return render_template('add.html')
@app.route('/addexpense',methods=['GET', 'POST'])
def addexpense():
    global id
    uid=session['id']
    if request.method == 'POST':
        date = request.form['date']
        time=request.form['time']
        expensename = request.form['expensename']
        amount = request.form['amount']
        paymode = request.form['paymode']
        category = request.form['category']
        uid=session['id']
        print(id)
        sql = "INSERT INTO expenses(userid,date,time,expensename,amount,paymode,category) VALUES(? ,?, ?, ?, ?, ?, ?)"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['id'])
        ibm_db.bind_param(stmt,2,date)
        ibm_db.bind_param(stmt,3,time)
        ibm_db.bind_param(stmt,4,expensename)
        ibm_db.bind_param(stmt,5,amount)
        ibm_db.bind_param(stmt,6,paymode)
        ibm_db.bind_param(stmt,7,category)
        ibm_db.execute(stmt)
        print(date+""+ time + " " + expensename + " " + amount + " " + paymode + " " + category)
    return redirect("/display")



#display
@app.route('/display')
def graph():
    param = "SELECT * FROM expenses ORDER BY date DESC "
    dataframe=pd.read_sql(param,connection)
    print(dataframe)
    dic=dataframe.to_dict('dict')
    print(dic)
    select="SELECT * FROM expenses "
    cur = connection.cursor()
    cur.execute(select)
    row=cur.fetchall()
    print(row)
    texpense = []
    userid= []
    date = []
    time = []
    expense_name = []
    amount = []
    paymode = []
    cat = []
    for i in row:
        userid.append(i[0])
        date.append(i[1])
        time.append(i[2])
        expense_name.append(i[3])
        amount.append(i[4])
        paymode.append(i[5])
        cat.append(i[6])
    texpense.append([userid, date, time, expense_name, amount, paymode, cat])
    print(texpense)
    dataframe=pd.read_sql(select,connection)
    print(dataframe)
    dic=dataframe.to_dict('dict')
    total=0
    for ele in range(0,len(amount)):
        total=total+amount[ele]
    print(total)
    return render_template('display.html',  total = total ,tables=[dataframe.to_html(classes='data')], titles=dataframe.columns.values)
 
   
     
      

            
         
    
            
 #limit
@app.route("/limit" )
def limit():
       return render_template("limit.html")

@app.route("/limitnum" , methods = ['GET','POST' ])
def limitnum():
    global userid
    if request.method == "POST":
        number= request.form['number']
        sql = "INSERT INTO limit(userid,limit) VALUES(?,?)"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['id'])
        ibm_db.bind_param(stmt,2,number)
        ibm_db.execute(stmt)
    return redirect('/base')     
#today 
@app.route("/today")
def today():
    select="SELECT * FROM expenses WHERE  DATE(date) = DATE(current date) ORDER BY date DESC"
    cur = connection.cursor()
    cur.execute(select)
    row=cur.fetchall()
    print(row)
    texpense = []
    userid= []
    date = []
    time = []
    expense_name = []
    amount = []
    paymode = []
    cat = []
    for i in row:
        userid.append(i[0])
        date.append(i[1])
        time.append(i[2])
        expense_name.append(i[3])
        amount.append(i[4])
        paymode.append(i[5])
        cat.append(i[6])
    texpense.append([userid, date, time, expense_name, amount, paymode, cat])
    print(texpense)
    dataframe=pd.read_sql(select,connection)
    print(dataframe)
    dic=dataframe.to_dict('dict')
    total=0
    for ele in range(0,len(amount)):
        total=total+amount[ele]
    print(total)
   
    #   cursor = mysql.connection.cursor()
    #   cursor.execute('SELECT * FROM expenses WHERE userid = % s AND DATE(date) = DATE(NOW()) AND date ORDER BY `expenses`.`date` DESC',(str(session['id'])))
    #   expense = cursor.fetchall()

     
    return render_template("today.html", texpense = texpense,   total = total ,
                           expense_name=expense_name,date=date, cat=cat, paymode=paymode,
                           time=time,tables=[dataframe.to_html(classes='data')], titles=dataframe.columns.values)
                           
     
#REPORT

#month  

@app.route("/month")
def month():
    sql = "SELECT * FROM expenses WHERE MONTH(date) = 11 "
    cur = connection.cursor()
    cur.execute(sql)
    row=cur.fetchall()
    print(row)
    texpense = []
    userid= []
    date = []
    time = []
    expense_name = []
    amount = []
    paymode = []
    cat = []
    for i in row:
        userid.append(i[0])
        date.append(i[1])
        time.append(i[2])
        expense_name.append(i[3])
        amount.append(i[4])
        paymode.append(i[5])
        cat.append(i[6])
    texpense.append([userid, date, time, expense_name, amount, paymode, cat])
    print(texpense)
    total=0
    for ele in range(0,len(amount)):
        total=total+amount[ele]
    print(total)
    dataframe=pd.read_sql(sql,connection)
    print(dataframe)
    sql='SELECT * FROM limit ORDER BY limit DESC '
    cur = connection.cursor()
    cur.execute(sql)
    row=cur.fetchall()
    print(row)
    userid = []
    limit = []
    for i in row:
        userid.append(i[0])
        limit.append(i[1])
    ttotal=0
    for ele in range(0,len(limit)):
        ttotal=total+amount[ele]
    print(ttotal)
    if ttotal<=total:
        msg = Message(
                'Hello',
                sender ='sridevi032002@gmail.com',
                recipients = 'useremail'
               )
        msg.body = 'You have exceeded your expense limit'
        mail.send(msg)
        return 'Sent'
    else:
        print(ttotal)

    return render_template("month.html", texpense = texpense,  total = total ,
                           expense_name=expense_name,date=date, cat=cat, paymode=paymode,
                           time=time,tables=[dataframe.to_html(classes='data')], titles=dataframe.columns.values)


#year
@app.route("/year")
def year(): 
    select="SELECT * FROM expenses WHERE  YEAR(date)=2022"
    cur = connection.cursor()
    cur.execute(select)
    row=cur.fetchall()
    print(row)
    texpense = []
    userid= []
    date = []
    time = []
    expense_name = []
    amount = []
    paymode = []
    cat = []
    for i in row:
        userid.append(i[0])
        date.append(i[1])
        time.append(i[2])
        expense_name.append(i[3])
        amount.append(i[4])
        paymode.append(i[5])
        cat.append(i[6])
    texpense.append([userid, date, time, expense_name, amount, paymode, cat])
    print(texpense)
    total=0
    for ele in range(0,len(amount)):
        total=total+amount[ele]
    print(total)
    dataframe=pd.read_sql(select,connection)
    print(dataframe)
   
    #   cursor = mysql.connection.cursor()
    #   cursor.execute('SELECT * FROM expenses WHERE userid = % s AND DATE(date) = DATE(NOW()) AND date ORDER BY `expenses`.`date` DESC',(str(session['id'])))
    #   expense = cursor.fetchall()

     
    return render_template("year.html", texpense = texpense,   total = total ,
                           expense_name=expense_name,date=date, cat=cat, paymode=paymode,
                           time=time,tables=[dataframe.to_html(classes='data')], titles=dataframe.columns.values)
#log-out

@app.route('/logout')

def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   session.pop('email',None)
   return render_template('home.html')

             

if __name__ == "__main__":
    app.run(debug=True)
        
  









  
  

