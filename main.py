# -*- coding: utf-8 -*-
"""
定时助手 - 支持定时关机和定时休眠
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import subprocess
import datetime
import sys
import os


class ShutdownTimer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("定时关机助手")
        self.root.geometry("380x400")
        self.root.resizable(False, False)

        # 设置图标（可选）
        try:
            self.root.iconbitmap(default='')
        except:
            pass

        # 状态变量
        self.running = False
        self.remaining = 0
        self.warning_shown = False
        self.timer_thread = None
        self.action_var = None  # 在create_widgets中初始化

        self.create_widgets()
        self.center_window()

    def center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')

    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        title_label = ttk.Label(main_frame, text="定时助手", font=("微软雅黑", 16, "bold"))
        title_label.pack(pady=(0, 15))

        # 操作类型选择
        action_frame = ttk.LabelFrame(main_frame, text="操作类型", padding="8")
        action_frame.pack(fill=tk.X, pady=(0, 8))

        self.action_var = tk.StringVar(value="shutdown")
        self.shutdown_rb = ttk.Radiobutton(action_frame, text="关机", variable=self.action_var,
                        value="shutdown")
        self.shutdown_rb.pack(side=tk.LEFT, padx=30)
        self.hibernate_rb = ttk.Radiobutton(action_frame, text="休眠", variable=self.action_var,
                        value="hibernate")
        self.hibernate_rb.pack(side=tk.LEFT, padx=30)

        # 模式选择
        mode_frame = ttk.LabelFrame(main_frame, text="定时模式", padding="8")
        mode_frame.pack(fill=tk.X, pady=(0, 8))

        self.mode_var = tk.StringVar(value="countdown")
        ttk.Radiobutton(mode_frame, text="倒计时", variable=self.mode_var,
                        value="countdown", command=self.on_mode_change).pack(side=tk.LEFT, padx=20)
        ttk.Radiobutton(mode_frame, text="指定时间", variable=self.mode_var,
                        value="scheduled", command=self.on_mode_change).pack(side=tk.LEFT, padx=20)

        # 时间输入区域
        self.time_frame = ttk.LabelFrame(main_frame, text="设置时间", padding="8")
        self.time_frame.pack(fill=tk.X, pady=(0, 8))

        # 倒计时输入
        self.countdown_frame = ttk.Frame(self.time_frame)
        self.countdown_frame.pack()

        ttk.Label(self.countdown_frame, text="时:").pack(side=tk.LEFT)
        self.hour_var = tk.StringVar(value="0")
        self.hour_spin = ttk.Spinbox(self.countdown_frame, from_=0, to=23, width=3,
                                     textvariable=self.hour_var, format="%02.0f")
        self.hour_spin.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(self.countdown_frame, text="分:").pack(side=tk.LEFT)
        self.minute_var = tk.StringVar(value="30")
        self.minute_spin = ttk.Spinbox(self.countdown_frame, from_=0, to=59, width=3,
                                       textvariable=self.minute_var, format="%02.0f")
        self.minute_spin.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(self.countdown_frame, text="秒:").pack(side=tk.LEFT)
        self.second_var = tk.StringVar(value="0")
        self.second_spin = ttk.Spinbox(self.countdown_frame, from_=0, to=59, width=3,
                                       textvariable=self.second_var, format="%02.0f")
        self.second_spin.pack(side=tk.LEFT)

        # 指定时间输入
        self.scheduled_frame = ttk.Frame(self.time_frame)

        ttk.Label(self.scheduled_frame, text="执行时间:").pack(side=tk.LEFT)
        self.time_hour_var = tk.StringVar(value="23")
        self.time_hour_spin = ttk.Spinbox(self.scheduled_frame, from_=0, to=23, width=3,
                                          textvariable=self.time_hour_var, format="%02.0f")
        self.time_hour_spin.pack(side=tk.LEFT, padx=(10, 0))

        ttk.Label(self.scheduled_frame, text=":").pack(side=tk.LEFT)
        self.time_minute_var = tk.StringVar(value="00")
        self.time_minute_spin = ttk.Spinbox(self.scheduled_frame, from_=0, to=59, width=3,
                                            textvariable=self.time_minute_var, format="%02.0f")
        self.time_minute_spin.pack(side=tk.LEFT)

        # 状态显示
        self.status_frame = ttk.LabelFrame(main_frame, text="状态", padding="8")
        self.status_frame.pack(fill=tk.X, pady=(0, 8))

        self.status_label = ttk.Label(self.status_frame, text="就绪", font=("微软雅黑", 10))
        self.status_label.pack()

        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        self.start_btn = ttk.Button(button_frame, text="开始", command=self.start_shutdown)
        self.start_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        self.cancel_btn = ttk.Button(button_frame, text="取消", command=self.cancel_shutdown, state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        self.close_btn = ttk.Button(button_frame, text="关闭", command=self.on_close)
        self.close_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

    def on_mode_change(self):
        """模式切换"""
        if self.running:
            messagebox.showwarning("警告", "正在计时中，请先取消后再切换模式")
            self.mode_var.set("countdown" if self.remaining > 0 else "scheduled")
            return

        # 隐藏所有输入框
        self.countdown_frame.pack_forget()
        self.scheduled_frame.pack_forget()

        # 显示对应输入框
        if self.mode_var.get() == "countdown":
            self.countdown_frame.pack()
        else:
            self.scheduled_frame.pack()

    def start_shutdown(self):
        """开始定时任务"""
        if self.running:
            return

        try:
            if self.mode_var.get() == "countdown":
                hours = int(self.hour_var.get())
                minutes = int(self.minute_var.get())
                seconds = int(self.second_var.get())
                total_seconds = hours * 3600 + minutes * 60 + seconds

                if total_seconds == 0:
                    messagebox.showwarning("警告", "请设置时间")
                    return

                # 关机时提前调度，休眠时等倒计时结束再执行
                if self.action_var.get() == "shutdown":
                    self.set_windows_shutdown(total_seconds)
                self.remaining = total_seconds

            else:  # scheduled mode
                target_hour = int(self.time_hour_var.get())
                target_minute = int(self.time_minute_var.get())

                now = datetime.datetime.now()
                target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

                if target <= now:
                    target += datetime.timedelta(days=1)

                total_seconds = int((target - now).total_seconds())
                if self.action_var.get() == "shutdown":
                    self.set_windows_shutdown(total_seconds)
                self.remaining = total_seconds

            # 更新界面状态
            self.running = True
            self.warning_shown = False
            self.start_btn.config(state=tk.DISABLED)
            self.cancel_btn.config(state=tk.NORMAL)
            self.set_inputs_state(tk.DISABLED)

            # 启动后台计时
            self.timer_thread = threading.Thread(target=self.timer_countdown, daemon=True)
            self.timer_thread.start()

            self.update_status()

        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")

    def set_windows_shutdown(self, seconds):
        """设置Windows关机或休眠"""
        try:
            if self.action_var.get() == "hibernate":
                # 休眠：使用 rundll32 命令
                result = subprocess.run(
                    ['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'],
                    capture_output=True,
                    text=True,
                    shell=True
                )
            else:
                # 关机：使用 shutdown 命令
                result = subprocess.run(
                    ['shutdown', '/s', '/t', str(seconds)],
                    capture_output=True,
                    text=True,
                    shell=True
                )
            if result.returncode != 0:
                action_name = "休眠" if self.action_var.get() == "hibernate" else "关机"
                messagebox.showerror("错误", f"设置{action_name}失败: {result.stderr}")
        except Exception as e:
            action_name = "休眠" if self.action_var.get() == "hibernate" else "关机"
            messagebox.showerror("错误", f"设置{action_name}失败: {str(e)}")

    def cancel_shutdown(self):
        """取消定时任务"""
        if not self.running:
            return

        try:
            subprocess.run(['shutdown', '/a'], capture_output=True, shell=True)
        except:
            pass

        self.running = False
        self.remaining = 0
        self.start_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.set_inputs_state(tk.NORMAL)
        self.action_var.set("shutdown")  # 重置为默认
        self.status_label.config(text="已取消")

    def set_inputs_state(self, state):
        """设置输入框状态"""
        self.hour_spin.config(state=state)
        self.minute_spin.config(state=state)
        self.second_spin.config(state=state)
        self.time_hour_spin.config(state=state)
        self.time_minute_spin.config(state=state)
        self.shutdown_rb.config(state=state)
        self.hibernate_rb.config(state=state)

    def timer_countdown(self):
        """后台计时"""
        while self.running and self.remaining > 0:
            self.remaining -= 1
            self.root.after(0, self.update_status)

            # 操作前1分钟提醒
            if self.remaining == 60 and not self.warning_shown:
                self.warning_shown = True
                self.root.after(0, self.show_warning)

            if self.remaining <= 0:
                # 倒计时结束，执行操作（休眠时在这里执行）
                if self.action_var.get() == "hibernate":
                    self.execute_action()
                # 重置UI状态
                self.running = False
                self.root.after(0, self.reset_ui)
                break

            # 精确等待1秒
            threading.Event().wait(1)

    def reset_ui(self):
        """重置UI状态"""
        self.start_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.set_inputs_state(tk.NORMAL)
        action_name = "休眠" if self.action_var.get() == "hibernate" else "关机"
        self.status_label.config(text=f"{action_name}已执行")
        self.root.title("定时助手")

    def update_status(self):
        """更新状态显示"""
        action_name = "休眠" if self.action_var.get() == "hibernate" else "关机"
        if self.running and self.remaining > 0:
            hours = self.remaining // 3600
            minutes = (self.remaining % 3600) // 60
            seconds = self.remaining % 60
            self.status_label.config(text=f"剩余时间: {hours:02d}:{minutes:02d}:{seconds:02d} ({action_name})")

            # 更新标题栏显示剩余时间
            self.root.title(f"定时{action_name} - {hours:02d}:{minutes:02d}:{seconds:02d}")
        elif not self.running:
            self.root.title("定时助手")

    def execute_action(self):
        """执行操作（休眠）"""
        try:
            subprocess.run(
                ['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'],
                shell=True
            )
        except Exception as e:
            messagebox.showerror("错误", f"执行休眠失败: {str(e)}")

    def show_warning(self):
        """操作前提醒"""
        action_name = "休眠" if self.action_var.get() == "hibernate" else "关机"
        if messagebox.askyesno(f"{action_name}提醒",
                               f"电脑将在1分钟后自动{action_name}！\n是否取消？",
                               icon=messagebox.WARNING):
            self.cancel_shutdown()

    def on_close(self):
        """关闭程序"""
        if self.running:
            action_name = "休眠" if self.action_var.get() == "hibernate" else "关机"
            if messagebox.askyesno("确认", f"定时任务正在运行，确定要关闭程序吗？\n（{action_name}任务将继续在后台运行）"):
                self.root.destroy()
        else:
            self.root.destroy()

    def run(self):
        """运行程序"""
        self.root.mainloop()


if __name__ == "__main__":
    app = ShutdownTimer()
    app.run()
