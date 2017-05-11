from guillotina import configure


app_settings = {
    "aiocache": {
        'cache': "aiocache.SimpleMemoryCache",
        'serializer': {
            'class': "guillotina_aiocache.serializers.JsonSerializer"
        }
    }
}


def includeme(root, settings):
    configure.scan('guillotina_aiocache.cache_strategy')
