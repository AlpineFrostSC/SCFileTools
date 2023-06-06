import sys
import os
import shutil
import ctypes
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QPoint
from PyQt5.uic import loadUi
import time

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


class SCFF(QMainWindow):
    def __init__(self):
        super().__init__()
        uipath = get_resource_path("form.ui")
        loadUi(uipath, self)

        self.current_user = os.getenv('USERNAME')

        self.rctime = 0

        self.main_directory = r"F:\Games\Roberts Space Industries"
        self.shaders_directory = os.path.join(os.getenv('LOCALAPPDATA'), "Star Citizen")
        self.test_directory = rf"C:\Users\{self.current_user}\PycharmProjects\ChatGPTStuff\sc_file_management\SCFileTools\Test"
        # return the last two subdirectories from self.test_directory
        self.test_directory_last_two = os.path.join(*self.test_directory.split(os.path.sep)[-2:])

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
        self.pb_setTestDir.clicked.connect(self.select_test_directory)
        self.pb_deleteShaders.clicked.connect(self.delete_shaders)
        self.pb_prepTest.clicked.connect(self.prep_test_data)
        self.pb_EXIT.clicked.connect(self.close)  # Connect EXIT button to close the program
        self.pb_MINIMIZE.clicked.connect(self.showMinimized)  # Connect MINIMIZE button to minimize the program
        self.pb_misc_launcher1.clicked.connect(lambda: self.reset_launcher(self.cb_launcher_deep.isChecked()))
        self.pb_misc_closeLauncher.clicked.connect(self.close_launcher)
        self.pb_misc_viewLog.clicked.connect(self.open_game_log)
        self.pb_misc_consoleLog.clicked.connect(self.powershell_log)
        self.pb_misc_relaunchLauncher.clicked.connect(self.relaunch_launcher)

        self.pb_EAC_SC.clicked.connect(lambda: self.nuke_EAC(self.pb_EAC_SC))
        self.pb_EAC_roaming.clicked.connect(lambda: self.nuke_EAC(self.pb_EAC_roaming))
        self.pb_EAC_programFiles.clicked.connect(lambda: self.nuke_EAC(self.pb_EAC_programFiles))
        self.pb_EAC_all.clicked.connect(lambda: self.nuke_EAC(self.pb_EAC_all))

        self.rb_misc_LIVE.clicked.connect(lambda: self.set_misc_log_env("LIVE"))
        self.rb_misc_PTU.clicked.connect(lambda: self.set_misc_log_env("PTU"))
        self.rb_misc_EPTU.clicked.connect(lambda: self.set_misc_log_env("EPTU"))

        # Set the text of the labels to the current paths
        self.l_path_main.setText(self.RSIPrefix + self.main_directory)
        self.l_path_shaders.setText(self.shadersPrefix + self.shaders_directory.replace(self.current_user, "[user]"))
        self.l_testDir.setText('...\\' + self.test_directory_last_two)

        self.l_permission.setText("Running as: " + permission_level())

        self.frame.mousePressEvent = self.mouse_press_event_frame
        self.frame.mouseMoveEvent = self.mouse_move_event
        self.frame.mouseReleaseEvent = self.mouse_release_event

        self.is_title_bar_hidden = False
        self.dragging_offset = None

        self.setStyleSheet("QGroupBox {font-size: 14px;}")

        self.adjustSize()

        self.toggle_title_bar()

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

    def delete_shaders(self):
        """
        Delete shaders based on the selected option.
        """
        done=False
        if self.rb_s_All.isChecked():
            folders = [f for f in os.listdir(self.shaders_directory) if
                       os.path.isdir(os.path.join(self.shaders_directory, f))]
            for folder in folders:
                if folder.startswith("sc-alpha"):
                    folder_path = os.path.join(self.shaders_directory, folder)
                    shutil.rmtree(folder_path)
                    print(f"Deleted folder: {folder_path}")
                    done=True
        elif self.rb_s_Pick.isChecked():
            selected_folder = QFileDialog.getExistingDirectory(self, "Select Folder to Delete", self.shaders_directory)
            if selected_folder:
                shutil.rmtree(selected_folder)
                print(f"Deleted folder: {selected_folder}")
                done=True

        if done:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setInformativeText("Shaders have been deleted")
            msg.setWindowTitle("Shaders Deleted")
            msg.exec_()
        else:
            print("No shaders deleted...")


    def set_misc_log_env(self, env):
        """
        Set the miscellaneous log environment.

        Args:
            env (str): Log environment ("LIVE", "PTU", "EPTU").
        """
        self.misc_log_env = env

    def open_game_log(self):
        """
        Open the game log file in the default program.
        """
        logpath = os.path.join(self.main_directory, "StarCitizen", self.misc_log_env, "Game.log")
        # Open the file in the default program
        try:
            os.startfile(logpath)
        except:
            print("Failed to open log file. Environment not found?")

    def powershell_log(self):
        """
        Open PowerShell and display the game log in real-time.
        """
        logpath = os.path.join(self.main_directory, "StarCitizen", self.misc_log_env, "Game.log")
        file_path = logpath.replace("\\", "\\\\")
        # full path to powershell
        pwershellpath = "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
        command = f'start {pwershellpath} Get-Content \'{file_path}\' -Wait'
        print(command)
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

        # Nuke the EAC folders in the SC directories
        if sender_object == 'pb_EAC_SC' or sender_object == 'pb_EAC_all':
            for env in enviro_list:
                print(f"Deleting EAC for {env}")
                scrub_folder(os.path.join(self.main_directory, "StarCitizen", env, "EasyAntiCheat"))

        # Nuke the EAC folder in appdata roaming
        if sender_object == 'pb_EAC_roaming' or sender_object == 'pb_EAC_all':
            scrub_folder(self.eac_roaming)

        # Nuke the EasyAntiCheat_EOS.sys file in program files
        # This requires admin privileges
        if sender_object == 'pb_EAC_programFiles' or sender_object == 'pb_EAC_all':

            PATH = os.path.join(self.eac_programFiles, "EasyAntiCheat_EOS.sys")
            try:
                print("Attempting to delete EasyAntiCheat_EOS.sys")
                if ctypes.windll.shell32.IsUserAnAdmin():
                    if os.path.exists(PATH):
                        os.remove(PATH)
                else:
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

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Nuking EAC is complete!")
        msg.setWindowTitle("Nuking EAC")
        msg.exec_()

    def close_launcher(self):
        """
        Close the launcher using the LauncherHelper module.
        """
        handle, _ = LauncherHelper.launcher_properties()
        LauncherHelper.close_launcher(handle)

    def relaunch_launcher(self):
        """
        Relaunch the launcher using the LauncherHelper module.
        """
        handle, exe = LauncherHelper.launcher_properties()
        LauncherHelper.close_launcher(handle)
        LauncherHelper.open_launcher(exe)

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

    def prep_test_data(self):
        """
        Copy test data from a source directory to the test directory.
        """
        src_directory = fr"C:\Users\{self.current_user}\PycharmProjects\ChatGPTStuff\sc_file_management\SCFileTools\testdata"
        for root, dirs, files in os.walk(src_directory):
            relative_dir = os.path.relpath(root, src_directory)
            dest_dir = os.path.join(self.test_directory, relative_dir)
            os.makedirs(dest_dir, exist_ok=True)
            for file in files:
                src_file = os.path.join(root, file)
                dest_file = os.path.join(dest_dir, file)
                shutil.copy2(src_file, dest_file)
                print(f"Copied file: {dest_file}")

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


if __name__ == '__main__':
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
