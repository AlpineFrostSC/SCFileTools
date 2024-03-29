=================================================
SC File Fiddler ... *Fiddle around and find out!*
=================================================


.. image:: https://media.discordapp.net/attachments/957406732525645855/1116365715142885476/image.png
   :align: center

Wut?
--------

**SC File Fiddler is a collection of simple tools for performing those standard
yet tedious tasks when troubleshooting Star Citizen.**


| Tired of remembering where your shaders have run off to?
| Sick of losing your settings when you delete that *sweet* USER folder?
| EAC holding your Finley for ransom?


Well, *fear no more*! SC File Fiddler is here to help!


Browse this documentation to see what you can do with SCFF, and be sure
to look over the `Some Guidance <#some-guidance>`_ section to get a more detailed explanation of the functions.

____

Quick-Start
-----------
*Because who has time to read words?*

1. Download `the latest portable version <https://github.com/AlpineFrostSC/SCFileTools/releases>`_.
2. Run it.

* Set your RSI directory. This is where your StarCitizen lives.

* Shaders should already be set correctly, but change it if you need to.

``What you can do...``

* Shaders - Clear some or all.
* USER Folder - Delete your USER folder for one or more environment.

  * Save your settings and bindings in place if you want to.

* EAC - Delete EAC files in various locations. (bet you didn't know there were *that* many places!)
* Misc.

  * Open the Game.log file
  * Create an 'external game console' using PowerShell!
  * Perform robust Launcher operations without having to play in Task Manager or remember key combos.

____

Features
--------

- Clear your shaders - Either selectively or all at once!
- Delete your USER folder, With options to back up your settings and keybindings!
- NUKE EAC out of existence! (yeah it'll  be back, but it feels good to watch it burn for a bit)
- Quick access to the Star Citizen log files, including *console emulation* to view the logs in real-time!
- ... *And much more!*

Run it!
-------
For cloning and running the python directly:

Dependencies can be found in the `requirements.txt` file.

*For the portable executable, just grab it and run it!*


Fancy portable executable
~~~~~~~~~~~~~~~~~~~~~~~~~


For Windows. What, you expected something else?

**No dependencies or external files required!**

1. Installation:
    - Download the latest release (zipped bundle or standalone exe) executable from `where latest releases are born <https://github.com/AlpineFrostSC/SCFileTools/releases>`_.
2. Run the Application:
    - Run the standalone executable, or unzip the bundle and run the executable.
    - That's it. You win.


Git clone
~~~~~~~~~

Probably also exclusively for Windows. Otherwise, this is a rabbit hole for *you* to squeeze your way through.

1. Installation:
    - Clone the repository: `git clone https://github.com/AlpineFrostSC/SCFileTools.git`
    - Install the required dependencies (if needed): `pip install -r requirements.txt`

2. Run the Application:
    - Navigate to the project directory: `cd SCFileTools`
    - Launch the application: `python SCFileTools.py`
    - Failure to run the application from within its directory may result in broken file references. No big deal.

Then just look at things with your eyeballs and identify what you'd like to accomplish.
Alternatively, read some docs at [docLocationNotFoundSryNotSry] for more information.


Some Guidance
------------
Let's take a look at the sections you see on the main window and the functions that those provide.

First, please note the "Running as:" in the tile bar of the program. This indicates whether you have run the program as
ADMIN or not. **This is an important point for at least one feature of the program.** But otherwise not a big deal. 

1. **Folder Paths**
    - These couple of lines allow you to choose where your main RSI directory and Shaders folders exist.
    - *You'll need to set the RSI directory yourself* (this is where the StarCitizen folder is, containing your important game files), while the shaders directory is initially set to the default location.
This assumes your game is installed inside the ``Roberts Space Industries`` folder somewhere, but you can set it to whatever directory your StarCitizen game folder exists in. Additionally, if you don't
plan on fiddling with shaders, you can ignore the Shaders Directory line.



2. **Shaders**
    - This section is for clearing out your shaders. You can either clear them all at once, or selectively clear them.
    - The `Delete All` radio option will delete all the shader files in the Shaders directory, while the `Prompt for folder`
      option will allow you to select a specific Shader folder to clear upon clicking the `Delete Shaders` button.

3. **USER Folder**
    - This section is for deleting your USER folder. You can choose to retain your settings and keybindings **in place** before
      deleting the folder, and you can also choose to delete the user folders for more than one environment at a time.
    - `Keep exported keybinds` retains your exported binding files, `Keep current keybinds` preserves the ``actionmaps.xml``, and `Keep settings` preserves the ``attributes.xml`` file. All in-place.
    - Check one or more environments in which to delete the USER folder (while applying any of the aforementioned options).
4. **EAC**
    - This section is for deleting a bunch of EasyAntiCheat stuff. EAC issues are somewhat common sources of issues
      when attempting to launch the game, and there are ``three locations`` where sneaky EAC files reside.
    - `"In SC Folders"` will delete the EAC folder contents within any of the selected environments immediately below the button.
    - `"In AppData>Roaming"` will delete the EAC folder contents within the AppData\\Roaming directory.
    - `"In Program Files"` will delete the ``EasyAntiCheat_EOS.sys`` file within the relevant Program Files (x86) subdirectory.

      + **Note: This one will require elevated permissions. You will need to run the program as ADMIN to allow this.**

    - `"Nuke-It-All™"` will delete all of the above. **Note: This will respect any un-selected environments in the SC Folders section.**

5. **Misc.**
    - This section includes some tools for the Game.log file, as well as for some Launcher support.
    - `Open Game.log` will open the Game.log file in the default text editor.
    - `Run Game.log in Powershell...` will open the Game.log file in PowerShell, providing a real-time view of the log
      as the game makes changes to it. This effectively mirrors the functionality of the console in the game.
    - **Launcher stuff**

      + `Reset Launcher` will clear the contents of the Launcher folder in AppData\\Roaming. This is similar to a conventional
        launcher reset, though substantially more thorough. **Launcher will be automatically closed during this process and then restarted.**
      + `Fully Close Launcher` will close the launcher window, and exit all remaining ``RSI Launcher.exe`` processes.
      + `Re-Launch Launcher` will close the launcher (using the method above), and then reopen it.
      + `Refresh Launcher` sends a `Ctrl+R` to your launcher, to refresh it. This is a quick alternative to closing and reopening the launcher to see if a patch has dropped.

        + `"Patch-watch mode"` option will keep sending refresh commands to your launcher *until you un-check it*. Handy if you're *really* eager to grab that patch ASAP!

Some Mild Caveats
~~~~~~~~~~~~~~~~~

Most of the functions provided by the Fiddler don't require any special permissions. That said, there are a few that do.
At the moment, the one one that appears to require elevated permissions is deleting the EAC file within the
Program Files directory.

Generally, this program can be run without any consideration to permissions. But if you *really* wanna nuke EAC, you may
want to run this as an administrator.

.. tip:: This is recommended, since the EAC file tucked away in the Program Files location is one of the common causes of ``CreateFile 32`` errors!


A Not-so-mild Disclaimer
~~~~~~~~~~~~~~~~~~~~~~~~
This program is provided as-is. I'm not responsible for any damage that may occur to your computer, your spaceships,
your dog, or your Picos. Use at your own risk.

With that out of the way, there shouldn't be much to lose sleep over. Most functions affect files and directories which
are hard-coded (or nearly so), defined by the user, or determined by windows variables, meaning the worst that is likely to happen is the functions will do what you expect them
to do!

Of course, it's still your job to `back up your files, and back up your backups`!



Contact
-------

For any inquiries or support, you can reach me at GrimHEX on use1c 020. (or `Spectrum
<https://robertsspaceindustries.com/spectrum/community/SC>`_. @AlpineFrost)




