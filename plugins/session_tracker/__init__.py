from PyQt6.QtWidgets import QWidget
from core.interfaces import IPlugin
from .ui import SessionTrackerWidget
from .service import SessionService
# 重要：导入 models 以便 SQLAlchemy 知道它们的存在
from . import models 

class SessionTrackerPlugin(IPlugin):
    plugin_id = "session_tracker"
    display_name = "游戏会话追踪"

    def __init__(self):
        self._widget = None
        self._service = None

    async def initialize(self, context):
        print(f"[{self.display_name}] 正在异步初始化...")
        # 1. 从上下文获取 DB 会话工厂
        session_factory = context.db_session_factory
        # 2. 初始化业务服务层
        self._service = SessionService(session_factory)
        # 3. 初始化 UI，并将服务层注入进 UI
        # 注意 UI 创建必须在主线程，但这里是在 async 环境中，没问题
        self._widget = SessionTrackerWidget(self._service)
        print(f"[{self.display_name}] 初始化完成。")

    def get_widget(self) -> QWidget:
        return self._widget

# 导出插件类以便加载器识别
PLUGIN_CLASS = SessionTrackerPlugin