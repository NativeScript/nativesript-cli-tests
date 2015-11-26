'''
Tests for livesync command in context of iOS simulator
'''

# C0111 - Missing docstring
# R0201 - Method could be a function
# pylint: disable=C0111, R0201

import psutil, subprocess, time, unittest

from helpers._os_lib import cleanup_folder, replace
from helpers._tns_lib import IOS_RUNTIME_SYMLINK_PATH, \
    create_project, platform_add, run
from helpers.device import stop_emulators
from helpers.simulator import create_simulator, delete_simulator, \
    cat_app_file_on_simulator, start_simulator, stop_simulators


class LiveSyncSimulator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        # setup simulator
        stop_emulators()
        stop_simulators()

        delete_simulator('iPhone 6s 90')
        create_simulator('iPhone 6s 90', \
            'iPhone 6s', '9.0')

        start_simulator('iPhone 6s 90')
        cleanup_folder('TNS_App')

        # setup app
        create_project(proj_name="TNS_App", copy_from="data/apps/livesync-hello-world")
        platform_add(platform="ios", framework_path=IOS_RUNTIME_SYMLINK_PATH, \
            path="TNS_App", symlink=True)
        run(platform="ios", emulator=True, path="TNS_App")

        # replace
        replace("TNS_App/app/main-page.xml", "TAP", "TEST")

        # livesync
        command = "tns livesync ios --emulator --watch --path TNS_App --log trace"
        print command
        cls.proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)

    def setUp(self):

        print ""
        print "#####"
        print self.id()
        print "#####"
        print ""

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        print "Killing subprocess ..."
        cls.proc.terminate()

        time.sleep(2)
        if psutil.pid_exists(cls.proc.pid):
            print "Forced killing subprocess ..."
            cls.proc.kill()

#         stop_simulators()
#         cleanup_folder('TNS_App')

    def wait_for_text_in_output(self, text):
        while True:
            line = self.proc.stdout.readline()
            if text in line:
                print " + Text \"{0}\" found in: ".format(text), line.rstrip()
                time.sleep(2)
                break
            else:
                print " - " + line

    def test_001_full_livesync(self):

        # TODO: To be updated with console.log() when supported.
        self.wait_for_text_in_output("prepared")

        output = cat_app_file_on_simulator("TNSApp", "app/main-page.xml")
        assert "<Button text=\"TEST\" tap=\"{{ tapAction }}\" />" in output
