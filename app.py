from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "replace_this_with_a_random_secret"  # change before hosting
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///airdrops.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Simple admin credentials (change before hosting)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password"

class Airdrop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    network = db.Column(db.String(80), nullable=True)
    category = db.Column(db.String(80), nullable=True)
    description = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(300), nullable=False)

# Home + search
@app.route("/")
def index():
    q = request.args.get("q", "")
    if q:
        airdrops = Airdrop.query.filter(Airdrop.name.contains(q) | Airdrop.description.contains(q)).order_by(Airdrop.id.desc()).all()
    else:
        airdrops = Airdrop.query.order_by(Airdrop.id.desc()).all()
    return render_template("index.html", airdrops=airdrops, q=q)

# Detail page
@app.route("/detail/<int:airdrop_id>")
def detail(airdrop_id):
    airdrop = Airdrop.query.get_or_404(airdrop_id)
    return render_template("detail.html", airdrop=airdrop)

# Submit (public)
@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        name = request.form["name"]
        network = request.form.get("network", "")
        category = request.form.get("category", "")
        description = request.form["description"]
        link = request.form["link"]
        new = Airdrop(name=name, network=network, category=category, description=description, link=link)
        db.session.add(new)
        db.session.commit()
        flash("Airdrop submitted — thank you!", "success")
        return redirect(url_for("index"))
    return render_template("submit.html")

# Admin login/logout
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            flash("Welcome, admin.", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid credentials.", "danger")
            return render_template("login.html")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    flash("Logged out.", "info")
    return redirect(url_for("index"))

# Admin dashboard (protected)
def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            flash("You must be logged in as admin.", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/admin")
@admin_required
def admin_dashboard():
    q = request.args.get("q", "")
    if q:
        airdrops = Airdrop.query.filter(Airdrop.name.contains(q) | Airdrop.description.contains(q)).order_by(Airdrop.id.desc()).all()
    else:
        airdrops = Airdrop.query.order_by(Airdrop.id.desc()).all()
    return render_template("admin_dashboard.html", airdrops=airdrops, q=q)

@app.route("/admin/add", methods=["GET", "POST"])
@admin_required
def admin_add():
    if request.method == "POST":
        name = request.form["name"]
        network = request.form.get("network", "")
        category = request.form.get("category", "")
        description = request.form["description"]
        link = request.form["link"]
        new = Airdrop(name=name, network=network, category=category, description=description, link=link)
        db.session.add(new)
        db.session.commit()
        flash("Airdrop added.", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_add.html")

@app.route("/admin/edit/<int:airdrop_id>", methods=["GET", "POST"])
@admin_required
def admin_edit(airdrop_id):
    airdrop = Airdrop.query.get_or_404(airdrop_id)
    if request.method == "POST":
        airdrop.name = request.form["name"]
        airdrop.network = request.form.get("network", "")
        airdrop.category = request.form.get("category", "")
        airdrop.description = request.form["description"]
        airdrop.link = request.form["link"]
        db.session.commit()
        flash("Airdrop updated.", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_edit.html", airdrop=airdrop)

@app.route("/admin/delete/<int:airdrop_id>", methods=["POST"])
@admin_required
def admin_delete(airdrop_id):
    airdrop = Airdrop.query.get_or_404(airdrop_id)
    db.session.delete(airdrop)
    db.session.commit()
    flash("Airdrop deleted.", "info")
    return redirect(url_for("admin_dashboard"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
