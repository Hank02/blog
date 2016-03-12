from flask import render_template
from flask import request, redirect, url_for
from flask import flash
from flask.ext.login import login_user, login_required, current_user, logout_user
from werkzeug.security import check_password_hash
from blog import app
from .database import session, Entry, User

PAGINATE_BY = 10

# view multiple entries with "older" and "newer" buttons at bottom
@app.route("/")
@app.route("/page/<int:page>")
def entries(page = 1):
    # zero-indexed page
    page_index = page - 1
    
    count = session.query(Entry).count()
    
    start = page_index * PAGINATE_BY
    end = start + PAGINATE_BY
    
    total_pages = (count - 1) / PAGINATE_BY + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0
    
    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    entries = entries[start:end]
    
    return render_template("entries.html", 
        entries = entries,
        has_next = has_next,
        has_prev = has_prev,
        page = page,
        total_pages = total_pages
    )


# add an entry -----------------------------------
# first generate emtpy forms
@app.route("/entry/add", methods = ["GET"])
@login_required
def add_entry_get():
    return render_template("add_entry.html")

# submit text to db
@app.route("/entry/add", methods = ["POST"])
@login_required
def add_entry_post():
    entry = Entry(
        title = request.form["title"],
        content = request.form["content"],
        author = current_user
    )
    # add and commit text to db
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))

# view a single entry at a time --------------------
@app.route("/entry/<int:id>")
def single_entry(id):
    # start session with current id
    entry = session.query(Entry).get(id)
    # render html with entire contents of session
    return render_template("single_entry.html",
        entry = entry
    )


# edit an existing entry -------------------------
# first get old text and display
@app.route("/entry/edit/<int:id>", methods = ["GET"])
@login_required
def edit_entry_get(id):
    # create session with current id
    entry = session.query(Entry).get(id)
    return render_template("edit_entry.html",
        # pass old-text to variables so they are available in html template
        title = entry.title,
        content = entry.content
    )

# submit edited text
@app.route("/entry/edit/<int:id>", methods = ["POST"])
@login_required
def edit_entry_post(id):
    # get text from form
    entry = Entry(
        title = request.form["title"],
        content = request.form["content"],
    )
    # create session with current id
    edited = session.query(Entry).get(id)
    # store edited text in respective filed
    edited.title = entry.title
    edited.content = entry.content
    # add and commit changes to db
    session.add(edited)
    session.commit()
    # redirect to main screen
    return redirect(url_for("entries"))

# delete entry -----------------------------------------
@app.route("/entry/delete/<int:id>", methods = ["GET"])
@login_required
def delete_entry(id):
    # start session with current id
    entry = session.query(Entry).get(id)
    # render html with entire contents of session
    return render_template("delete_entry.html",
        entry = entry
    )

# confirm deletion of selected entry
@app.route("/entry/delete/<int:id>", methods=["POST"])
@login_required
def delete_entry_confirm(id):
    # start session with current id
    entry = session.query(Entry).get(id)
    session.delete(entry)
    session.commit()
    return redirect(url_for("entries"))

# add login feature ------------------------------------
@app.route("/login", methods = ["GET"])
def login_get():
    return render_template("login.html")

@app.route("/login", methods = ["POST"])
def login_post():
    # read email and password from request.form dictionary
    email = request.form["email"]
    password = request.form["password"]
    # look for user object with matching email address
    user = session.query(User).filter_by(email = email).first()
    # make sure the user exists and that entered password matches stored password (hash)
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))
    
    # if login succeeds, store cookie and redirect user
    login_user(user)
    return redirect(request.args.get('next') or url_for("entries"))

# log user out ----------------------------------------------
@app.route("/logout")
def logout():
    logout_user()
    return render_template("logout.html")