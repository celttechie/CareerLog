import datetime
from flask import url_for
from CareerLog import db
from mongoengine import signals
from humanize import naturaltime
import string


# database signal handler for use in models.py
def handler(event):
    """Signal decorator to allow use of callback functions as class
    decorators."""

    def decorator(fn):
        def apply(cls):
            event.connect(fn, sender=cls)
            return cls

        fn.apply = apply
        return fn

    return decorator


# handler to update 'modified' field before save
@handler(signals.pre_save)
def update_modified(sender, document):
    document.modified = datetime.datetime.now()


# handler to create slug from title if one isn't defined
@handler(signals.pre_save)
def set_slug(sender, document):
    if document.slug == "":
        title = document.title.encode('utf-8')
        document.slug = title.lower().translate(
            string.maketrans(" ", "-"), string.punctuation)


# data models for use with MongoEngine, WTForms, and SuperAdmin
# which is a nice DRY way to keep everything in sync.

# db/form model for comments
@update_modified.apply
class Comments(db.EmbeddedDocument):

    created = db.DateTimeField(default=datetime.datetime.now, required=True)
    modified = db.DateTimeField(default=datetime.datetime.now, required=True)
    author = db.StringField(default='Anonymous', verbose_name="Name",
                            max_length=255, required=True)
    body = db.StringField(verbose_name="Comment", required=True)

    def get_naturaltime(self, field):
        return naturaltime(self[field])

    meta = {'allow_inheritance': True,
            'indexes': ['-created', 'modified'],
            'ordering': ['created']
            }


# model for all posts
@set_slug.apply
@update_modified.apply
class Posts(db.Document):

    created = db.DateTimeField(default=datetime.datetime.now(), required=True)
    modified = db.DateTimeField(
        default=datetime.datetime.now(), required=True)
    author = db.StringField(
        default="Anonymous", verbose_name="Name",
        max_length=255, required=True)
    title = db.StringField(
        default=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
        max_length=255, required=True)
    subtitle = db.StringField(max_length=255, required=False)
    slug = db.StringField(max_length=255, required=False, unique=True)
    body = db.StringField(required=True)
    category = db.StringField(max_length=100, default='Note', required=True)
    tags = db.ListField(db.StringField(max_length=50), required=False)
    published = db.BooleanField(default=False)
    comments_allowed = db.BooleanField(default=False)
    comments = db.ListField(db.EmbeddedDocumentField(Comments))

    def get_naturaltime(self, field):
        return naturaltime(self[field])

    def get_absolute_url(self):
        return url_for('post', kwargs={"slug": self.slug})

    def __unicode__(self):
        return self.title

    meta = {
        'allow_inheritance': True,
        'indexes': ['-created', 'modified', 'slug'],
        'ordering': ['-created']
    }


# model for employment data used in resume
class Employment(db.Document):
    start_year = db.IntField(min_value=1900, max_value=2100, required=True)
    start_month = db.IntField(min_value=1, max_value=12, required=True)
    end_year = db.IntField(min_value=1900, max_value=2100)
    end_month = db.IntField(min_value=1, max_value=12)
    employer = db.StringField(max_length=100, required=True)
    position = db.StringField(max_length=100, required=True)
    location = db.StringField(max_length=100, required=True)
    body = db.StringField(required=True)


# model for education data used in resume
class Education(db.Document):
    start_year = db.IntField(min_value=1900, max_value=2100, required=True)
    end_year = db.IntField(min_value=1900, max_value=2100, required=True)
    institution = db.StringField(max_length=100, required=True)
    location = db.StringField(max_length=100)
    fieldofstudy = db.StringField()
    notes = db.StringField()


# model for certifications used in resume
class Certification(db.Document):
    certified_year = db.IntField(min_value=1900, max_value=2100)
    certified_month = db.IntField(min_value=1, max_value=12)
    expire_year = db.IntField(min_value=1900, max_value=2100)
    expire_month = db.IntField(min_value=1, max_value=12)
    authority = db.StringField(max_length=100)
    certification = db.StringField(max_length=100)
    cert_url = db.StringField(max_length=255)
    badge_url = db.StringField(max_length=255)
    notes = db.StringField()
    priority = db.IntField()


# something we might want to implement later??
# class Skills(db.Document):
# class User(db.Document):
#     name = db.StringField(max_length=40)
#     tags = db.ListField(db.ReferenceField('Tag'))
#     password = db.StringField(max_length=40)
#
#     def __unicode__(self):
#         return self.name
