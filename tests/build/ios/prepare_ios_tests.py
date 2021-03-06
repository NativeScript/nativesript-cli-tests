"""
Tests for prepare command in context of iOS
"""

import os.path
import re

from core.base_class.BaseClass import BaseClass
from core.device.simulator import Simulator
from core.osutils.command import run
from core.osutils.file import File
from core.osutils.folder import Folder
from core.settings.settings import IOS_PACKAGE, CURRENT_OS, OSType, TEST_RUN_HOME, ANDROID_PACKAGE, \
    PROVISIONING
from core.tns.replace_helper import ReplaceHelper
from core.tns.tns import Tns
from core.tns.tns_platform_type import Platform
from core.tns.tns_prepare_type import Prepare
from core.tns.tns_verifications import TnsAsserts


class PrepareiOSTests(BaseClass):
    @classmethod
    def setUpClass(cls):
        BaseClass.setUpClass(cls.__name__)
        if CURRENT_OS != OSType.OSX:
            raise NameError("Can not run iOS tests on non OSX OS.")
        else:
            Simulator.stop()
        Tns.create_app(cls.app_name)
        Tns.platform_add_ios(attributes={"--path": cls.app_name, "--frameworkPath": IOS_PACKAGE})
        Folder.copy(TEST_RUN_HOME + "/" + cls.app_name, TEST_RUN_HOME + "/data/TestApp")

    @classmethod
    def tearDownClass(cls):
        BaseClass.tearDownClass()
        Folder.cleanup(TEST_RUN_HOME + "/data/TestApp")

    def setUp(self):
        BaseClass.setUp(self)
        Folder.cleanup(self.app_name)
        Folder.copy(TEST_RUN_HOME + "/data/TestApp", TEST_RUN_HOME + "/TestApp")

    def tearDown(self):
        assert not Simulator.is_running()[0], 'iOS Simulator started after prepare!'

    def test_100_prepare_ios(self):
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_PACKAGE})

        # Initial prepare should be full.
        output = Tns.prepare_ios(attributes={"--path": self.app_name})
        TnsAsserts.prepared(self.app_name, platform=Platform.IOS, output=output, prepare=Prepare.FULL)

        # If no file is touched next time prepare should be skipped at all.
        output = Tns.prepare_ios(attributes={"--path": self.app_name}, assert_success=False)
        TnsAsserts.prepared(self.app_name, platform=Platform.IOS, output=output, prepare=Prepare.SKIP)

        # If some JS/CSS/XML is changed incremental prepare should be done.
        ReplaceHelper.replace(self.app_name, ReplaceHelper.CHANGE_JS)
        output = Tns.prepare_ios(attributes={"--path": self.app_name})
        TnsAsserts.prepared(self.app_name, platform=Platform.IOS, output=output, prepare=Prepare.INCREMENTAL)

        # Verify Xcode Schemes
        output = run("xcodebuild -project " + self.app_name + "/platforms/ios/TestApp.xcodeproj/ -list")
        assert "This project contains no schemes." not in output
        result = re.search("Targets:\n\s*TestApp", output)
        assert result is not None
        result = re.search("Schemes:\n\s*TestApp", output)
        assert result is not None

        # Initial prepare for other platform (Android) should be full.
        output = Tns.prepare_android(attributes={"--path": self.app_name})
        TnsAsserts.prepared(self.app_name, platform=Platform.ANDROID, output=output, prepare=Prepare.FULL)

        # Prepare original platform (iOS) should be skipped.
        output = Tns.prepare_ios(attributes={"--path": self.app_name}, assert_success=False)
        TnsAsserts.prepared(self.app_name, platform=Platform.IOS, output=output, prepare=Prepare.SKIP)

        # Initial prepare for other platform (Android) should be skipped.
        output = Tns.prepare_android(attributes={"--path": self.app_name}, assert_success=False)
        TnsAsserts.prepared(self.app_name, platform=Platform.ANDROID, output=output, prepare=Prepare.SKIP)

    def test_200_prepare_additional_appresources(self):
        # prepare project
        output = Tns.prepare_ios(attributes={"--path": self.app_name})
        TnsAsserts.prepared(self.app_name, platform=Platform.IOS, output=output, prepare=Prepare.FULL)

        # Create new files in AppResources
        File.copy(self.app_name + "/app/App_Resources/iOS/Assets.xcassets/AppIcon.appiconset/icon-76.png",
                  self.app_name + "/app/App_Resources/iOS/newDefault.png")

        # prepare project
        output = Tns.prepare_ios(attributes={"--path": self.app_name})
        TnsAsserts.prepared(self.app_name, platform=Platform.IOS, output=output, prepare=Prepare.INCREMENTAL)

        # Verify XCode Project include files from App Resources folder
        output = run("cat " + self.app_name + "/platforms/ios/TestApp.xcodeproj/project.pbxproj | grep newDefault.png")
        assert "newDefault.png" in output

    def test_201_prepare_ios_platform_not_added(self):
        Tns.platform_remove(platform=Platform.IOS, attributes={"--path": self.app_name}, assert_success=False)
        output = Tns.prepare_ios(attributes={"--path": self.app_name})
        TnsAsserts.prepared(self.app_name, platform=Platform.IOS, output=output, prepare=Prepare.FIRST_TIME)

    def test_220_build_ios_with_custom_plist(self):
        # Update Info.plist
        src_file = os.path.join(TEST_RUN_HOME, 'data', 'Info.plist')
        target_file = os.path.join(TEST_RUN_HOME, self.app_name, 'app', 'App_Resources', 'iOS', 'Info.plist')
        File.remove(target_file)
        File.copy(src=src_file, dest=target_file)

        # Prepare in debug
        final_plist = os.path.join(TEST_RUN_HOME, self.app_name, 'platforms', 'ios', 'TestApp', 'TestApp-Info.plist')
        Tns.prepare_ios(attributes={"--path": self.app_name})
        assert "<string>fbXXXXXXXXX</string>" in File.read(final_plist)
        assert "<string>orgnativescriptTestApp</string>" in File.read(final_plist)

        # Prepare in release
        Tns.prepare_ios(attributes={"--path": self.app_name, '--release': ''})
        assert "<string>fbXXXXXXXXX</string>" in File.read(final_plist)
        assert "<string>orgnativescriptTestApp</string>" not in File.read(final_plist)

    def test_300_prepare_ios_preserve_case(self):
        File.copy(self.app_name + "/node_modules/tns-core-modules/application/application-common.js",
                  self.app_name + "/node_modules/tns-core-modules/application/New-application-common.js")
        File.copy(self.app_name + "/node_modules/tns-core-modules/application/application.android.js",
                  self.app_name + "/node_modules/tns-core-modules/application/New-application.android.js")
        File.copy(self.app_name + "/node_modules/tns-core-modules/application/application.ios.js",
                  self.app_name + "/node_modules/tns-core-modules/application/New-application.ios.js")

        output = Tns.prepare_ios(attributes={"--path": self.app_name})
        TnsAsserts.prepared(self.app_name, platform=Platform.IOS, output=output, prepare=Prepare.FULL)

        # Verify case is preserved
        path = TnsAsserts._get_ios_modules_path(self.app_name)
        assert File.exists(path + 'application/New-application-common.js')
        assert File.exists(path + 'application/New-application.js')
        assert not File.exists(path + 'application/New-application.ios.js')

    def test_301_prepare_android_does_not_prepare_ios(self):
        Tns.plugin_add("nativescript-social-share", attributes={"--path": self.app_name})
        Tns.plugin_add("nativescript-iqkeyboardmanager@1.2.0", attributes={"--path": self.app_name})

        output = Tns.prepare_android(attributes={"--path": self.app_name})
        assert "nativescript-iqkeyboardmanager is not supported for android" in output
        assert "Successfully prepared plugin nativescript-social-share for android" in output

    def test_320_prepare_ios_with_provisioning(self):
        # Prepare with --provision (debug, emulator)
        Tns.prepare_ios(attributes={"--path": self.app_name, "--provision": PROVISIONING})

        # Prepare with --provision (release, emulator)
        Tns.prepare_ios(attributes={"--path": self.app_name, "--release": "", "--provision": PROVISIONING})

        # Prepare with --provision (debug, device)
        Tns.prepare_ios(attributes={"--path": self.app_name, "--forDevice": "", "--provision": PROVISIONING})

        # Prepare with --provision (release, device)
        Tns.prepare_ios(
            attributes={"--path": self.app_name, "--release": "", "--forDevice": "", "--provision": PROVISIONING})
