# MP3: ALICE IN BRAINROT LAND 

## PERFORMING A SQL INJECTION 

<p align="center">
<img src="images/Screenshot from 2025-05-10 21-45-54.png" alt="sqlini" width="400" style="border-radius: 12px; outline: 5px solid #d6d6d6;"/>
</p>

<p style="text-align: center; font-weight: bold;">
  SQLini Injectioni
</p>
<p style="text-align: center; font-style: italic;">
  In the land of Brainrotland, not everything is as it seems—especially not the login form.
</p>


```py
res = cur.execute("SELECT id from users WHERE username = '"
            + request.form["username"]
            + "' AND password = '"
            + request.form["password"] + "'")
```

The login part of the web application has a SQL injection security flaw. This happens because the application builds a database query by directly inserting the username and password you enter into the query, without properly protecting those inputs.

Normally, the application takes our username and password and uses them in a database query to check if they're correct. However, if we enter special characters in the username (or password) field, we can trick the database into doing something it's not supposed to.

### WHAT AN ATTACKER CAN DO 
If the attacker enters this in the username field:

<p align="center">
<img src="images/Screenshot from 2025-05-10 21-46-18.png" alt="username" width="400" style="border-radius: 12px; outline: 5px solid #d6d6d6;"/>
</p>

And leaves the password blank, the application puts that directly into the database query which will result to this: 

```sql
SELECT id from users WHERE username = '' OR 1=1--' AND password = ''
```

### WHAT THE DATABASE DOES
- The `OR 1=1` part makes the query always true. 
- The `--` art tells the database to ignore the rest of the query (including the password check).

**Result**

The attacker is logged in as the first user in the database (likely the admin). The application doesn't clean or "sanitize" the input. It just assumes that whatever you type is a normal username and password. But a clever attacker can type in SQL code that changes the meaning of the database query.

<p align="center">
<img src="images/Screenshot from 2025-05-10 21-46-31.png" alt="username" width="400" style="border-radius: 12px; outline: 5px solid #d6d6d6;"/>
</p>

### HOW TO PREVENT IT 

- All database interactions were updated to use parameterized queries.
- Instead of manually constructing SQL strings with user input, the application now uses safe placeholders (`?`) and parameter binding.

```python
# Before (vulnerable):
cur.execute("SELECT id FROM users WHERE username = '" + request.form["username"] + "'")

# After (secure):
cur.execute("SELECT id FROM users WHERE username = ?", (request.form["username"],))
```

## PERFORMING A CSRF ATTACK 

<p align="center">
<img src="images/Screenshot from 2025-05-10 21-46-44.png" alt="csrfino" width="400" style="border-radius: 12px; outline: 5px solid #d6d6d6;"/>

<p style="text-align: center; font-weight: bold;">
  CiSRaFino Attackino
</p>
<p style="text-align: center; font-style: italic;">
  Alice is back—still logged in, still trusting... and now, a target of CisraFino Attackino
</p>


CSRF is a type of attack where a malicious website or web application can force a user's browser to perform an unwanted action on another web application in which the user is currently authenticated.

The web application, built with Python and Flask, has a vulnerability in its "posts" functionality. Specifically, the application doesn't properly validate the origin of the requests to the /posts endpoint.

### WHAT AN ATTACKER CAN DO

To perform the attack, we created a malicious HTML page (named malicious_attack.html).  This page contains an HTML form that, when submitted, sends a POST request to the vulnerable application's /posts endpoint. The form includes a hidden input field named "message" with the value "This is a CSRF attack!". This is the data that we want to submit as "attackers" to the vulnerable application.

```html
<body>
    <h2>CSRF Attack Simulation</h2>
    <form method="POST" action="http://127.0.0.1:5000/posts">
      <input type="hidden" name="message" value="This is a CSRF attack!">
    </form>
    <script>
      // Automatically submit the form after loading the page
      document.forms[0].submit();
    </script>
  </body>
```

Host it on another local server.

<p align="center">
<img src="images/Screenshot from 2025-05-10 21-47-00.png" alt="local" width="400" style="border-radius: 12px; outline: 5px solid #d6d6d6;"/>
</p>

Log in using the default account 

<p align="center">
<img src="images/Screenshot from 2025-05-10 21-47-14.png" alt="login" width="400" style="border-radius: 12px; outline: 5px solid #d6d6d6;"/>
</p>

Alice logs into the vulnerable web application (running on `127.0.0.1:5000`) and their session is active. Crucially, she remains logged in to the vulnerable application. Alice,  while still logged in to the vulnerable application, visits the attacker's malicious page (`127.0.0.1:8080/malicious_attack.html`) in a new browser tab. The malicious page automatically submits the hidden form. This form submission sends a POST request to the vulnerable application's `/posts` endpoint. Because the user is already authenticated with the vulnerable application, the browser automatically includes the user's session cookies in the request to `/posts`.

The vulnerable application receives the request to `/posts`. Because it doesn't check where the request came from (i.e., it lacks CSRF protection), it processes the request as if it came from the legitimate user. The application inserts the message "This is a CSRF attack!" into the "posts" table in the database, associated with the logged-in user.

<p align="center">
<img src="images/Screenshot from 2025-05-10 21-47-24.png" alt="sakses" width="400" style="border-radius: 12px; outline: 5px solid #d6d6d6;"/>
</p>

The attacker's message is successfully posted as if the victim user had done it themselves.

### HOW TO PREVENT IT 

- Flask-WTF was integrated to enable automatic CSRF token generation and validation for all forms.
- A global CSRF protection instance was added using `CSRFProtect`.

```python 
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()
csrf.init_app(app)
```

## PERFORMING A XSS ATTACK 

<p align="center">
<img src="images/Screenshot from 2025-05-10 21-47-36.png" alt="csrfino" width="400" style="border-radius: 12px; outline: 5px solid #d6d6d6;"/>
</p>

<p style="text-align: center; font-weight: bold;">
  Cross-Sitesino Scriptinimo
</p>

XSS is a vulnerability that allows an attacker to inject malicious code, typically JavaScript, into web pages viewed by other users. The web application is vulnerable to XSS in its "posts" functionality. Specifically, it appears that the application doesn't properly sanitize user-provided input before displaying it on the page.

**Vulnerable Code**

```python
@app.route("/home")
def home():
    ...
    if user:
        res = cur.execute("SELECT message FROM posts WHERE user = " + str(user[0]) + ";")
        posts = res.fetchall()
        return render_template("home.html", username=user[1], posts=posts)
```

Because our `home.html` is structured like this:


```html
{% for post in posts %}
  <li>{{ post[0] | safe }}</li>
{% endfor %}
```

The rendered HTML becomes:
```html
<li><script>alert('XSS')</script></li>
```

### WHAT AN ATTACKER CAN DO 

The attacker enters the following payload into the input field for creating a post:

```html
<script>alert('1')</script>
```

The attacker submits this input, attempting to create a new post. The application stores this input in the database. When the web page displays the posts, it retrieves the attacker's input from the database and includes it in the HTML of the page. 

<p align="center">
<img src="images/Screenshot from 2025-05-10 21-47-54.png" alt="sakses" width="400" style="border-radius: 12px; outline: 5px solid #d6d6d6;"/>
</p>

It's fortunate that Cross-Sitesino Scriptinino was simply displaying an alert (`1`) to scare Alice, rather than more dangerous actions such as: stealing sensitive information (like session cookies, which could allow account hijacking), modifying the appearance of the web page, redirecting the user to a malicious website, or installing malware.

### HOW TO PREVENT IT 

- Apply HTML escaping (e.g., using `html.escape()` in Python) before displaying user data. This converts special characters to their HTML entity equivalents, preventing browsers from executing them as code.

#### ADDITIONAL SECURITY ENHANCEMENTS

**Secure Cookie Settings:** 
- `httponly=True`: Prevents JavaScript from accessing session cookies.
- `secure=True`: Ensures cookies are transmitted only over HTTPS.
- `samesite='Strict'`: Blocks cross-origin requests from sending cookies.

**Session Management**
- Replaced insecure or hard-coded session keys with securely generated tokens using `secrets.token_hex()`.
