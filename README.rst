Introduction
============

`guillotina_aiocache` implements aiocache into guillotina



Configuration
-------------

app_settings for this::

    {
        "aiocache": {
            'cache': "aiocache.RedisCache",
            'endpoint': "127.0.0.1",
            'port': 6379,
            'timeout': 1,
            'plugins': [
                {'class': "aiocache.plugins.HitMissRatioPlugin"},
                {'class': "aiocache.plugins.TimingPlugin"}
            ]
        }
    }
