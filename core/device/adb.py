import os

from core.osutils.command import run
from core.osutils.command_log_level import CommandLogLevel
from core.osutils.file import File
from core.osutils.os_type import OSType
from core.settings.settings import CURRENT_OS

ANDROID_HOME = os.environ.get('ANDROID_HOME')
ADB_PATH = os.path.join(ANDROID_HOME, 'platform-tools', 'adb')


class Adb(object):
    @staticmethod
    def __find_aapt():
        """
        Find aapt tool under $ANDRODI_HOME/build-tools
        :return: Path to appt.
        """
        aapt_executable = 'aapt'
        if CURRENT_OS is OSType.WINDOWS:
            aapt_executable += '.exe'
        base_path = os.path.join(ANDROID_HOME, 'build-tools')
        return File.find(base_path=base_path, file_name=aapt_executable, exact_match=True)

    @staticmethod
    def __get_pacakge_id(apk_file):
        """
        Get package id from apk file.
        :param apk_file: Path to apk file.
        :return: Package identifier.
        """
        app_id = None
        aapt = Adb.__find_aapt()
        command = aapt + ' dump badging ' + apk_file
        output = run(command=command, log_level=CommandLogLevel.COMMAND_ONLY)
        for line in output.split('\n'):
            if 'package:' in line:
                app_id = line.split('\'')[1]
        return app_id

    @staticmethod
    def run(command, device_id, timeout=60, log_level=CommandLogLevel.COMMAND_ONLY):
        """
        Run adb command.
        :param command: Command to run (without adb in front).
        :param device_id: Device id.
        :param timeout: Timeout.
        :param log_level: Log level.
        :return: Output of executed command.
        """
        return run(ADB_PATH + ' -s ' + device_id + ' ' + command, timeout=timeout, log_level=log_level)

    @staticmethod
    def uninstall_all_apps(device_id):
        """
        Uninstall all 3rd party applications.
        :param device_id: Device id.
        """
        apps = Adb.run(command='shell pm list packages -3', device_id=device_id)
        for line in apps:
            if 'package:' in line:
                app = line.replace('package:', '')
                Adb.uninstall(app_id=app, device_id=device_id)

    @staticmethod
    def install(apk_file, device_id):
        """
        Install application.
        :param apk_file: Application under test.
        :param device_id: Device id.
        """
        output = Adb.run(command='install -r ' + apk_file, device_id=device_id)
        assert 'Success' in output, 'Failed to install {0}. \n Log: \n {1}'.format(apk_file, output)
        print '{0} installed successfully on {1}'.format(apk_file, device_id)

    @staticmethod
    def uninstall(app_id, device_id):
        """
        Uninstall application.
        :param app_id: Package identifier (for example org.nativescript.testapp).
        :param device_id: Device id.
        """
        output = Adb.run(command='shell pm uninstall ' + app_id, device_id=device_id)
        assert 'Success' in output, 'Failed to uninstall {0}. \n Log: \n {1}'.format(app_id, output)

    @staticmethod
    def monkey(apk_file, device_id):
        """
        Perform monkey testing.
        :param apk_file: Application under test.
        :param device_id: Device id.
        """
        Adb.__monkey_kill(device_id)
        app_id = Adb.__get_pacakge_id(apk_file)
        print 'Start monkey testing...'
        output = Adb.run(command='shell monkey -p ' + app_id + ' --throttle 100 -v 100 -s 120', device_id=device_id)
        assert 'No activities found' not in output, '{0} is not available on {1}'.format(app_id, device_id)
        assert 'Monkey aborted due to error' not in output, '{0} crashed! \n Log: \n {1}'.format(app_id, output)
        assert 'Monkey finished' in output, 'Unknown error occurred! \n Log: \n {0}'.format(output)
        print 'Monkey test passed!'

    @staticmethod
    def __monkey_kill(device_id):
        """
        Kill running adb monkey instances.
        :param device_id: device id.
        """
        kill_command = "shell ps | awk '/com\.android\.commands\.monkey/ { system(\"adb shell kill \" $2) }'"
        Adb.run(command=kill_command, device_id=device_id, log_level=CommandLogLevel.SILENT)
