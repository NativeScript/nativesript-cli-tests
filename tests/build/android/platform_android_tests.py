"""
Test platform add (android)
"""
import os

from core.base_class.BaseClass import BaseClass
from core.npm.npm import Npm
from core.osutils.file import File
from core.osutils.folder import Folder
from core.settings.settings import TNS_PATH, ANDROID_RUNTIME_PATH, TEST_RUN_HOME
from core.settings.strings import *
from core.tns.tns import Tns
from core.tns.tns_platform_type import Platform
from core.tns.tns_verifications import TnsAsserts


class PlatformAndroidTests(BaseClass):

    @classmethod
    def setUpClass(cls):
        BaseClass.setUpClass(cls.__name__)

    @classmethod
    def tearDownClass(cls):
        BaseClass.tearDownClass()

    def setUp(self):
        BaseClass.setUp(self)
        Folder.cleanup(self.app_name)

    def test_100_platform_add_android(self):
        """ Default `tns platform add` command"""
        Tns.create_app(self.app_name, update_modules=False)
        Tns.platform_add_android(attributes={"--path": self.app_name})

    def test_110_platform_add_android_framework_path(self):
        """ Add platform from local package"""
        Tns.create_app(self.app_name, update_modules=False)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_RUNTIME_PATH})

    def test_120_platform_add_android_inside_project(self):
        """ Add platform inside project folder (not using --path)"""
        Tns.create_app(self.app_name, update_modules=False)
        Folder.navigate_to(self.app_name)
        output = Tns.platform_add_android(tns_path=os.path.join("..", TNS_PATH), assert_success=False)
        Folder.navigate_to(TEST_RUN_HOME, relative_from_current_folder=False)
        TnsAsserts.platform_added(self.app_name, platform=Platform.ANDROID, output=output)

    def test_130_platform_remove_and_platform_add_android_custom_version(self):
        """Verify platform add supports custom versions"""

        # Add custom version number
        Tns.create_app(self.app_name, update_modules=False)
        Tns.platform_add_android(version="2.4.0", attributes={"--path": self.app_name})
        TnsAsserts.package_json_contains(self.app_name, ["\"version\": \"2.4.0\""])

        # Add remove
        Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name})

        # Add custom version with tag
        Tns.platform_add_android(version="rc", attributes={"--path": self.app_name})

    def test_200_platform_update_android(self):
        """Update platform"""

        # Create project with tns-android@2.4.0
        Tns.create_app(self.app_name, update_modules=False)
        Tns.platform_add_android(version="2.4.0", attributes={"--path": self.app_name})
        TnsAsserts.package_json_contains(self.app_name, ["\"version\": \"2.4.0\""])

        # Update platform to 2.5.0
        Tns.platform_update(platform=Platform.ANDROID, version="2.5.0", attributes={"--path": self.app_name})
        TnsAsserts.package_json_contains(self.app_name, ["\"version\": \"2.5.0\""])

    def test_210_platform_update_android_when_platform_not_added(self):
        """`platform update` should work even if platform is not added"""
        Tns.create_app(self.app_name, update_modules=False)
        output = Tns.platform_update(platform=Platform.ANDROID, attributes={"--path": self.app_name},
                                     assert_success=False)
        TnsAsserts.platform_added(self.app_name, platform=Platform.ANDROID, output=output)

    def test_220_platform_clean_android(self):
        """Prepare after `platform clean` should add the same version that was before clean"""

        # Create project with tns-android@2.4.0
        Tns.create_app(self.app_name, update_modules=False)
        Tns.platform_add_android(version="2.4.0", attributes={"--path": self.app_name})
        TnsAsserts.package_json_contains(self.app_name, ["\"version\": \"2.4.0\""])

        # Clean platform and verify platform is 2.4.0
        Tns.platform_clean(platform=Platform.ANDROID, attributes={"--path": self.app_name})
        TnsAsserts.package_json_contains(self.app_name, ["\"version\": \"2.4.0\""])

    def verify_update(self, output):
        assert "Platform android successfully removed" in output
        assert "Successfully removed plugin tns-core-modules" in output
        assert "Successfully removed plugin tns-core-modules-widgets" in output
        assert "Project successfully created" in output
        assert "Successfully installed plugin tns-core-modules" in output

    def test_230_tns_update(self):
        """ Default `tns platform add` command"""
        Tns.create_app(self.app_name, update_modules=False)
        Tns.platform_add_android(attributes={"--path": self.app_name}, version="latest")

        output = Tns.update(attributes={"--path": self.app_name})
        self.verify_update(output)
        modules_version = Npm.get_version("tns-core-modules")
        TnsAsserts.package_json_contains(self.app_name, [modules_version])

        output = Tns.update(attributes={"3.2.0": "", "--path": self.app_name})
        self.verify_update(output)
        TnsAsserts.package_json_contains(self.app_name, ["3.2.0"])

        Tns.update(attributes={"next": "", "--path": self.app_name})
        self.verify_update(output)
        modules_version = Npm.get_version("tns-android@next")
        android_version = Npm.get_version("tns-core-modules@next")
        TnsAsserts.package_json_contains(self.app_name, [modules_version, android_version])

    def test_300_set_sdk(self):
        """Platform add android should be able to specify target sdk with `--sdk` option"""
        Tns.create_app(self.app_name, update_modules=False)
        Tns.platform_add_android(attributes={"--path": self.app_name,
                                             "--frameworkPath": ANDROID_RUNTIME_PATH, "--sdk": "19"})

        manifest = os.path.join(self.app_name, TnsAsserts.PLATFORM_ANDROID_SRC_MAIN_PATH, "AndroidManifest.xml")
        output = File.read(manifest)
        assert "android:minSdkVersion=\"17\"" in output
        assert "android:targetSdkVersion=\"19\"" in output

    def test_310_set_sdk_not_installed(self):
        Tns.create_app(self.app_name, update_modules=False)
        output = Tns.platform_add_android(attributes={"--path": self.app_name,
                                                      "--frameworkPath": ANDROID_RUNTIME_PATH, "--sdk": "29"})

        assert "Support for the selected Android target SDK android-29 is not verified. " + \
               "Your Android app might not work as expected." in output

        manifest = os.path.join(self.app_name, TnsAsserts.PLATFORM_ANDROID_SRC_MAIN_PATH, "AndroidManifest.xml")
        output = File.read(manifest)
        assert "android:minSdkVersion=\"17\"" in output
        assert "android:targetSdkVersion=\"29\"/>" in output

    def test_390_platform_list(self):
        """Platform list command should list installed platforms and if app is prepared for those platforms"""

        Tns.create_app(self.app_name, update_modules=False)

        # `tns platform list` on brand new project
        output = Tns.platform_list(attributes={"--path": self.app_name})
        TnsAsserts.platform_list_status(output=output, prepared=Platform.NONE, added=Platform.NONE)

        # `tns platform list` when android is added
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_RUNTIME_PATH})
        output = Tns.platform_list(attributes={"--path": self.app_name})
        TnsAsserts.platform_list_status(output=output, prepared=Platform.NONE, added=Platform.ANDROID)

        # `tns platform list` when android is prepared
        Tns.prepare_android(attributes={"--path": self.app_name})
        output = Tns.platform_list(attributes={"--path": self.app_name})
        TnsAsserts.platform_list_status(output=output, prepared=Platform.ANDROID, added=Platform.ANDROID)

    def test_400_platform_list_wrong_path(self):
        output = Tns.run_tns_command("platform list")
        assert "No project found at or above" in output
        assert "and neither was a --path specified." in output

        output = Tns.run_tns_command("platform list", attributes={"--path": "invalidPath"})
        assert "No project found at or above" in output
        assert "and neither was a --path specified." in output

    def test_420_platform_add_existing_platform(self):
        self.test_110_platform_add_android_framework_path()
        output = Tns.platform_add_android(attributes={"--path ": self.app_name}, assert_success=False)
        assert "Platform android already added" in output

    def test_421_platform_add_android_wrong_option(self):
        Tns.create_app(self.app_name, update_modules=False)

        # frameworkPath point to missing file
        output = Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": "invalidFile.tgz"},
                                          assert_success=False)
        assert "npm ERR!" in output or "exit code" in output
        assert "invalidFile.tgz" in output

        # Wrong frameworkPath option
        output = Tns.platform_add_android(attributes={"--path": self.app_name, "--" + invalid: "tns-android.tgz"},
                                          assert_success=False)
        assert invalid_option.format(invalid) in output

        # Empty platform, only `tns platform add`
        output = Tns.platform_add(attributes={"--path": self.app_name}, assert_success=False)
        assert no_platform in output
        assert "Usage" in output

    def test_430_platform_remove_missing_invalid_or_empty_platform(self):
        Tns.create_app(self.app_name, update_modules=False)

        output = Tns.platform_remove(platform=Platform.ANDROID, attributes={"--path": self.app_name},
                                     assert_success=False)
        assert "The platform android is not added to this project"
        assert "Usage" in output

        output = Tns.platform_remove(platform="invalidPlatform", attributes={"--path": self.app_name},
                                     assert_success=False)
        assert "Invalid platform invalidplatform. Valid platforms are ios or android." in output
        assert "Usage" in output

        output = Tns.platform_remove(attributes={"--path": self.app_name}, assert_success=False)
        assert no_platform in output
        assert "Usage" in output

    def test_440_platform_update_empty_platform(self):
        Tns.create_app(self.app_name, update_modules=False)
        output = Tns.platform_update(attributes={"--path": self.app_name}, assert_success=False)
        assert no_platform in output
        assert "Usage" in output
