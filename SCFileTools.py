import sys
import os

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCREEN_SCALE_FACTORS"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1"

import shutil
import ctypes
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QPoint, QThread, QThreadPool, QRunnable, pyqtSignal
from PyQt5.QtGui import QFont, QFontDatabase

from PyQt5.uic import loadUi
import time

import logging
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
o = logging.getLogger(__name__)

import LauncherHelper


def exception_hook(type, value, traceback):
    """
    Custom exception hook to handle and print exceptions.
    """
    print("Exception Hook:")
    print(f"Type: {type}")
    print(f"Value: {value}")
    print(f"Traceback: {traceback}")

    sys.__excepthook__(type, value, traceback)


sys.excepthook = exception_hook


def scrub_folder(folder):
    """
    Recursively delete files and directories within a folder.

    Args:
        folder (str): Path to the folder to be scrubbed.
    """
    # Check if folder exists
    if not os.path.exists(folder):
        return

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)

        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)

            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def get_resource_path(relative_path):
    """
    Get the absolute path to a resource, whether in development or PyInstaller bundle.

    Args:
        relative_path (str): Relative path to the resource.

    Returns:
        str: Absolute path to the resource.
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    else:
        # Use the directory containing the script as the base path
        base_path = os.path.abspath(os.path.dirname(sys.argv[0]))
    return os.path.join(base_path, relative_path)


def is_admin():
    """
    Check if the current user has admin privileges.

    Returns:
        bool: True if the user has admin privileges, False otherwise.
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def permission_level():
    """
    Get the permission level of the current user.

    Returns:
        str: Permission level, either "ADMIN" or "Non-Admin".
    """
    if is_admin():
        return "ADMIN"
    else:
        return "Non-Admin"


class Task2(QRunnable):
    def __init__(self, target_method):
        super().__init__()
        self.target_method = target_method

    def run(self):
        # Execute the target method
        self.target_method()

# Custom task class implementing QRunnable
class Task(QRunnable):
    def __init__(self, target_method, *args, **kwargs):
        super().__init__()
        self.target_method = target_method
        self.args = args
        self.kwargs = kwargs

    def run(self):
        # Execute the target method with the provided arguments
        self.target_method(*self.args, **self.kwargs)


class SCFF(QMainWindow):
    info_signal = pyqtSignal(str, str)
    def __init__(self):
        super().__init__()

        self.thread_pool = QThreadPool()


        uipath = get_resource_path("form.ui")
        loadUi(uipath, self)


        self.info_signal.connect(self.info)

        self.current_user = os.getenv('USERNAME')

        self.rctime = 0

        self.main_directory = r"F:\Games\Roberts Space Industries"
        self.shaders_directory = os.path.join(os.getenv('LOCALAPPDATA'), "Star Citizen")

        self.LIVE_directory = os.path.join(self.main_directory, "StarCitizen", "LIVE")
        self.PTU_directory = os.path.join(self.main_directory, "StarCitizen", "PTU")
        self.EPTU_directory = os.path.join(self.main_directory, "StarCitizen", "EPTU")

        # EAC directories
        self.eac_roaming = os.path.join(os.getenv('APPDATA'), "EasyAntiCheat")
        self.eac_programFiles = os.path.join(os.getenv('ProgramFiles(x86)'), "EasyAntiCheat_EOS")

        self.launcher_roaming = os.path.join(os.getenv('APPDATA'), "rsilauncher")

        self.RSIPrefix = "RSI: "
        self.shadersPrefix = "Shaders: "

        self.misc_log_env = "LIVE"

        self.launcher_handle = None
        self.launcher_exe = None

        self.testing = True

        self.is_title_bar_hidden = False

        self.init_ui()

    def init_ui(self):
        """
        Initialize the user interface and connect buttons to their respective functions.
        """
        # Connect buttons to functions
        self.pb_setMainDir.clicked.connect(self.select_main_directory)
        self.pb_setShadersDir.clicked.connect(self.select_shaders_directory)
        self.pb_deleteShaders.clicked.connect(self.delete_shaders)
        self.pb_openShaders.clicked.connect(lambda: subprocess.Popen(f'explorer {self.shaders_directory}'))
        self.pb_deleteUser.clicked.connect(self.delete_user_folder)
        self.pb_EXIT.clicked.connect(self.close)  # Connect EXIT button to close the program
        self.pb_MINIMIZE.clicked.connect(self.showMinimized)  # Connect MINIMIZE button to minimize the program
        self.pb_misc_launcher1.clicked.connect(lambda: self.reset_launcher(self.cb_launcher_deep.isChecked()))
        self.pb_misc_closeLauncher.clicked.connect(self.close_launcher)
        self.pb_misc_viewLog.clicked.connect(self.open_game_log)
        self.pb_misc_consoleLog.clicked.connect(self.powershell_log)
        self.pb_misc_recentErrorLog.clicked.connect(self.open_crash_log)
        self.pb_misc_relaunchLauncher.clicked.connect(self.relaunch_launcher)

        self.pb_EAC_SC.clicked.connect(lambda: self.nuke_EAC(self.pb_EAC_SC))
        self.pb_EAC_roaming.clicked.connect(lambda: self.nuke_EAC(self.pb_EAC_roaming))
        self.pb_EAC_programFiles.clicked.connect(lambda: self.nuke_EAC(self.pb_EAC_programFiles))
        self.pb_EAC_all.clicked.connect(lambda: self.nuke_EAC(self.pb_EAC_all))

        self.rb_misc_LIVE.clicked.connect(lambda: setattr(self, "misc_log_env", "LIVE"))
        self.rb_misc_PTU.clicked.connect(lambda: setattr(self, "misc_log_env", "PTU"))
        self.rb_misc_EPTU.clicked.connect(lambda: setattr(self, "misc_log_env", "EPTU"))

        # Set the text of the labels to the current paths
        self.l_path_main.setText(self.RSIPrefix + self.main_directory)
        self.l_path_shaders.setText(self.shadersPrefix + self.shaders_directory.replace(self.current_user, "[user]"))

        self.l_permission.setText("Running as: " + permission_level())

        self.frame.mousePressEvent = self.mouse_press_event_frame
        self.frame.mouseMoveEvent = self.mouse_move_event
        self.frame.mouseReleaseEvent = self.mouse_release_event

        self.is_title_bar_hidden = False
        self.dragging_offset = None

        self.setStyleSheet("QGroupBox {font-size: 14px;}")
        self.info_style=QFont("Lucida Console", 10)

        self.l_info_1.setFont(self.info_style)
        self.l_info_2.setFont(self.info_style)

        self.adjustSize()

        self.toggle_title_bar()

        self.info(preset=0)

    def show_info_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Information")
        msg.exec_()

    def select_main_directory(self):
        """
        Open a dialog to select the main directory and update the path accordingly.
        """
        directory = QFileDialog.getExistingDirectory(self, "Select Main Directory")
        if directory:
            self.main_directory = directory
            self.l_path_main.setText(self.RSIPrefix + directory)

    def select_shaders_directory(self):
        """
        Open a dialog to select the shaders directory and update the path accordingly.
        """
        directory = QFileDialog.getExistingDirectory(self, "Select Shaders Directory")
        if directory:
            self.shaders_directory = directory
            username = os.path.split(os.path.expanduser("~"))[-1]
            display_directory = self.shaders_directory.replace(username, "[user]")
            self.l_path_shaders.setText(self.shadersPrefix + display_directory)

    def select_test_directory(self):
        """
        Open a dialog to select the test directory and update the path accordingly.
        """
        directory = QFileDialog.getExistingDirectory(self, "Select Test Directory")
        if directory:
            self.test_directory = directory
            self.l_testDir.setText(directory)

    def delete_user_folder(self):

        enviro_list = []
        if self.cb_user_LIVE.isChecked():
            enviro_list.append("LIVE")
        if self.cb_user_PTU.isChecked():
            enviro_list.append("PTU")
        if self.cb_user_EPTU.isChecked():
            enviro_list.append("EPTU")

        main_dir = os.path.join(self.main_directory, 'StarCitizen')

        fc = 0
        dc = 0

        for env in enviro_list:
            folders_to_keep = []
            files_to_keep = []
            kept = []

            user_dir = os.path.join(main_dir, env, "USER")
            cli_0_dir = os.path.join(user_dir, "Client", "0")

            if self.cb_user_retainBindingsEx.isChecked():
                folders_to_keep.append(os.path.join(cli_0_dir, "Controls", "Mappings"))
                kept.append("Exported Bindings")
            if self.cb_user_retainBindingsCur.isChecked():
                files_to_keep.append(os.path.join(cli_0_dir, "Profiles", "default", "actionmaps.xml"))
                kept.append("Current Bindings")
            if self.cb_user_retainSettings.isChecked():
                files_to_keep.append(os.path.join(cli_0_dir, "Profiles", "default", "attributes.xml"))
                kept.append("Settings")

            for root, dirs, files in os.walk(user_dir, topdown=False):
                for name in files:
                    file_path = os.path.join(root, name)
                    if file_path not in files_to_keep and root not in folders_to_keep:
                        os.remove(file_path)
                        fc += 1

                for name in dirs:
                    dir_path = os.path.join(root, name)
                    if not os.listdir(dir_path) and dir_path not in folders_to_keep:
                        os.rmdir(dir_path)
                        dc += 1
        self.info(clear_unused=True)
        if len(enviro_list) > 0:
            self.info(f"Deleted {fc} files and {dc} folders.")
            if len(kept) > 0:
                self.info(t2="Kept: " + ", ".join(kept))
            else:
                self.info(t2="Kept nothing.")
        else:
            self.info("No environment selected.")

    def delete_shaders(self):
        """
        Delete shaders based on the selected option.
        """
        done = False
        if self.rb_s_All.isChecked():
            folders = [f for f in os.listdir(self.shaders_directory) if
                       os.path.isdir(os.path.join(self.shaders_directory, f))]
            for folder in folders:
                if folder.startswith("sc-alpha"):
                    folder_path = os.path.join(self.shaders_directory, folder)
                    shutil.rmtree(folder_path)

                    done = True
            self.info(clear_unused=True)
            self.info(t1=f"Deleted all shaders!", t2=f"({len(folders)} folders)")
        elif self.rb_s_Pick.isChecked():
            selected_folder = QFileDialog.getExistingDirectory(self, "Select Folder to Delete", self.shaders_directory)
            if selected_folder:
                shutil.rmtree(selected_folder)
                done = True
                self.info(clear_unused=True)
                self.info(t1=f"Deleted shaders in:", t2=f"{selected_folder}")

    def open_game_log(self):
        """
        Open the game log file in the default program.
        """

        envpath = os.path.join(self.main_directory, "StarCitizen", self.misc_log_env)
        logpath = os.path.join(envpath, "Game.log")
        self.info(clear_unused=True)
        if not os.path.isfile(logpath):
            self.info(f"Log file not found...")
            if not os.path.isdir(envpath):
                self.info(t2=f"Environment {self.misc_log_env} folder not found...")
            return
        else:
            try:
                os.startfile(logpath)
                self.info(f"Opened {logpath}")
            except:
                o.error("Failed to open log file.")
    def open_crash_log(self):
        """
        Open the most recent crash log.
        """

        logpath = os.path.join(self.shaders_directory, "Crashes")
        logfile = os.path.join(logpath,"Game.log")

        self.info(clear_unused=True)
        if not os.path.isfile(logfile):
            self.info(f"Log file not found...")
            if not os.path.isdir(logpath):
                self.info(t2=f"Crash folder not found.")
            return
        else:
            try:
                os.startfile(logfile)
                self.info(f"Opened {logfile}")
            except:
                o.error("Failed to open log file.")

    def powershell_log(self):
        """
        Open PowerShell and display the game log in real-time.
        """
        logpath = os.path.join(self.main_directory, "StarCitizen", self.misc_log_env, "Game.log")

        if not os.path.isfile(logpath):
            self.info(f"Log file not found...")
            if not os.path.isdir(self.misc_log_env):
                self.info(t2=f"Environment {self.misc_log_env} folder not found...")
            return

        file_path = logpath.replace("\\", "\\\\")
        # full path to powershell
        pwershellpath = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
        command = f'start {pwershellpath} Get-Content \'{file_path}\' -Wait'
        self.info(clear_unused=True)
        self.info(t1="Opening PowerShell...", t2=f"Log file: {logpath}")
        subprocess.call(command, shell=True)

    def nuke_EAC(self, sender):
        """
        Nuke Easy Anti-Cheat (EAC) directories and files.

        Chosen environment(s) will be respected for the individual case of
        nuking the EAC folders in the SC directories. If the 'nuke all' button
        is pressed, these environments will also be included. Un-checked environments
        will be ignored in all cases.

        Args:
            sender (QPushButton): The button that triggered the function.
            This determines which nuke routines will run. If the 'nuke all' button
            is pressed, all nuke routines will run.
        """
        sender_object = sender.objectName()
        enviro_list = []
        if self.cb_EAC_LIVE.isChecked():
            enviro_list.append("LIVE")
        if self.cb_EAC_PTU.isChecked():
            enviro_list.append("PTU")
        if self.cb_EAC_EPTU.isChecked():
            enviro_list.append("EPTU")
        checklist=[]

        if sender_object == 'pb_EAC_SC' and len(enviro_list) == 0:
            self.info("No environment selected.")
            return

        # Nuke the EAC folders in the SC directories
        if sender_object == 'pb_EAC_SC' or sender_object == 'pb_EAC_all':
            for env in enviro_list:
                print(f"Deleting EAC for {env}")
                scrub_folder(os.path.join(self.main_directory, "StarCitizen", env, "EasyAntiCheat"))
                checklist.append(env)

        # Nuke the EAC folder in appdata roaming
        if sender_object == 'pb_EAC_roaming' or sender_object == 'pb_EAC_all':
            scrub_folder(self.eac_roaming)
            checklist.append('AppData\\Roaming')

        # Nuke the EasyAntiCheat_EOS.sys file in program files
        # This requires admin privileges
        if sender_object == 'pb_EAC_programFiles' or sender_object == 'pb_EAC_all':

            PATH = os.path.join(self.eac_programFiles, "EasyAntiCheat_EOS.sys")
            try:
                print("Attempting to delete EasyAntiCheat_EOS.sys")
                if ctypes.windll.shell32.IsUserAnAdmin():
                    if os.path.exists(PATH):
                        os.remove(PATH)
                        checklist.append('Program Files')
                else:
                    self.info("Incorrect permissions. Please run the program as an administrator and try again.",'')
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Error when attempting to nuke EAC in the Program Files (x86) folder...\n"
                                "Incorrect permissions. Please run the program as an administrator and try again.")
                    msg.setWindowTitle("Error")
                    msg.exec_()
                    return
            except:
                print("Failed to delete EasyAntiCheat_EOS.sys")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Error: Failed to delete EasyAntiCheat_EOS.sys\n"
                            "--___--")
                msg.setWindowTitle("Error")
                msg.exec_()
        self.info(f'Nuking EAC is complete!',f'Locations liberated: {", ".join(checklist)}')
        # msg = QMessageBox()
        # msg.setIcon(QMessageBox.Information)
        # msg.setText("Nuking EAC is complete!")
        # msg.setWindowTitle("Nuking EAC")
        # msg.exec_()

    def close_launcher_thread(self):
        is_thread = isinstance(threading.current_thread(), QThread)
        if is_thread:
            print("Closing launcher from within a thread")

        handle, exe = LauncherHelper.launcher_properties()
        self.launcher_handle = handle
        self.launcher_exe = exe
        LauncherHelper.close_launcher(handle)

    def open_launcher_thread(self):
        if self.launcher_exe:
            LauncherHelper.open_launcher(self.launcher_exe)
        else:
            o.error("Launcher exe not found. It may not have been running yet.")

    def close_launcher(self):
        """
        Close the launcher using the LauncherHelper module.
        """
        i_string="Closing launcher and all launcher processes."
        print("Labels text:")
        print(self.l_info_1.text())
        print(self.l_info_2.text())

        if self.l_info_2.text()==" ":
            self.info(t2=i_string)
        else:
            self.info(t1=i_string)
        QApplication.processEvents()



        thread = Task(self.close_launcher_thread)
        # self.thread_pool.\
        pool.start(thread)

    def relaunch_launcher(self):

        self.info("Please wait for launcher to restart...", ' ')
        QApplication.processEvents()

        self.close_launcher()

        # thread1 = Task(self.close_launcher_thread)
        # pool.start(thread1)

        pool.waitForDone()

        thread2 = Task(self.open_launcher_thread)
        pool.start(thread2)

        pool.waitForDone()
        self.info(t1="Launcher restarted.",t2='')

        # self.relaunch_launcher_manager()

    def relaunch_launcher_manager(self):
        """
        Relaunch the launcher using the LauncherHelper module.
        """

        thread1 = Task(self.close_launcher_thread)
        pool.start(thread1)

        pool.waitForDone()

        thread2 = Task(self.open_launcher_thread)
        pool.start(thread2)

    def reset_launcher(self, deep_clean):
        """
        Reset the launcher by deleting selected items in the launcher directory.

        Args:
            deep_clean (bool): Whether to perform a deep clean or not.
            deep_clean will delete the entire contents of the roaming\rsilauncher directory.
        """

        shallow_list = ['Session Storage', 'sentry', 'log.log']
        launcher_roaming_dir = self.launcher_roaming
        launcher_handle, launcher_exe = LauncherHelper.launcher_properties()

        print('Closing Launcher...')
        LauncherHelper.close_launcher(launcher_handle)

        # For testing purposes, skip the deletion of the launcher items
        skip = False
        self.info(clear_unused=True)
        self.info(t1="Resetting and restarting launcher. Please wait...")
        if not skip:
            if deep_clean:
                # shutil.rmtree(launcher_roaming_dir)
                scrub_folder(launcher_roaming_dir)
                print(f"Deleted directory and all its contents: {launcher_roaming_dir}")
            else:
                for shallow_item in shallow_list:
                    shallow_item_path = os.path.join(launcher_roaming_dir, shallow_item)
                    if os.path.isdir(shallow_item_path):
                        shutil.rmtree(shallow_item_path)
                        print(f"Deleted directory and all its contents: {shallow_item_path}")
                    elif os.path.isfile(shallow_item_path):
                        os.remove(shallow_item_path)
                        print(f"Deleted file: {shallow_item_path}")

        print("Reopening launcher")
        LauncherHelper.open_launcher(launcher_exe)
        self.info(t2="Done!")

    def info(self, t1=None, t2=None, preset=None, clear_unused=False):

        def l1(txt):
            self.l_info_1.setText(str(txt))

        def l2(txt):
            self.l_info_2.setText(str(txt))

        if preset is not None:
            if preset == 0:
                l1("Welcome!")
                l2('')
        else:
            if t1 is not None:
                l1(t1)
            if clear_unused and t2 is None:
                l2('')
            if t2 is not None:
                l2(t2)
            if clear_unused and t1 is None:
                l1('')

    def mouse_press_event_frame(self, event):
        """
        Handle the mouse press event on the frame (title bar).

        Args:
            event (QMouseEvent): Mouse press event.
        """
        if event.button() == Qt.LeftButton:
            self.dragging_offset = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mousePressEvent(self, event):
        """
        Handle the mouse press event on the window.

        Args:
            event (QMouseEvent): Mouse press event.
        """
        if event.button() == 2:
            thisclick = time.time()
            if thisclick - self.rctime < 0.15:

                self.toggle_title_bar()
            else:
                self.rctime = thisclick

        else:
            super().mousePressEvent(event)

    def mouse_move_event(self, event):
        """
        Handle the mouse move event on the window.

        Args:
            event (QMouseEvent): Mouse move event.
        """
        if event.buttons() & Qt.LeftButton and self.dragging_offset is not None:
            self.move(event.globalPos() - self.dragging_offset)
            event.accept()

    def mouse_release_event(self, event):
        """
        Handle the mouse release event on the window.

        Args:
            event (QMouseEvent): Mouse release event.
        """
        if event.button() == Qt.LeftButton:
            self.dragging_offset = None
            event.accept()

    def toggle_elements(self):
        if self.is_title_bar_hidden:
            self.l_testDir.hide()
            self.pb_setTestDir.hide()
            self.pb_prepTest.hide()
        else:
            self.l_testDir.show()
            self.pb_setTestDir.show()
            self.pb_prepTest.show()

    def toggle_title_bar(self):
        """
        Toggle the visibility of the title bar and testing elements.
        """
        self.is_title_bar_hidden = not self.is_title_bar_hidden
        self.toggle_elements()
        self.setWindowFlag(Qt.FramelessWindowHint, self.is_title_bar_hidden)
        self.show()

    def closeEvent(self, event):
        """
        Handle the close event on the window.

        Args:
            event (QCloseEvent): Close event.
        """
        o.info(f"Number of threads in the pool: {self.thread_pool.activeThreadCount()}")
        self.thread_pool.clear()
        event.accept()


if __name__ == '__main__':
    pool=QThreadPool()
    app = QApplication(sys.argv)
    qsspath = get_resource_path("IC1a.qss")
    try:
        with open(qsspath, "r") as qss_file:
            style_sheet = qss_file.read()
        app.setStyleSheet(style_sheet)
    except:
        pass

    SCFF_obj = SCFF()
    SCFF_obj.show()
    sys.exit(app.exec_())
