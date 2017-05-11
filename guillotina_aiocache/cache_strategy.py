from guillotina import configure
from guillotina.db.cache.base import BaseCache
from guillotina.db.interfaces import IStorage
from guillotina.db.interfaces import IStorageCache
from aiocache import caches
from guillotina import app_settings
import logging


logger = logging.getLogger('guillotina_aiocache')


@configure.adapter(for_=IStorage, provides=IStorageCache, name="aio")
class AIOCache(BaseCache):

    def __init__(self, storage):
        super().__init__(storage)
        options = app_settings['aiocache']
        options['serializer'] = {
            'class': "guillotina_aiocache.serializers.JsonSerializer"
        }
        caches.set_config({
            'default': options
        })
        self._cache = caches.get('default')

    async def get(self, oid, default=None):
        try:
            val = await self._cache.get(oid)
            if val is not None:
                logger.debug('Retrieved {} from cache'.format(oid))
            return val
        except Exception:
            logger.warn('Error getting cache value', exc_info=True)

    async def set(self, ob, value):
        try:
            await self._cache.set(ob._p_oid, value)
            logger.debug('set {} in cache'.format(ob._p_oid))
        except Exception:
            logger.warn('Error setting cache value', exc_info=True)

    async def get_child(self, oid, id, prefix=''):
        key = prefix + oid + '/' + id
        try:
            val = await self._cache.get(key)
            if val is not None:
                logger.debug('Retrieved {} from cache'.format(key))
            return val
        except Exception:
            logger.warn('Error getting child cache value', exc_info=True)

    async def set_child(self, oid, id, value, prefix=''):
        key = prefix + oid + '/' + id
        try:
            await self._cache.set(key, value)
            logger.debug('Set {} in cache'.format(key))
        except Exception:
            logger.warn('Error setting cache value', exc_info=True)

    async def get_len(self, oid):
        key = oid + '-length'
        try:
            val = await self._cache.get(key)
            if val is not None:
                logger.debug('Retrieved {} from cache'.format(key))
            return val
        except Exception:
            logger.warn('Error getting len', exc_info=True)

    async def set_len(self, oid, val):
        key = oid + '-length'
        try:
            await self._cache.set(key, val)
            logger.debug('Set {} in cache'.format(key))
        except Exception:
            logger.warn('Error setting len', exc_info=True)

    async def clear(self):
        try:
            await self._cache.clear()
            logger.debug('Cleared cache')
        except Exception:
            logger.warn('Error clearing cache', exc_info=True)

    async def invalidate(self, ob):
        try:
            await self._cache.delete(ob._p_oid)
            await self._cache.delete(ob._p_oid + '-length')
            logger.debug('Deleted {} from cache'.format(ob._p_oid))
        except Exception:
            logger.warn('Error invalidating object', exc_info=True)
