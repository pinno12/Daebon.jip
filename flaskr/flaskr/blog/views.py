from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from flaskr import db
from flaskr.auth.views import login_required
from flaskr.blog.models import Post

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    posts = Post.query.filter_by(author=g.user).order_by(Post.created.desc()).all()
    return render_template("blog/index.html", posts=posts)


def get_post(id, check_author=True):
    post = Post.query.get_or_404(id, f"Post id {id} doesn't exist.")

    if check_author and post.author != g.user:
        abort(403)

    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        weight = request.form["weight"]
        fat = request.form["fat"]
        protein = request.form["protein"]
        error = None
        if not weight:
            error = "weight is required."

        if error is not None:
            flash(error)
        else:
            db.session.add(Post(weight=weight, fat=fat, author=g.user, protein = protein))
            db.session.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        weight = request.form["weight"]
        fat = request.form["fat"]
        protein = request.form["protein"]
       
        error = None

        if not weight:
            error = "weight is required."

        if error is not None:
            flash(error)
        else:
            post.weight = weight
            post.fat = fat
            post.protein = protein
     
            db.session.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    post = get_post(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("blog.index"))
