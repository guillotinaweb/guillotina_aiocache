from aiocache.serializers import DefaultSerializer

import asyncpg
import base64
import json


class JsonSerializer(DefaultSerializer):

    @classmethod
    def dumps(cls, value):
        """
        Serialize the received value using ``json.dumps``.

        :param value: dict
        :returns: str
        """
        if isinstance(value, asyncpg.Record):
            value = dict(value)
        if isinstance(value, dict):
            value['state'] = base64.b64encode(value['state']).decode('ascii')
        return json.dumps(value)

    @classmethod
    def loads(cls, value):
        """
        Deserialize value using ``json.loads``.

        :param value: str
        :returns: output of ``json.loads``.
        """
        if value is None:
            return None
        value = json.loads(value)
        if isinstance(value, dict):
            if 'state' in value:
                value['state'] = base64.b64decode(value['state'].encode('ascii'))
        return value
