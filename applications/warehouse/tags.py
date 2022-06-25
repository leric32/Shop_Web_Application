from flask import Blueprint
from applications.models import database, Product
from sqlalchemy import func

tagsBlueprint = Blueprint("tags", __name__)


# @tagsBlueprint.route("/<name>", methods=["GET"])
# def create_tag(name):
#     tag = Tag(name=name)
#     database.session.add(tag)
#     database.session.commit()
#
#     return str(Tag.query.all())
#
#
# @tagsBlueprint.route("/frequency/<number>", methods=["GET"])
# def get_frequency(number=None):
#     count = func.count(Tag.name)
#
#     query = Tag.query.join(ThreadTag).join(Thread) \
#         .group_by(Tag.name).with_entities(Tag.name, count)
#
#     if number is not None:
#         query = query.having(count > int(number))
#
#     result = query.all()
#
#     return str(result)
