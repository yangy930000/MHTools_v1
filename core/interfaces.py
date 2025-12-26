from abc import ABC, abstractmethod
from PyQt6.QtWidgets import QWidget

class IPlugin(ABC):
    """所有插件必须实现的抽象基类"""

    @property
    @abstractmethod
    def plugin_id(self) -> str:
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        pass

    @abstractmethod
    async def initialize(self, context):
        """
        异步初始化钩子。
        插件应在这里进行数据库模型的注册或其他耗时准备工作。
        :param context: AppContext 实例，提供核心服务
        """
        pass

    @abstractmethod
    def get_widget(self) -> QWidget:
        """返回插件的主界面 Widget"""
        pass

    async def shutdown(self):
        """可选的异步清理钩子"""
        pass