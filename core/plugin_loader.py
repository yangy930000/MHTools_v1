import os
import importlib
import inspect
import sys
from typing import List
from core.interfaces import IPlugin

class PluginLoader:
    def __init__(self, plugin_dir: str = "plugins"):
        """
        :param plugin_dir: 插件存放的目录名称，默认为 'plugins'
        """
        self.plugin_dir = plugin_dir
        # 获取绝对路径，确保导入路径正确
        self.base_path = os.path.join(os.getcwd(), plugin_dir)

    def load_all(self) -> List[IPlugin]:
        """
        扫描插件目录，导入并实例化所有有效的插件。
        """
        loaded_plugins = []

        # 1. 确保插件目录存在
        if not os.path.exists(self.base_path):
            print(f"警告: 插件目录 '{self.base_path}' 不存在，已自动创建。")
            os.makedirs(self.base_path)
            return []

        # 2. 遍历目录下的子文件夹
        for item in os.listdir(self.base_path):
            full_path = os.path.join(self.base_path, item)
            
            # 忽略文件和 __pycache__ 等
            if os.path.isdir(full_path) and not item.startswith("__"):
                plugin_instance = self._load_single_plugin(item)
                if plugin_instance:
                    loaded_plugins.append(plugin_instance)

        return loaded_plugins

    def _load_single_plugin(self, package_name: str) -> IPlugin | None:
        """
        尝试加载单个插件包
        """
        try:
            # 动态导入模块，例如: import plugins.session_tracker
            module_path = f"{self.plugin_dir}.{package_name}"
            module = importlib.import_module(module_path)

            plugin_class = None

            # 策略 A (推荐): 检查是否有显式导出的 PLUGIN_CLASS
            if hasattr(module, 'PLUGIN_CLASS'):
                plugin_class = getattr(module, 'PLUGIN_CLASS')
                # 再次校验是否真的实现了接口
                if not issubclass(plugin_class, IPlugin):
                    print(f"错误: {package_name} 的 PLUGIN_CLASS 未继承 IPlugin")
                    return None

            # 策略 B (备选): 自动扫描模块中的类
            else:
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, IPlugin) and 
                        obj is not IPlugin):
                        plugin_class = obj
                        break
            
            if plugin_class:
                print(f"[PluginLoader] 成功加载插件: {package_name}")
                return plugin_class() # 实例化并返回
            else:
                print(f"[PluginLoader] 警告: 在 {package_name} 中未找到有效的插件类")

        except Exception as e:
            # 捕获所有错误，防止一个坏插件导致整个程序崩溃
            print(f"[PluginLoader] 加载插件 {package_name} 失败: {e}")
            import traceback
            traceback.print_exc()
        
        return None