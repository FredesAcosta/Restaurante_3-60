from flask import Flask, render_template,session,request
from flaskext.mysql import MySQL
import pymysql

mysql = MySQL()# Configure MySQL connection

app = Flask(__name__,template_folder='templates')

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'crud'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql.init_app(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    text = ''
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = mysql.connect()#conectamos a la base de datos
        cur = conn.cursor(pymysql.cursors.DictCursor)#instanciamos el cursor para que nos retorne un diccionario
        cur.execute(" SELECT * FROM accounts WHERE username = %s OR email = %s",(username,email,))#aqui se ejecuta la consulta
        accounts = cur.fetchone()

        if accounts:
            text = "Account already exists"
        else:
            #insercicion de datos
            cur.execute("INSERT INTO accounts VALUES(NULL, %s, %s, %s)", (username, email, password,))
            conn.commit()
            text = "Account successfully created!"    
    # elif request.method=='POST':
    #     text = "Fill in the forms"
    return render_template('register.html',text=text)

if __name__ == '__main__':
    app.run(debug=True)