class AppContext:
    """应用上下文，作为 Service Locator，向插件提供核心能力"""
    def __init__(self, db_manager):
        self._db_manager = db_manager
        self._plugins = {}

    @property
    def db_session_factory(self):
        """提供数据库异步会话工厂"""
        return self._db_manager.async_session_factory
    
    def register_plugin(self, plugin):
        self._plugins[plugin.plugin_id] = plugin

    # 未来可以添加更多功能，如全局配置管理器、事件总线等