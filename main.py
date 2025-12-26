import sys
import asyncio
import qasync
from PyQt6.QtWidgets import QApplication

from core.database import DatabaseManager
from core.context import AppContext
from ui.main_window import MainWindow

# 手动导入插件（在实际框架中，这里会用 importlib 动态扫描 plugins 目录）
from plugins.session_tracker import SessionTrackerPlugin

async def main():
    """异步主函数"""
    # 1. 初始化核心组件
    db_manager = DatabaseManager()
    context = AppContext(db_manager)
    main_window = MainWindow()

    # 2. 异步初始化数据库表结构 (核心改变：不卡 UI)
    print("正在检查数据库结构...")
    await db_manager.initialize_tables()

    # 3. 加载插件 (这里简化为手动列表，实际应为动态扫描)
    plugins_to_load = [
        SessionTrackerPlugin(),
        # 未来在这里添加更多插件...
    ]

    loaded_plugins = []
    for plugin in plugins_to_load:
        # 异步初始化每个插件
        await plugin.initialize(context)
        context.register_plugin(plugin)
        loaded_plugins.append(plugin)

    # 4. 将插件 UI 加载到主窗口
    main_window.load_plugins_ui(loaded_plugins)
    main_window.show()

    # 5. 保持运行直到窗口关闭（qasync 会处理这里）
    await asyncio.Future() 

    # 6. 清理工作
    print("正在关闭应用，清理资源...")
    await db_manager.close()

if __name__ == "__main__":
    # 标准 PyQt 设置
    app = QApplication(sys.argv)
    # 使用 qasync 的事件循环融合 asyncio 和 Qt
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    try:
        # 运行异步入口点
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()