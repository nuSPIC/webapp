from django.db import models
from django.utils.encoding import smart_str

from cPickle import dumps, loads


class SerializedField(models.TextField):
    """
    Field for transparent access to serialized data
    """

    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if not value:
            return {}
        return loads(smart_str(value))

    def get_prep_value(self, value):
        return dumps(value)
