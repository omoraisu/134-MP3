import secrets
import sqlite3
from flask import Flask, request, render_template, redirect, session
from flask_wtf.csrf import CSRFProtect
import html

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Required for session and CSRF
csrf = CSRFProtect(app)
con = sqlite3.connect("app.db", check_same_thread=False)

@app.route("/login", methods=["GET", "POST"])
def login():
    cur = con.cursor()
    if request.method == "GET":
        if request.cookies.get("session_token"):
            # Use parameterized query
            res = cur.execute("SELECT username FROM users INNER JOIN sessions ON "
                            "users.id = sessions.user WHERE sessions.token = ?",
                            (request.cookies.get("session_token"),))
            user = res.fetchone()
            if user:
                return redirect("/home")

        return render_template("login.html")
    else:
        # Use parameterized query
        res = cur.execute("SELECT id from users WHERE username = ? AND password = ?",
                        (request.form["username"], request.form["password"]))
        user = res.fetchone()
        if user:
            token = secrets.token_hex()
            # Use parameterized query
            cur.execute("INSERT INTO sessions (user, token) VALUES (?, ?)",
                        (user[0], token))
            con.commit()
            response = redirect("/home")
            response.set_cookie("session_token", token, httponly=True, secure=True, samesite='Strict')
            return response
        else:
            return render_template("login.html", error="Invalid username and/or password!")

@app.route("/")
@app.route("/home")
def home():
    cur = con.cursor()
    if request.cookies.get("session_token"):
        # Use parameterized query
        res = cur.execute("SELECT users.id, username FROM users INNER JOIN sessions ON "
                        "users.id = sessions.user WHERE sessions.token = ?",
                        (request.cookies.get("session_token"),))
        user = res.fetchone()
        if user:
            # Use parameterized query
            res = cur.execute("SELECT message FROM posts WHERE user = ?", (user[0],))
            posts = res.fetchall()
            # Escape HTML in posts
            safe_posts = [(html.escape(post[0]),) for post in posts]
            return render_template("home.html", username=html.escape(user[1]), posts=safe_posts)

    return redirect("/login")

@app.route("/posts", methods=["POST"])
def posts():
    cur = con.cursor()
    if request.cookies.get("session_token"):
        # Use parameterized query
        res = cur.execute("SELECT users.id, username FROM users INNER JOIN sessions ON "
                        "users.id = sessions.user WHERE sessions.token = ?",
                        (request.cookies.get("session_token"),))
        user = res.fetchone()
        if user:
            # Use parameterized query
            cur.execute("INSERT INTO posts (message, user) VALUES (?, ?)",
                        (request.form["message"], user[0]))
            con.commit()
            return redirect("/home")

    return redirect("/login")

@app.route("/logout", methods=["GET"])
def logout():
    cur = con.cursor()
    if request.cookies.get("session_token"):
        # Use parameterized query
        res = cur.execute("SELECT users.id, username FROM users INNER JOIN sessions ON "
                        "users.id = sessions.user WHERE sessions.token = ?",
                        (request.cookies.get("session_token"),))
        user = res.fetchone()
        if user:
            # Use parameterized query
            cur.execute("DELETE FROM sessions WHERE user = ?", (user[0],))
            con.commit()

    response = redirect("/login")
    response.set_cookie("session_token", "", expires=0, httponly=True, secure=True, samesite='Strict')
    return response
