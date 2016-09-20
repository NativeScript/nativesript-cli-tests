"""
Tests for run command in context of iOS
"""

import os

from core.base_class.BaseClass import BaseClass
from core.device.device import Device
from core.device.simulator import Simulator
from core.osutils.folder import Folder
from core.osutils.process import Process
from core.settings.settings import IOS_RUNTIME_SYMLINK_PATH, TNS_PATH
from core.tns.tns import Tns


class RuniOS(BaseClass):
    @classmethod
    def setUpClass(cls):
        logfile = os.path.join("out", cls.__name__ + ".txt")
        BaseClass.setUpClass(logfile)
        Device.ensure_available(platform="ios")
        Simulator.stop_simulators()

        Tns.create_app(cls.app_name_space)
        Tns.platform_add_ios(attributes={"--path":  "\"" + cls.app_name_space + "\"",
                                         "--frameworkPath": IOS_RUNTIME_SYMLINK_PATH,
                                         "--symlink": ""
                                         })
        Tns.create_app(cls.app_name)
        Tns.platform_add_ios(attributes={"--path": cls.app_name,
                                         "--frameworkPath": IOS_RUNTIME_SYMLINK_PATH,
                                         "--symlink": ""
                                         })

    def setUp(self):
        BaseClass.setUp(self)

        # Stoping simulators is required because of issue
        # https://github.com/NativeScript/nativescript-cli/issues/1904
        # TODO: Remove this after issue is fixed
        Simulator.stop_simulators()

    def tearDown(self):
        BaseClass.tearDown()
        # Stoping simulators is required because of issue
        # https://github.com/NativeScript/nativescript-cli/issues/1904
        # TODO: Remove this after issue is fixed
        Simulator.stop_simulators()

    @classmethod
    def tearDownClass(cls):
        Folder.cleanup('./' + cls.app_name_space)
        Folder.cleanup('./' + cls.app_name)
        Folder.cleanup('./' + cls.app_name_noplatform)
        Simulator.stop_simulators()

    def test_001_run_ios_justlaunch(self):
        output = Tns.run_ios(attributes={"--path": self.app_name,
                                         "--justlaunch": ""},
                             timeout=180, assert_success=False)
        assert "Project successfully prepared" in output
        assert "CONFIGURATION Debug" in output
        assert "Project successfully built" in output
        device_ids = Device.get_ids("ios")
        for device_id in device_ids:
            assert device_id in output

    def test_002_run_ios_release(self):
        output = Tns.run_ios(attributes={"--path": self.app_name,
                                         "--justlaunch": "",
                                         "--release": ""
                                         },
                             assert_success=False, timeout=180)
        assert "Project successfully prepared" in output
        assert "CONFIGURATION Release" in output
        assert "Project successfully built" in output
        assert "Successfully deployed on device" in output
        device_ids = Device.get_ids("ios")
        for device_id in device_ids:
            assert device_id in output

    def test_003_run_ios_simulator(self):
        output = Tns.run_ios(attributes={"--path": "\"" + self.app_name_space + "\"",
                                         "--justlaunch": "",
                                         "--emulator": ""
                                         },
                             timeout=180, assert_success=False)
        assert "Project successfully prepared" in output
        assert "CONFIGURATION Debug" in output
        assert "Project successfully built" in output
        assert "Successfully deployed on" in output
        assert Process.wait_until_running("Simulator", 60)

    def test_004_run_ios_release_simulator(self):
        output = Tns.run_ios(attributes={"--path": "\"" + self.app_name_space + "\"",
                                         "--emulator": "",
                                         "--release": "",
                                         "--justlaunch": ""
                                         },
                             assert_success=False, timeout=180)
        assert "Project successfully prepared" in output
        assert "CONFIGURATION Release" in output
        assert "Project successfully built" in output
        assert "Successfully deployed on" in output
        assert Process.wait_until_running("Simulator", 60)
        # TODO: Get device id and verify files are deployed and process is
        # running on this device

    def test_005_run_ios_default(self):
        output = Tns.run_ios(attributes={"--path": self.app_name}, timeout=60)
        assert "Project successfully prepared" in output
        assert "CONFIGURATION Debug" in output
        assert "Project successfully built" in output
        assert "Successfully deployed on device" in output
        assert "Successfully run application" in output

    def test_200_run_ios_inside_project(self):
        current_dir = os.getcwd()
        os.chdir(os.path.join(current_dir, self.app_name))
        output = Tns.run_tns_command("run ios", attributes={"--path": self.app_name,
                                                            "--justlaunch": ""},
                                     tns_path=os.path.join("..", TNS_PATH), timeout=180)
        os.chdir(current_dir)
        assert "Project successfully prepared" in output
        assert "CONFIGURATION Debug" in output
        assert "Project successfully built" in output
        assert "Successfully deployed on device" in output

    def test_301_run_ios_platform_not_added(self):
        Tns.create_app(self.app_name_noplatform)
        output = Tns.run_ios(attributes={"--path": self.app_name_noplatform,
                                         "--justlaunch": ""},
                             timeout=180)
        assert "Copying template files..." in output
        assert "Installing tns-ios" in output
        assert "Project successfully created." in output
        assert "Project successfully built" in output
        assert "Successfully deployed on device" in output

    def test_302_run_ios_device_not_connected(self):
        output = Tns.run_ios(attributes={"--path": self.app_name_noplatform,
                                         "--device": "xxxxx",
                                         "--justlaunch": ""},
                             timeout=180, assert_success=False)
        assert "Cannot resolve the specified connected device" in output
        assert "Project successfully prepared" not in output
        assert "Project successfully built" not in output
        assert "Successfully deployed on device" not in output
