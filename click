import tkinter as tk
from tkinter import ttk
import numpy as np
import mss
import keyboard
import threading
import time
import win32api, win32con
import pygetwindow as gw

class ProSniperV4_1:
    def __init__(self, root):
        self.root = root
        self.root.title("⚡C")
        self.root.geometry("420x820")
        self.root.attributes("-topmost", True)

        self.is_running = False
        self.target_window = None
        self.relative_coords = []  
        self.refresh_coord = None  
        
        self.target_rgb = None 
        self.tolerance = 60 
        self.click_lock = threading.Lock()

        self.setup_ui()
        threading.Thread(target=self.hotkey_listener, daemon=True).start()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. 모드 선택
        ttk.Label(main_frame, text="[실행 모드 선택]", font=("Arial", 10, "bold")).pack(anchor="w")
        self.comm_mode = tk.StringVar(value="websocket")
        mode_frame = ttk.Frame(main_frame)
        mode_frame.pack(fill=tk.X, pady=5)
        ttk.Radiobutton(mode_frame, text="색상감지", variable=self.comm_mode, value="websocket").pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="새로고침+색상감지", variable=self.comm_mode, value="refresh").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="무지성 광클", variable=self.comm_mode, value="raw").pack(side=tk.LEFT)

        # 2. 색상 설정 표시
        ttk.Label(main_frame, text="[타겟 색상 설정]", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
        color_info_frame = ttk.Frame(main_frame)
        color_info_frame.pack(fill=tk.X, pady=5)
        
        self.color_preview = tk.Label(color_info_frame, text="색상 미지정", width=12, relief="ridge", bg="#dddddd")
        self.color_preview.pack(side=tk.LEFT)
        self.color_label = ttk.Label(color_info_frame, text=" RGB: (---, ---, ---)")
        self.color_label.pack(side=tk.LEFT, padx=5)

        guide_text = (
            "Shift + F : 활성화 창 고정\n"
            "Shift + D : 마우스 위치 색상을 타겟으로 등록\n"
            "Shift + R : 새로고침 버튼 위치 등록 (필요시)\n"
            "Shift + A : 클릭할 위치 추가\n"
            "Shift + C : 최근 추가 제거\n"
            "Shift + E : 전체 초기화\n"
            "Shift + S : 매크로 시작/중지\n"
        )
        ttk.Label(main_frame, text="[단축키]", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))

        ttk.Label(main_frame, text=guide_text, justify=tk.LEFT, foreground="#555555").pack(anchor="w")

        self.status_label = ttk.Label(main_frame, text="상태: 대기 중", font=("Arial", 11, "bold"), foreground="blue")
        self.status_label.pack(pady=10)

        self.coord_listbox = tk.Listbox(main_frame, height=8, font=("Consolas", 9))
        self.coord_listbox.pack(fill=tk.X, pady=5)

        self.log_box = tk.Text(main_frame, height=12, width=55, font=("Consolas", 8), bg="#f8f9fa")
        self.log_box.pack(pady=10)

    def log(self, message):
        self.log_box.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_box.see(tk.END)

    def set_target_color(self):
        with mss.mss() as sct:
            abs_x, abs_y = win32api.GetCursorPos()
            img = np.array(sct.grab({"top": abs_y, "left": abs_x, "width": 1, "height": 1}))
            b, g, r = img[0][0][:3]
            self.target_rgb = (int(r), int(g), int(b))
            hex_color = '#%02x%02x%02x' % self.target_rgb
            self.color_preview.config(bg=hex_color, text="등록 완료")
            self.color_label.config(text=f" RGB: {self.target_rgb}")
            self.log(f"타겟 색상 등록 완료")

    def fast_click(self, x, y):
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    def monitor_worker(self, rx, ry):
        """각 좌표를 독립적으로 감시하여 클릭"""
        with mss.mss() as sct:
            mode = self.comm_mode.get()
            while self.is_running:
                win_l, win_t = self.target_window.left, self.target_window.top
                curr_x, curr_y = win_l + rx, win_t + ry
                
                if mode == "raw":
                    self.fast_click(curr_x, curr_y)
                    time.sleep(0.05)
                    continue

                if self.target_rgb:
                    img = np.array(sct.grab({"top": curr_y, "left": curr_x, "width": 1, "height": 1}))
                    b, g, r = img[0][0][:3]
                    dist = np.sqrt((int(r)-self.target_rgb[0])**2 + (int(g)-self.target_rgb[1])**2 + (int(b)-self.target_rgb[2])**2)
                    
                    if dist < self.tolerance:
                        if self.click_lock.acquire(blocking=False):
                            try:
                                self.fast_click(curr_x, curr_y)
                                self.log(f"좌표({rx}, {ry}) 클릭 성공!")
                            finally:
                                self.click_lock.release()
                        time.sleep(.01) # 한 번 클릭 후 잠시 대기
                
                time.sleep(0.01)

    def refresh_loop(self):
        while self.is_running:
            if self.refresh_coord:
                win_l, win_t = self.target_window.left, self.target_window.top
                self.fast_click(win_l + self.refresh_coord[0], win_t + self.refresh_coord[1])
            time.sleep(3) # 새로고침 주기

    def start_macro(self):
        if not self.target_window or not self.relative_coords:
            self.log("창 고정과 좌표 등록이 필요합니다."); self.is_running = False; return
        if self.comm_mode.get() != "raw" and not self.target_rgb:
            self.log("타겟 색상을 먼저 등록하세요."); self.is_running = False; return

        mode = self.comm_mode.get()
        self.log(f"[{mode}] 모드 시작")
        
        # 등록된 모든 좌표에 대해 개별 쓰레드 생성 (동시 감시)
        for rx, ry in self.relative_coords:
            threading.Thread(target=self.monitor_worker, args=(rx, ry), daemon=True).start()

        if mode == "refresh" and self.refresh_coord:
            threading.Thread(target=self.refresh_loop, daemon=True).start()

    def hotkey_listener(self):
        while True:
            if keyboard.is_pressed('shift'):
                if keyboard.is_pressed('f'):
                    active_win = gw.getActiveWindow()
                    if active_win: 
                        self.target_window = active_win
                        self.root.after(0, lambda: self.status_label.config(text=f"고정: {active_win.title[:10]}", foreground="green"))
                        self.log("창 고정")
                    time.sleep(0.4)
                elif keyboard.is_pressed('d'):
                    self.set_target_color(); time.sleep(0.4)
                elif keyboard.is_pressed('r'):
                    abs_x, abs_y = win32api.GetCursorPos()
                    if self.target_window:
                        self.refresh_coord = (abs_x - self.target_window.left, abs_y - self.target_window.top)
                        self.log(f"새로고침 좌표 등록")
                    time.sleep(0.4)
                elif keyboard.is_pressed('a'):
                    abs_x, abs_y = win32api.GetCursorPos()
                    if self.target_window:
                        rel = (abs_x - self.target_window.left, abs_y - self.target_window.top)
                        self.relative_coords.append(rel)
                        self.coord_listbox.insert(tk.END, f"대상: {rel}")
                        self.log(f"클릭 대상 추가")
                    time.sleep(0.4)
                elif keyboard.is_pressed('s'):
                    self.is_running = not self.is_running
                    status = "실행 중" if self.is_running else "중지됨"
                    self.root.after(0, lambda s=status: self.status_label.config(text=s, foreground="red" if self.is_running else "blue"))
                    if self.is_running: self.start_macro()
                    time.sleep(0.5)
                elif keyboard.is_pressed('c'):
                    if self.relative_coords:
                        # 리스트와 리스트박스에서 마지막 항목 제거
                        removed_coord = self.relative_coords.pop()
                        self.coord_listbox.delete(tk.END)
                        self.log(f"마지막 좌표 삭제됨: {removed_coord}")
                    else:
                        self.log("삭제할 좌표가 없습니다.")
                    time.sleep(0.4)
                elif keyboard.is_pressed('e'):
                    self.relative_coords = []; self.refresh_coord = None; self.target_rgb = None
                    self.color_preview.config(bg="#dddddd", text="색상 미지정")
                    self.color_label.config(text=" RGB: (---, ---, ---)")
                    self.coord_listbox.delete(0, tk.END); self.log("초기화 완료"); time.sleep(0.4)
            time.sleep(0.01)

if __name__ == "__main__":
    root = tk.Tk(); app = ProSniperV4_1(root); root.mainloop()
