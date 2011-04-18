# coding: utf-8

from datetime import date
from django.conf import settings
from django.utils.hashcompat import sha_constructor
from django.utils.http import int_to_base36, base36_to_int


class TokenGenerator(object):
    """
    Generates and validates confirmation tokens
    """
    
    def __init__(self, timeout):
        self.timeout = timeout
    
    def make_token(self, user):
        """
        Returns a token that can be used once to perform activation for a given user
        """
        return self._make_token_with_timestamp(user, self._num_days(self._today()))

    def check_token(self, user, token):
        """
        Check that the token is correct for a given user
        """
        
        # Parse the token
        try:
            ts_b36, hash = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        # Check that the timestamp/uid have not been tampered
        if self._make_token_with_timestamp(user, ts) != token:
            return False

        # Check that the timestamp is within limits
        if (self._num_days(self._today()) - ts) > self.timeout:
            return False

        return True

    def _make_token_with_timestamp(self, user, timestamp):

        # Timestamp is number of days since 2001-1-1.  Converted to
        # base 36, this gives us a 3 digit string until about 2121
        ts_b36 = int_to_base36(timestamp)
        
        # By hashing on the internal state of the user and using state
        # that is sure to change , we produce a hash that will be
        # invalid as soon as it is used.
        # We limit the hash to 20 chars to keep URL short
        hash = sha_constructor(settings.SECRET_KEY + unicode(user.id) + user.is_active + user.email +
                               unicode(timestamp)).hexdigest()[::2]
        return "%s-%s" % (ts_b36, hash)

    def _num_days(self, dt):
        return (dt - date(2001,1,1)).days

    def _today(self):
        return date.today()
