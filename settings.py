import os
import configparser


def delete_ini():

    if os.path.exists('SCFF.ini'):
        os.remove('SCFF.ini')
        print(f"SCFF.ini has been removed")
    else:
        print(f"SCFF.ini does not exist")

def defaults():
    shaders_path = os.path.join(os.getenv('LOCALAPPDATA'), "Star Citizen")
    eac_roaming_path = os.path.join(os.getenv('APPDATA'), "EasyAntiCheat")
    eac_programfiles_path = os.path.join(os.getenv('ProgramFiles(x86)'), "EasyAntiCheat_EOS")
    launcher_roaming_path = os.path.join(os.getenv('APPDATA'), "rsilauncher")
    defaults={
            'rsi_path': r"---NOT SET---",
            'shaders_path': shaders_path,
            'eac_roaming_path': eac_roaming_path,
            'eac_programfiles_path': eac_programfiles_path,
            'launcher_roaming_path': launcher_roaming_path,

        }

    return defaults

def read():
    if not os.path.isfile('SCFF.ini'):
        create_default_settings()
    verify_settings(populate=True)

    config = configparser.ConfigParser()
    config.read('SCFF.ini')

    settings = {}
    for key in config['Global']:
        settings[key] = config['Global'][key]

    return settings

def read_one(setting, section='Global'):
    if not os.path.isfile('SCFF.ini'):
        create_default_settings()

    config = configparser.ConfigParser()
    config.read('SCFF.ini')

    if setting in config[section]:
        value = config[section][setting]
    else:
        value = None

    return value

def write(settings):
    if not os.path.isfile('SCFF.ini'):
        create_default_settings()

    config = configparser.ConfigParser()

    if 'Global' not in config:
        config.add_section('Global')

    for key, value in settings.items():
        config.set('Global', key, value)

    with open('SCFF.ini', 'w') as configfile:
        config.write(configfile)

def verify_settings(required_keys=None, populate=False):
    if not os.path.isfile('SCFF.ini'):
        create_default_settings()

    if required_keys is None:
        required_keys = defaults().keys()

    config = configparser.ConfigParser()
    config.read('SCFF.ini')

    settings = {}

    if 'Global' not in config:
        print(f"Settings file does not contain required section: Global")
        if populate:
            print(f"Populating settings file with default values.")
            write(defaults())
            return True
        else:
            return False

    for key in config['Global']:
        settings[key] = config['Global'][key]

    for key in required_keys:
        if key not in settings:
            print(f"Settings file does not contain required key: {key}")
            if populate:
                print(f"Populating settings file with default value.")
                write_one(key, defaults()[key])
            else:
                return False

    return True


def create_default_settings(leave_blank=False):
    config = configparser.ConfigParser()
    stype='Default'

    if not leave_blank:
        config['Global'] = defaults()
    else:
        stype='Blank'

    with open('SCFF.ini', 'w') as configfile:
        config.write(configfile)
    print(f"SCFF.ini has been created with {stype} settings")


def write_one(setting, value, section='Global'):
    if setting == '' and value == '':
        return
    if not os.path.isfile('SCFF.ini'):
        create_default_settings()

    config = configparser.ConfigParser()
    config.read('SCFF.ini')

    if section not in config:
        config[section] = {}

    config[section][setting] = value

    with open('SCFF.ini', 'w') as configfile:
        config.write(configfile)

if __name__ == "__main__":
    pass
# delete_ini()
# create_default_settings(leave_blank=False)
#
# # write(defaults())
#
# write_one('setting23', '32')
# # print(read_one('setting3'))
# v=verify_settings(populate=False)
# print(v)