import unittest

from core.base_class.BaseClass import BaseClass
from core.device.emulator import Emulator
from core.device.simulator import Simulator
from core.npm.npm import Npm
from core.osutils.os_type import OSType
from core.settings.settings import ANDROID_KEYSTORE_PATH, \
    ANDROID_KEYSTORE_PASS, ANDROID_KEYSTORE_ALIAS, ANDROID_KEYSTORE_ALIAS_PASS, EMULATOR_ID, CURRENT_OS, \
    IOS_PACKAGE, ANDROID_PACKAGE, SIMULATOR_NAME, WEBPACK_PACKAGE, TYPESCRIPT_PACKAGE
from core.tns.replace_helper import ReplaceHelper
from core.tns.tns import Tns
from core.tns.tns_platform_type import Platform
from tests.webpack.helpers.helpers import Helpers


class WebPackHelloWorldNG(BaseClass):
    SIMULATOR_ID = ""

    image_original = 'hello-world-ng'
    image_change = 'hello-world-ng-js-css-xml'

    html_change = ['app/item/items.component.html', '[text]="item.name"', '[text]="item.id"']
    ts_change = ['app/item/item.service.ts', 'Ter Stegen', 'Stegen Ter']
    css_change = ['app/app.css', 'core.light.css', 'core.dark.css']

    @classmethod
    def setUpClass(cls):
        BaseClass.setUpClass(cls.__name__)
        Emulator.stop()
        Emulator.ensure_available()
        Tns.create_app_ng(cls.app_name, update_modules=True)
        Npm.uninstall(package="nativescript-dev-typescript", option='--save-dev', folder=cls.app_name)
        Npm.install(package=TYPESCRIPT_PACKAGE, option='--save-dev', folder=cls.app_name)
        Npm.install(package=WEBPACK_PACKAGE, option='--save-dev', folder=cls.app_name)
        Tns.platform_add_android(attributes={"--path": cls.app_name, "--frameworkPath": ANDROID_PACKAGE})

        if CURRENT_OS == OSType.OSX:
            Simulator.stop()
            cls.SIMULATOR_ID = Simulator.ensure_available(simulator_name=SIMULATOR_NAME)
            Tns.platform_add_ios(attributes={'--path': cls.app_name, '--frameworkPath': IOS_PACKAGE})

    def setUp(self):
        Tns.kill()
        Helpers.emulator_cleanup(app_name=self.app_name)
        BaseClass.tearDown(self)

    def tearDown(self):
        BaseClass.tearDown(self)
        Tns.kill()

    @classmethod
    def tearDownClass(cls):
        BaseClass.tearDownClass()

    def test_001_android_build_release_with_bundle(self):
        Tns.build_android(attributes={"--path": self.app_name,
                                      "--keyStorePath": ANDROID_KEYSTORE_PATH,
                                      "--keyStorePassword": ANDROID_KEYSTORE_PASS,
                                      "--keyStoreAlias": ANDROID_KEYSTORE_ALIAS,
                                      "--keyStoreAliasPassword": ANDROID_KEYSTORE_ALIAS_PASS,
                                      "--release": "",
                                      "--bundle": ""})

        Helpers.verify_size(app_name=self.app_name, config="ng-android-bundle")
        Helpers.run_android_via_adb(app_name=self.app_name, image=self.image_original)

    @unittest.skipIf(CURRENT_OS != OSType.OSX, "Run only on macOS.")
    def test_001_ios_build_release_with_bundle(self):
        Tns.build_ios(attributes={"--path": self.app_name, "--release": "", "--for-device": "", "--bundle": ""})
        Helpers.verify_size(app_name=self.app_name, config="ng-ios-bundle")

    def test_100_android_build_release_with_bundle_and_uglify(self):
        Tns.build_android(attributes={"--path": self.app_name,
                                      "--keyStorePath": ANDROID_KEYSTORE_PATH,
                                      "--keyStorePassword": ANDROID_KEYSTORE_PASS,
                                      "--keyStoreAlias": ANDROID_KEYSTORE_ALIAS,
                                      "--keyStoreAliasPassword": ANDROID_KEYSTORE_ALIAS_PASS,
                                      "--release": "",
                                      "--bundle": "",
                                      "--env.uglify": ""})

        Helpers.verify_size(app_name=self.app_name, config="ng-android-bundle-uglify")
        Helpers.run_android_via_adb(app_name=self.app_name, image=self.image_original)

    @unittest.skipIf(CURRENT_OS != OSType.OSX, "Run only on macOS.")
    def test_100_ios_build_release_with_bundle_and_uglify(self):
        # Hack due to https://github.com/NativeScript/nativescript-cli/issues/3415
        Tns.platform_remove(platform=Platform.IOS, attributes={"--path": self.app_name})
        Tns.platform_add_ios(attributes={'--path': self.app_name, '--frameworkPath': IOS_PACKAGE})

        Tns.build_ios(attributes={"--path": self.app_name, "--release": "", "--for-device": "", "--bundle": "",
                                  "--env.uglify": ""})

        Helpers.verify_size(app_name=self.app_name, config="ng-ios-bundle-uglify")

    @unittest.skipIf(CURRENT_OS == OSType.WINDOWS, "Windows can't build with snapshot.")
    def test_110_android_build_release_with_bundle_and_snapshot(self):
        Tns.build_android(attributes={"--path": self.app_name,
                                      "--keyStorePath": ANDROID_KEYSTORE_PATH,
                                      "--keyStorePassword": ANDROID_KEYSTORE_PASS,
                                      "--keyStoreAlias": ANDROID_KEYSTORE_ALIAS,
                                      "--keyStoreAliasPassword": ANDROID_KEYSTORE_ALIAS_PASS,
                                      "--release": "",
                                      "--bundle": "",
                                      "--env.snapshot": ""})

        Helpers.verify_size(app_name=self.app_name, config="ng-android-bundle-snapshot")
        Helpers.run_android_via_adb(app_name=self.app_name, image=self.image_original)

    @unittest.skipIf(CURRENT_OS == OSType.WINDOWS, "Windows can't build with snapshot.")
    def test_120_android_build_release_with_bundle_and_snapshot_and_uglify(self):
        Tns.build_android(attributes={"--path": self.app_name,
                                      "--keyStorePath": ANDROID_KEYSTORE_PATH,
                                      "--keyStorePassword": ANDROID_KEYSTORE_PASS,
                                      "--keyStoreAlias": ANDROID_KEYSTORE_ALIAS,
                                      "--keyStoreAliasPassword": ANDROID_KEYSTORE_ALIAS_PASS,
                                      "--release": "",
                                      "--bundle": "",
                                      "--env.uglify": "",
                                      "--env.snapshot": ""})

        Helpers.verify_size(app_name=self.app_name, config="ng-android-bundle-uglify-snapshot")
        Helpers.run_android_via_adb(app_name=self.app_name, image=self.image_original)

    def test_200_run_android_with_bundle_sync_changes(self):
        log = Tns.run_android(attributes={'--path': self.app_name,
                                          "--bundle": "",
                                          '--device': EMULATOR_ID}, wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=Helpers.wp_run, not_existing_string_list=Helpers.wp_errors,
                         timeout=180)
        Helpers.android_screen_match(image=self.image_original)
        Helpers.wait_webpack_watcher()

        # Change JS, XML and CSS
        ReplaceHelper.replace(self.app_name, self.ts_change)
        ReplaceHelper.replace(self.app_name, self.html_change)
        ReplaceHelper.replace(self.app_name, self.css_change)

        # Verify application looks correct
        Tns.wait_for_log(log_file=log, string_list=Helpers.wp_sync, not_existing_string_list=Helpers.wp_errors)
        Helpers.android_screen_match(image=self.image_change)

        # Revert changes
        ReplaceHelper.rollback(self.app_name, self.ts_change)
        ReplaceHelper.rollback(self.app_name, self.html_change)
        ReplaceHelper.rollback(self.app_name, self.css_change)

        # Verify application looks correct
        Tns.wait_for_log(log_file=log, string_list=Helpers.wp_sync, not_existing_string_list=Helpers.wp_errors)
        Helpers.android_screen_match(image=self.image_original)

    @unittest.skipIf(CURRENT_OS != OSType.OSX, "Run only on macOS.")
    def test_200_run_ios_with_bundle_sync_changes(self):
        log = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': '', '--bundle': ''}, wait=False,
                          assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=Helpers.wp_run, not_existing_string_list=Helpers.wp_errors,
                         timeout=240)
        Helpers.ios_screen_match(sim_id=self.SIMULATOR_ID, image=self.image_original)
        Helpers.wait_webpack_watcher()

        # Change JS, XML and CSS
        ReplaceHelper.replace(self.app_name, self.ts_change)
        ReplaceHelper.replace(self.app_name, self.html_change)
        ReplaceHelper.replace(self.app_name, self.css_change)

        # Verify application looks correct
        Tns.wait_for_log(log_file=log, string_list=Helpers.wp_sync, not_existing_string_list=Helpers.wp_errors)
        Helpers.ios_screen_match(sim_id=self.SIMULATOR_ID, image=self.image_change)

        # Revert changes
        ReplaceHelper.rollback(self.app_name, self.ts_change)
        ReplaceHelper.rollback(self.app_name, self.html_change)
        ReplaceHelper.rollback(self.app_name, self.css_change)

        # Verify application looks correct
        Tns.wait_for_log(log_file=log, string_list=Helpers.wp_sync, not_existing_string_list=Helpers.wp_errors)
        Helpers.ios_screen_match(sim_id=self.SIMULATOR_ID, image=self.image_original)

    def test_210_run_android_with_bundle_uglify_sync_changes(self):
        log = Tns.run_android(attributes={'--path': self.app_name,
                                          "--bundle": "",
                                          "--env.uglify": "",
                                          '--device': EMULATOR_ID}, wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=Helpers.wp_run, not_existing_string_list=Helpers.wp_errors,
                         timeout=180)
        Helpers.android_screen_match(image=self.image_original)
        Helpers.wait_webpack_watcher()

        # Change JS, XML and CSS
        ReplaceHelper.replace(self.app_name, self.ts_change)
        ReplaceHelper.replace(self.app_name, self.html_change)
        ReplaceHelper.replace(self.app_name, self.css_change)

        # Verify application looks correct
        Tns.wait_for_log(log_file=log, string_list=Helpers.wp_sync, not_existing_string_list=Helpers.wp_errors)
        Helpers.android_screen_match(image=self.image_change)

        # Revert changes
        ReplaceHelper.rollback(self.app_name, self.ts_change)
        ReplaceHelper.rollback(self.app_name, self.html_change)
        ReplaceHelper.rollback(self.app_name, self.css_change)

        # Verify application looks correct
        Tns.wait_for_log(log_file=log, string_list=Helpers.wp_sync, not_existing_string_list=Helpers.wp_errors)
        Helpers.android_screen_match(image=self.image_original)

    @unittest.skipIf(CURRENT_OS != OSType.OSX, "Run only on macOS.")
    def test_210_run_ios_with_bundle_uglify_sync_changes(self):
        log = Tns.run_ios(attributes={'--path': self.app_name, '--emulator': '', '--bundle': '', '--env.uglify': ''},
                          wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=Helpers.wp, not_existing_string_list=Helpers.wp_errors,
                         timeout=240)
        Helpers.ios_screen_match(sim_id=self.SIMULATOR_ID, image=self.image_original)
        Helpers.wait_webpack_watcher()

        # Change JS, XML and CSS
        ReplaceHelper.replace(self.app_name, self.ts_change)
        ReplaceHelper.replace(self.app_name, self.html_change)
        ReplaceHelper.replace(self.app_name, self.css_change)

        # Verify application looks correct
        Tns.wait_for_log(log_file=log, string_list=Helpers.wp_sync, not_existing_string_list=Helpers.wp_errors,
                         timeout=60)
        Helpers.ios_screen_match(sim_id=self.SIMULATOR_ID, image=self.image_change, timeout=60)

        # Revert changes
        ReplaceHelper.rollback(self.app_name, self.ts_change)
        ReplaceHelper.rollback(self.app_name, self.html_change)
        ReplaceHelper.rollback(self.app_name, self.css_change)

        # Verify application looks correct
        Tns.wait_for_log(log_file=log, string_list=Helpers.wp_sync, not_existing_string_list=Helpers.wp_errors,
                         timeout=60)
        Helpers.ios_screen_match(sim_id=self.SIMULATOR_ID, image=self.image_original, timeout=60)

    def test_320_run_android_with_bundle_snapshot_sync_changes(self):
        log = Tns.run_android(attributes={'--path': self.app_name,
                                          "--bundle": "",
                                          "--env.snapshot": "",
                                          '--device': EMULATOR_ID}, wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=Helpers.wp_run, not_existing_string_list=Helpers.wp_errors,
                         timeout=180)
        Helpers.android_screen_match(image=self.image_original)
        Helpers.wait_webpack_watcher()

        # Change JS, XML and CSS
        ReplaceHelper.replace(self.app_name, self.ts_change)
        ReplaceHelper.replace(self.app_name, self.html_change)
        ReplaceHelper.replace(self.app_name, self.css_change)

        # Verify application looks correct
        Tns.wait_for_log(log_file=log, string_list=Helpers.wp_sync, not_existing_string_list=Helpers.wp_errors,
                         timeout=60)
        Helpers.android_screen_match(image=self.image_change, timeout=60)

        # Revert changes
        ReplaceHelper.rollback(self.app_name, self.ts_change)
        ReplaceHelper.rollback(self.app_name, self.html_change)
        ReplaceHelper.rollback(self.app_name, self.css_change)

        # Verify application looks correct
        Tns.wait_for_log(log_file=log, string_list=Helpers.wp_sync, not_existing_string_list=Helpers.wp_errors,
                         timeout=60)
        Helpers.android_screen_match(image=self.image_original, timeout=60)

    def test_330_run_android_with_bundle_snapshot_and_uglify_sync_changes(self):
        log = Tns.run_android(attributes={'--path': self.app_name,
                                          "--bundle": "",
                                          "--env.snapshot": "",
                                          "--env.uglify": "",
                                          '--device': EMULATOR_ID}, wait=False, assert_success=False)
        Tns.wait_for_log(log_file=log, string_list=Helpers.wp_run, not_existing_string_list=Helpers.wp_errors,
                         timeout=180)
        Helpers.android_screen_match(image=self.image_original)
        Helpers.wait_webpack_watcher()

        # Change JS, XML and CSS
        ReplaceHelper.replace(self.app_name, self.ts_change)
        ReplaceHelper.replace(self.app_name, self.html_change)
        ReplaceHelper.replace(self.app_name, self.css_change)

        # Verify application looks correct
        Tns.wait_for_log(log_file=log, string_list=Helpers.wp_sync, not_existing_string_list=Helpers.wp_errors,
                         timeout=60)
        Helpers.android_screen_match(image=self.image_change, timeout=60)

        # Revert changes
        ReplaceHelper.rollback(self.app_name, self.ts_change)
        ReplaceHelper.rollback(self.app_name, self.html_change)
        ReplaceHelper.rollback(self.app_name, self.css_change)

        # Verify application looks correct
        Tns.wait_for_log(log_file=log, string_list=Helpers.wp_sync, not_existing_string_list=Helpers.wp_errors,
                         timeout=60)
        Helpers.android_screen_match(image=self.image_original, timeout=60)
