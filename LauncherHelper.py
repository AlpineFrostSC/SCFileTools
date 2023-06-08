import win32gui
import win32con
import psutil
import subprocess
import time
import win32process
import ctypes


def launcher_properties():
    window_title = 'RSI Launcher'
    # Find the handle of the program's main window
    window_handle = win32gui.FindWindow(None, window_title)

    if window_handle != 0:
        process_id = win32process.GetWindowThreadProcessId(window_handle)[1]
        process = psutil.Process(process_id)
        executable_path = process.exe()
        return window_handle, executable_path
    else:
        return None, None


def close_launcher(window_handle):
    exe_name = 'RSI Launcher.exe'
    # Send a close request to the program's main window
    try:
        win32gui.PostMessage(window_handle, win32con.WM_CLOSE, 0, 0)
        time.sleep(1)
    except:
        # If the window is already closed,
        pass
    try:
        subprocess.call(['taskkill', '/f', '/im', exe_name], stderr=subprocess.DEVNULL)
    except:
        # If all remaining processes are killed
        pass


def open_launcher(executable_location):
    if executable_location:
        subprocess.Popen(executable_location, shell=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)


def ctypes_input():
    inputs = ctypes.c_buffer(2 * ctypes.sizeof(ctypes.c_ulong))

    ctypes.windll.user32.keybd_event(0x11, 0, 0, 0)  # CTRL key down
    ctypes.windll.user32.keybd_event(0x52, 0, 0, 0)  # R key down and up
    ctypes.windll.user32.keybd_event(0x52, 0, win32con.KEYEVENTF_KEYUP, 0)
    ctypes.windll.user32.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)  # CTRL key up

    ctypes.windll.user32.SendInput(2, inputs, ctypes.sizeof(ctypes.c_ulong))


if __name__ == '__main__':
    window_handle, executable_path = launcher_properties()
    if window_handle:
        close_launcher(window_handle)
        open_launcher(executable_path)
