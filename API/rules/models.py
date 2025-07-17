# rules/models.py

from mongoengine import Document, StringField, EmbeddedDocument, EmbeddedDocumentField, ListField,DictField,BooleanField,IntField

class Alert(EmbeddedDocument):
    severity = StringField(required=True)
    type = StringField(required=True)

class Rules(Document):
    rule_id = StringField()
    name = StringField(required=True)
    index = StringField(required=True)
    description = StringField()
    condition = DictField()
    alert = DictField()
    business_service_details = DictField()
    is_deleted = BooleanField(default=False)
    duration = IntField()