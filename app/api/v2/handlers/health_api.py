import platform
import psutil
import time
import os
from aiohttp import web
from aiohttp_apispec import docs

from app.api.v2.handlers.base_api import BaseApi
from app.api.v2.schemas.base_schemas import BaseGetAllQuerySchema


class HealthApi(BaseApi):
    """
    Health check API for monitoring Caldera's status
    """

    def __init__(self, services):
        super().__init__(services)
        self.data_svc = services.get('data_svc')
        self.app_svc = services.get('app_svc')
        self.start_time = time.time()
        
    def add_routes(self, app):
        """
        Add routes to the API app
        """
        router = app.router
        router.add_get('/health', self.get_health)

    @docs(tags=['health'], summary='Get health status')
    async def get_health(self, request):
        """
        Get the health status of the Caldera server
        """
        try:
            # Basic health check
            health_data = {
                'status': 'ok',
                'version': self.get_version(),
                'uptime': self.get_uptime(),
                'system': self.get_system_info(),
                'resources': self.get_resource_usage(),
                'components': await self.get_component_status()
            }
            return web.json_response(health_data)
        except Exception as e:
            return web.json_response({
                'status': 'error',
                'error': str(e)
            }, status=500)

    def get_version(self):
        """Get Caldera version"""
        from app import version
        return version.get_version()

    def get_uptime(self):
        """Get server uptime in seconds"""
        return int(time.time() - self.start_time)

    def get_system_info(self):
        """Get basic system information"""
        return {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'hostname': platform.node()
        }

    def get_resource_usage(self):
        """Get resource usage information"""
        process = psutil.Process(os.getpid())
        return {
            'cpu_percent': process.cpu_percent(),
            'memory_percent': process.memory_percent(),
            'memory_info': {
                'rss': process.memory_info().rss,
                'vms': process.memory_info().vms
            },
            'threads': process.num_threads(),
            'connections': len(process.connections())
        }

    async def get_component_status(self):
        """Get status of various Caldera components"""
        components = {
            'data_service': True,
            'file_service': True,
            'contact_service': True,
            'plugins': {}
        }
        
        # Check plugins
        plugins = await self.data_svc.locate('plugins', match=dict(enabled=True))
        for plugin in plugins:
            components['plugins'][plugin.name] = True
            
        return components
