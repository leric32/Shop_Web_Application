from flask import Blueprint, request
from applications.models import database, Product
from sqlalchemy import and_, or_
from redis import Redis
from applications.configuration import Configuration

threadsBlueprint = Blueprint("threads", __name__)


# @threadsBlueprint.route("/", methods=["GET"])
# def threads():
#     return str(Thread.query.all())
#
#
# @threadsBlueprint.route("/<title>", methods=["GET"])
# def create_thread(title):
#     #thread = Thread(title=title)
#     #database.session.add(thread)
#     #database.session.commit()
#
#     #return str(Thread.query.all())
#
#     with Redis(host=Configuration.REDIS_HOST) as redis:
#         redis.rpush(Configuration.REDIS_THREADS_LIST, title)
#
#     return "Thread pending approval!"
#
#
# @threadsBlueprint.route("/<thread_id>/<tag_id>", methods=["GET"])
# def add_tag_to_thread(thread_id, tag_id):
#     thread_tag = ThreadTag(threadId=thread_id, tagId=tag_id)
#     database.session.add(thread_tag)
#     database.session.commit()
#
#     return str(Thread.query.all())
#
#
# @threadsBlueprint.route("/withWordsInTitle", methods=["GET"])
# def getThreadsWithWordsInTitle():
#     words = [ item.strip() for item in request.args["words"].split(",")]
#
#     threads = Thread.query.filter(
#         and_ (
#             *[Thread.title.like(f"%{word}%") for word in words]
#         )
#     ).all()
#
#     return str(threads)
#
#
# @threadsBlueprint.route("/withTags", methods=["GET"])
# def get_thread_with_tags():
#     tags = [item.strip() for item in request.args["tags"].split(",")]
#
#     threads = Thread.query.join(ThreadTag).join(Tag).filter(
#         or_(
#             *[Tag.name == tag for tag in tags]
#         )
#     ).all()
#
#     return str(threads)
