import asyncio
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt6.QtCore import QTimer, Qt
from qasync import asyncSlot
from datetime import datetime, timedelta

# 导入业务服务
from .service import SessionService

class SessionTrackerWidget(QWidget):
    def __init__(self, session_service: SessionService):
        super().__init__()
        self.service = session_service
        self._start_time_anchor = None # 用于 UI 计时显示

        self.init_ui()
        
        # UI 计时器 (仅用于刷新界面显示的时间，不涉及数据库)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer_display)

        # 初始化加载数据
        QTimer.singleShot(0, self.load_history_data)

    def init_ui(self):
        layout = QVBoxLayout(self)

        # --- 顶部控制区 ---
        control_layout = QHBoxLayout()
        self.game_name_input = QLineEdit()
        self.game_name_input.setPlaceholderText("输入正在游玩的游戏名称...")
        
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        
        self.btn_action = QPushButton("开始记录")
        self.btn_action.setFixedHeight(35)
        # 【关键】连接到异步槽函数
        self.btn_action.clicked.connect(self.on_action_clicked)

        control_layout.addWidget(QLabel("游戏:"))
        control_layout.addWidget(self.game_name_input)
        control_layout.addWidget(self.timer_label)
        control_layout.addWidget(self.btn_action)
        layout.addLayout(control_layout)

        # --- 中部历史列表区 ---
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["游戏名称", "开始时间", "结束时间", "时长"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(QLabel("最近历史:"))
        layout.addWidget(self.table)

    def update_ui_state(self, is_tracking):
        if is_tracking:
            self.btn_action.setText("停止记录")
            self.btn_action.setStyleSheet("background-color: #ffcccc;") # 红色系
            self.game_name_input.setEnabled(False)
            self.timer.start(1000)
        else:
            self.btn_action.setText("开始记录")
            self.btn_action.setStyleSheet("") # 恢复默认
            self.game_name_input.setEnabled(True)
            self.timer.stop()
            self.timer_label.setText("00:00:00")

    def update_timer_display(self):
        if self._start_time_anchor:
            now = datetime.now()
            delta = now - self._start_time_anchor
            # 格式化为 HH:MM:SS
            total_seconds = int(delta.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.timer_label.setText(f"{hours:02}:{minutes:02}:{seconds:02}")

    # =========== 异步核心交互区 ===========

    @asyncSlot() # 使用 qasync 的装饰器，允许这里的函数是 async 的
    async def on_action_clicked(self):
        """处理按钮点击，调用后台异步服务"""
        self.btn_action.setEnabled(False) # 防止重复点击
        try:
            if not self.service.is_tracking():
                # 开始动作
                game_name = self.game_name_input.text().strip()
                if not game_name:
                    QMessageBox.warning(self, "提示", "请输入游戏名称")
                    return
                
                # 调用异步服务
                session = await self.service.start_session(game_name)
                # 记录开始时间用于 UI 显示
                self._start_time_anchor = session.start_time
                if self._start_time_anchor.tzinfo is None:
                     self._start_time_anchor = self._start_time_anchor.astimezone()
                
                self.update_ui_state(True)
            else:
                # 停止动作
                await self.service.stop_session()
                self.update_ui_state(False)
                self._start_time_anchor = None
                # 刷新列表
                await self.load_history_data()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"操作失败: {str(e)}")
            # 在实际生产中，这里应该记录日志
            import traceback
            traceback.print_exc()
        finally:
             self.btn_action.setEnabled(True)

    @asyncSlot()
    async def load_history_data(self):
        """异步加载历史数据并填充表格"""
        sessions = await self.service.get_recent_history()
        self.table.setRowCount(0)
        for row_idx, session in enumerate(sessions):
            self.table.insertRow(row_idx)
            
            # 格式化时间显示
            start_str = session.start_time.strftime("%Y-%m-%d %H:%M")
            end_str = session.end_time.strftime("%H:%M") if session.end_time else "-"
            duration_str = str(timedelta(seconds=session.duration_seconds))

            self.table.setItem(row_idx, 0, QTableWidgetItem(session.game_name))
            self.table.setItem(row_idx, 1, QTableWidgetItem(start_str))
            self.table.setItem(row_idx, 2, QTableWidgetItem(end_str))
            self.table.setItem(row_idx, 3, QTableWidgetItem(duration_str))