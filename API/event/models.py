from mongoengine import Document, StringField, DateTimeField, BooleanField, ListField, DictField, ReferenceField
import datetime

class Event(Document):
    """
    Event model stored in MongoDB using MongoEngine.
    """
    event_id = StringField()
    title = StringField(required=True, max_length=255)
    description = StringField()
    logs = ListField()
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    rule_name = StringField()
    severity = StringField()
    resolved = BooleanField(default=False)
    meta = {
        'collection': 'event',
        'ordering': ['-date'],
        'strict': False,
    }

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.utcnow()
        return super(Event, self).save(*args, **kwargs)
