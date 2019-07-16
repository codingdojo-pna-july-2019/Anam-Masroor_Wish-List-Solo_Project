from flask import Flask, render_template,request, redirect, flash, session
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt
import re


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "key is secret"


#This route will show the form-WORKED
@app.route('/')
def index():
    return render_template("index.html")

#Register the user -WORKED- validation WORKED-user is getting added in db also
@app.route("/register", methods=["POST"])
def register():
    
    is_valid = True
    
    if len(request.form["first_name"]) < 2:
        is_valid = False
        flash("First name must be at least 2 character long!")
    if len(request.form["last_name"]) < 2:
        is_valid = False
        flash("Last name must be at least 2 character long!")
    if not EMAIL_REGEX.match(request.form['email']):
        is_valid = False
        flash("Please enter valid email address!")
    if len(request.form["password"]) < 8:
        is_valid = False
        flash("Password must be at least 8 charater long!")
    if (request.form["c_password"]) != request.form["password"]:
        is_valid = False
        flash("Password does not match!")
    
    if is_valid: #if user input passes all validation, route to success and "login"
        #hashing password
        password = bcrypt.generate_password_hash(request.form["password"])
        #create a connection to database
        mysql = connectToMySQL("wish_app")
        #build my query
        query = "INSERT into users (first_name, last_name, email, password, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(email)s, %(pass)s, Now(), Now());"

        #pass revlevant through query
        data = {
            "fn" : request.form["first_name"],
            "ln" : request.form["last_name"],
            "email" : request.form["email"],
            "pass" : password
        }
        #commit the query
        user_id = mysql.query_db(query, data)
        session["user_id"] = user_id
        return redirect("/wishes")
    else: 
        return redirect("/")

#Login the user
@app.route("/login", methods=["POST"])
def login_user():
    is_valid = True

    if len(request.form["email"]) < 1:
        is_valid = False
        flash("Enter valid email address!")
    if len(request.form["password"]) < 1:
        is_valid = False
        flash("Enter valid password!")

    if not is_valid:
        return redirect("/")
    else:
        #connect to DB
        mysql = connectToMySQL("wish_app")
        #run query
        query = "SELECT * FROM users WHERE users.email = %(email)s"
        data = {
            "email" : request.form["email"]
        }
        user =  mysql.query_db(query, data)
        if user:
            hashed_password = user[0]["password"]
            if bcrypt.check_password_hash(hashed_password, request.form["password"]):
                session["user_id"] = user[0]["id"]
                return redirect("/wishes")
            else:
                flash("Password is invalid")
                return redirect("/")
        else:
            print("Please enter valid email address!") 
            return redirect("/")

#Logout Route-once the user logged out-they should not be able to go back on the dashboard or user specfic page. 
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/") 

#email Search -Email already in the system
@app.route("/email", methods=["POST"])
def email():
    print(request.form)
    found = False

    mysql = connectToMySQL('wish_app')        # connect to the database 
    query = "SELECT email FROM users WHERE email = %(email)s;"
    data = { "email": request.form["email"] }
    result = mysql.query_db(query, data)
    if result:
        found = True
    return render_template('partials/email.html', found=found)  # render a partial and return it



#Wish Dashboard-which will show all the wishes by all the users when a specfic user is logged in -WORKED
@app.route("/wishes")
def dashboard():
    if 'user_id' not in session:
        return redirect("/")
    
    mysql = connectToMySQL("wish_app")
    query = "SELECT * FROM users WHERE users.id = %(id)s"
    data = {'id' : session['user_id']}
    user = mysql.query_db(query, data)

    mysql = connectToMySQL("wish_app")
    query = "SELECT * FROM wishes LEFT JOIN users ON user_id = users.id"
    wishes = mysql.query_db(query)

    mysql = connectToMySQL("wish_app")
    query = "SELECT wish_id, count(distinct likes.user_id) AS count FROM likes GROUP BY likes.wish_id"
    likes = mysql.query_db(query)

  
    return render_template("wishes.html", user=user[0], wishes=wishes, likes=likes)

#Create and Post a Wish-WORKED
@app.route("/wishes/create", methods=["POST"])
def create_wish():

    is_valid = True

    if len(request.form["wish_content"]) < 3:
        is_valid = False
        flash("Wish must be more than 2 character long!")

    if not is_valid:
        return redirect("/wishes")

    else:

        mysql = connectToMySQL("wish_app")
        query = "INSERT INTO wishes(user_id, wish_content, created_at, updated_at) VALUES (%(wid)s, %(wis)s, NOW(), NOW())"
        data = {
            "wis" : request.form["wish_content"],
            "wid" : session["user_id"] 
        }
        wish_id = mysql.query_db(query, data)
        return redirect("/wishes")


#Delete the Wish-WORKED | if logged in user try to delete someone else wish-an error flash-WORKEd
@app.route('/wishes/<wish_id>/delete', methods=["GET", "POST"])
def delete(wish_id):
    session['wish_id']= "wish_id"
    mysql = connectToMySQL('wish_app') 
    query = "SELECT * FROM wishes WHERE user_id = %(wid)s;"
    data = {
        "wid" : session["user_id"],
        

    }
    creater_id = mysql.query_db(query, data)
    if creater_id:
        mysql = connectToMySQL("wish_app")
        query = "DELETE FROM wishes WHERE id = %(wid)s;"
        data = {
            "wid" : int(wish_id)
            

        }
        mysql.query_db(query, data)
        flash("Wish Removed!")
        return redirect('/wishes')
    else:
        flash("This is not your Wish!")
        return redirect("/wishes")

#Edit Account -WORKEd
@app.route("/users/<user_id>/edit", methods =["GET", "POST"])
def edit(user_id):
    # print(id)
    user_id = session["user_id"]
    mysql = connectToMySQL("wish_app")
    query = "SELECT * FROM users WHERE id = %(id)s"
    data = {
        "id" : session["user_id"],
    }
    
    created_id = mysql.query_db(query, data)
    if created_id:
        return render_template("edit.html", user=created_id[0])
    else:
        flash("Not Your Account")
        return redirect("/wishes")

#Update Account -WORKED
@app.route("/users/<user_id>/update", methods=["GET", "POST"])
def update(user_id):
    is_valid= True
    if len(request.form["first_name"]) < 1:
        is_valid = False
        flash("First name field cannot be blank!")
    if len(request.form["last_name"]) < 2:
        is_valid = False
        flash("Last name field cannot be black!")
        
    if not is_valid:
        return redirect("/wishes")
    else:

        mysql = connectToMySQL("wish_app")
        query = "UPDATE users SET first_name = %(fn)s, last_name = %(ln)s, email = %(email)s, updated_at = NOW() WHERE id = %(id)s"
        data = {
            "fn" : request.form["first_name"],
            "ln" : request.form["last_name"],
            "email" : request.form["email"],
            "id" : session["user_id"]
        }
        mysql.query_db(query, data)
        flash("Account Updated")
        return redirect("/wishes")    

#Edit Wish-WORKEd
@app.route('/wishes/<wish_id>/edit', methods=["GET", "POST"])
def edit_wish(wish_id):
    session['wish_id']= wish_id
    mysql = connectToMySQL('wish_app') 
    query = "SELECT * FROM wishes WHERE user_id = %(wid)s AND id = %(id)s;"
    data = {
        "wid" : session["user_id"],
        "id" : int(wish_id)
    }
    creater_id = mysql.query_db(query, data)
    if creater_id:
        return render_template("edit_wish.html", wish=creater_id[0])
    else:
        flash("Not your Wish")
        return redirect("/wishes")
#Update Wish-WORKEd
@app.route("/wishes/<wish_id>/update", methods=["GET", "POST"])
def update_wish(wish_id):
    is_valid = True

    if len(request.form["wish_content"]) < 3:
        is_valid = False
        flash("Wish must be more than 2 character long!")

    if not is_valid:
        return redirect("/wishes")
    else:
        mysql = connectToMySQL("wish_app")
        query = "UPDATE wishes SET wish_content = %(wis)s, updated_at = NOW() where id = %(id)s"
        data = {
            "wis" : request.form["wish_content"],
            "id" : int(wish_id)
            
        }
        mysql.query_db(query, data)
        flash("Wish Updated")
        return redirect("/wishes")

#User Page-which will show all wishes of the Logged in user - WORKED
@app.route("/users/<user_id>", methods=["GET"])
def show_user(user_id):
    is_valid = True
    print(type(user_id)) 
    print(type(session["user_id"])) #type will show in command prompt what kind of class it is | since one was string and one was integar, I had to make next line integar to match the comparison
    if int(user_id) != session["user_id"]:   #!= for comparisons, = for assignments
        is_valid = False
        flash ("Not Your Account")
    if not is_valid:
        return redirect("/wishes")
    else:
        mysql = connectToMySQL("wish_app")
        query = "SELECT * FROM users WHERE users.id = %(id)s"
        data = {'id' : session['user_id']}
        user = mysql.query_db(query, data)
        

        mysql = connectToMySQL("wish_app")
        query = "SELECT * FROM wishes LEFT JOIN users ON user_id = users.id WHERE user_id = %(wid)s"
        data = {"wid" : user_id}

        wishes = mysql.query_db(query, data)
        return render_template("users.html", user=user[0], wishes=wishes)

#Like the wish-WORKED
@app.route("/wishes/<wish_id>/add_like", methods=["POST"])
def add_like(wish_id):
    # session['wish_id']= wish_id
    mysql = connectToMySQL('wish_app')  
    query = 'SELECT * FROM likes WHERE user_id =%(wid)s AND wish_id =%(id)s;'    
    data = {
        "wid" : session['user_id'],
        "id" : int(wish_id)
        }  
    creater_id = mysql.query_db(query, data)
    if creater_id:
        print(creater_id)
        return redirect('/wishes') 
    else:
        mysql = connectToMySQL("wish_app")
        query = "INSERT into likes (user_id, wish_id, created_at, updated_at) VALUES (%(wid)s, %(id)s, NOw(), NOW())"
        data = {
            "wid" : session["user_id"],
            "id" : int(wish_id)
        }
        mysql.query_db(query, data)
        return redirect('/wishes')



if __name__ == "__main__":
    app.run(debug=True)