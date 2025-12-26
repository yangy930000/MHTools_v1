from PyQt6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NexTool - Game Assistant")
        self.setMinimumSize(800, 600)

        container = QWidget()
        main_layout = QVBoxLayout(container)
        
        # 顶部状态栏（预留）
        self.status_label = QLabel("就绪。")
        main_layout.addWidget(self.status_label)

        # 核心 Tab 区域
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.setCentralWidget(container)

    def load_plugins_ui(self, plugins: list):
        """将加载好的插件 UI 添加到 Tab 中"""
        for plugin in plugins:
            self.tabs.addTab(plugin.get_widget(), plugin.display_name)
        self.status_label.setText(f"已加载 {len(plugins)} 个插件。")