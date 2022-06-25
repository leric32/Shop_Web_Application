from flask import Blueprint, request
from applications.models import Product
import io
import csv

commentsBlueprint = Blueprint("comments", __name__)


# @commentsBlueprint.route("/<thread_id>/<content>", methods=["GET"])
# def add_comment(thread_id, content):
#     comment = Comment(threadId = thread_id, content=content)
#     database.session.add(comment)
#     database.session.commit()
#
#     return str(Thread.query.all())
#
# @commentsBlueprint.route("/file", methods = ["POST"])
# def upload_file_with_comments():
#     content = request.files["file"].stream.read().decode("utf-8")
#     stream = io.StringIO(content)
#     reader = csv.reader(stream)
#
#     comments = []
#     for row in reader:
#         comment = Comment( threadId= int(row[0]), content= row[1])
#         comments.append(comment)
#
#     database.session.add_all(comments)
#     database.session.commit()
#
#     return str(Comment.query.all())
#
# @commentsBlueprint.route("/commentsForThread/<threadId>", methods=["GET"])
# def get_comments_for_thread(threadId):
#     comments = Comment.query.filter(Comment.threadId == threadId).all()
#
#     return str(comments)
