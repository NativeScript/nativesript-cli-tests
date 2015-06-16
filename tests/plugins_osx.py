import os
import unittest

from helpers._os_lib import CleanupFolder, runAUT, FileExists
from helpers._tns_lib import CreateProjectAndAddPlatform, iosRuntimePath, \
    tnsPath, CreateProject


class Plugins_OSX(unittest.TestCase):
    
    def setUp(self):
        
        print ""
        print "#####"
        print self.id()
        print "#####"
        print ""
        
        CleanupFolder('./TNS_App');

    def tearDown(self):        
        pass

    def test_001_PluginAdd_Before_PlatformAdd_iOS(self):
        CreateProject(projName="TNS_App");        
        output = runAUT(tnsPath + " plugin add tns-plugin --path TNS_App")
        assert ("TNS_App/node_modules/tns-plugin" in output)
        assert ("Successfully installed plugin tns-plugin" in output)
        assert FileExists("TNS_App/node_modules/tns-plugin/index.js")
        assert FileExists("TNS_App/node_modules/tns-plugin/package.json")
        output = runAUT("cat TNS_App/package.json")
        assert ("org.nativescript.TNSApp" in output)
        assert ("dependencies" in output)
        assert ("tns-plugin" in output)
        
    def test_002_PluginAdd_After_PlatformAdd_iOS(self):
        CreateProjectAndAddPlatform(projName="TNS_App", platform="ios", frameworkPath=iosRuntimePath)    
        output = runAUT(tnsPath + " plugin add tns-plugin --path TNS_App");
        assert ("TNS_App/node_modules/tns-plugin" in output)
        assert ("Successfully installed plugin tns-plugin" in output)
        assert FileExists("TNS_App/node_modules/tns-plugin/index.js")
        assert FileExists("TNS_App/node_modules/tns-plugin/package.json")
        output = runAUT("cat TNS_App/package.json")
        assert ("org.nativescript.TNSApp" in output)
        assert ("dependencies" in output)
        assert ("tns-plugin" in output)
    
    def test_003_PluginAdd_InsideProject(self):
        CreateProjectAndAddPlatform(projName="TNS_App", platform="ios", frameworkPath=iosRuntimePath)     
        currentDir = os.getcwd()   
        os.chdir(os.path.join(currentDir,"TNS_App"))   
        output = runAUT(os.path.join("..", tnsPath) + " plugin add tns-plugin")
        os.chdir(currentDir);
        assert ("node_modules/tns-plugin" in output)
        assert ("Successfully installed plugin tns-plugin" in output)
        assert FileExists("TNS_App/node_modules/tns-plugin/index.js")
        assert FileExists("TNS_App/node_modules/tns-plugin/package.json")
        output = runAUT("cat TNS_App/package.json")
        assert ("org.nativescript.TNSApp" in output)
        assert ("dependencies" in output)
        assert ("tns-plugin" in output)

    def test_100_BuildAppWithPluginInsideProject(self):
        
        CreateProjectAndAddPlatform(projName="TNS_App", platform="ios", frameworkPath=iosRuntimePath)
        
        currentDir = os.getcwd()
        os.chdir(os.path.join(currentDir,"TNS_App"))
        output = runAUT(os.path.join("..", tnsPath) + " plugin add tns-plugin")
        os.chdir(currentDir);
        assert ("Successfully installed plugin tns-plugin" in output)
        
        output = runAUT(tnsPath + " build ios --path TNS_App")
        assert ("Project successfully prepared" in output) 
        assert ("Touch build/emulator/TNSApp.app" in output)  
        assert ("** BUILD SUCCEEDED **" in output)
        assert not ("ERROR" in output)   
        assert not ("malformed" in output)  
        
    def test_101_BuildAppWithPluginOutside(self):
        
        CreateProjectAndAddPlatform(projName="TNS_App", platform="ios", frameworkPath=iosRuntimePath)
        
        output = runAUT(tnsPath + " plugin add tns-plugin --path TNS_App")
        assert ("Successfully installed plugin tns-plugin" in output)
        
        output = runAUT(tnsPath + " build ios --path TNS_App")
        assert ("Project successfully prepared" in output) 
        assert ("Touch build/emulator/TNSApp.app" in output)  
        assert ("** BUILD SUCCEEDED **" in output)
        assert not ("ERROR" in output)   
        assert not ("malformed" in output)            
                
    def test_400_PluginAdd_NotExistingPlugin(self):
        CreateProject(projName="TNS_App");        
        output = runAUT(tnsPath + " plugin add fakePlugin --path TNS_App")
        assert ("Not Found: fakePlugin" in output)

    def test_401_PluginAdd_InvalidPlugin(self):
        CreateProject(projName="TNS_App");        
        output = runAUT(tnsPath + " plugin add wd --path TNS_App")
        assert ("wd is not a valid NativeScript plugin" in output)
        assert ("Verify that the plugin package.json file contains a nativescript key and try again" in output)