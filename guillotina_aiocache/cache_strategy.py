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

    def get_key(self, oid=None, container=None, id=None, variant=None):
        key = ''
        if oid is not None:
            key = oid
        elif container is not None:
            key = container._p_oid
        if id is not None:
            key += '/' + id
        if variant is not None:
            key += '-' + variant
        return key

    async def get(self, **kwargs):
        key = self.get_key(**kwargs)
        try:
            val = await self._cache.get(key)
            if val is not None:
                logger.debug('Retrieved {} from cache'.format(key))
            return val
        except Exception:
            logger.warn('Error getting cache value', exc_info=True)

    async def set(self, value, **kwargs):
        key = self.get_key(**kwargs)
        try:
            await self._cache.set(key, value)
            logger.debug('set {} in cache'.format(key))
        except Exception:
            logger.warn('Error setting cache value', exc_info=True)

    async def clear(self):
        try:
            await self._cache.clear()
            logger.debug('Cleared cache')
        except Exception:
            logger.warn('Error clearing cache', exc_info=True)

    async def invalidate(self, ob):
        try:
            await self._cache.delete(ob._p_oid)
            if ob.__of__:
                # like an annotiation, invalidate diff
                await self._cache.delete(ob._p_oid)
                await self._cache.delete(
                    self.get_key(oid=ob.__of__, id=ob.__name__,
                                 variant='annotation'))
                await self._cache.delete(
                    self.get_key(oid=ob.__of__, variant='annotation-keys'))
            else:
                await self._cache.delete(
                    self.get_key(container=ob, variant='len'))
                await self._cache.delete(
                    self.get_key(container=ob, variant='keys'))
                await self._cache.delete(
                    self.get_key(container=ob, variant='annotation-keys'))
                await self._cache.delete(
                    self.get_key(container=ob.__parent__, id=ob.id))
            logger.debug('Deleted {} from cache'.format(ob._p_oid))
        except Exception:
            logger.warn('Error invalidating object', exc_info=True)
