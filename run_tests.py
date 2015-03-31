import os
import platform

from helpers._os_lib import CleanupFolder, runAUT
from helpers._tns_lib import UninstallCLI, InstallCLI, GetAndroidRuntime, GetiOSRuntime, \
    androidRuntimeSymlinkPath, iosRuntimeSymlinkPath, androidRuntimePath, iosRuntimePath
from helpers.device import StopEmulators
import tns_tests_runner


smokeTestResult = ""

def ExecuteTests():
    print "####RUNNING TESTS####"
    global smokeTestResult
    smokeTestResult = str(tns_tests_runner.RunTests())

def AnalyzeResultAndExit():
    global smokeTestResult
    if not ("errors=0" in smokeTestResult) or not ("failures=0" in smokeTestResult):
        exit(1)
    else:
        exit(0)

if __name__ == '__main__':
   
    # Cleanup old runtimes
    
    CleanupFolder(os.path.split(androidRuntimeSymlinkPath)[0])
    CleanupFolder(os.path.split(iosRuntimeSymlinkPath)[0])
    if os.path.isfile(androidRuntimePath):
        os.remove(androidRuntimePath)
    if os.path.isfile(iosRuntimePath):
        os.remove(iosRuntimePath)
               
    # Cleanup folders created by test execution
    CleanupFolder('TNS App')
    CleanupFolder('TNS App')
    CleanupFolder('TNS_TempApp')
    CleanupFolder('folder')
    CleanupFolder('template')
    CleanupFolder('tns_modules')
    CleanupFolder('tns_helloworld_app')
    
    # Uninstall previous CLI and install latest   
    UninstallCLI()
    InstallCLI()
                
    # Get latest Android and iOS runtimes
    GetAndroidRuntime()
    if 'Darwin' in platform.platform():
        GetiOSRuntime()
 
    # Clone hello-world template repo 
    CleanupFolder('template-hello-world')
    output = runAUT("git clone git@github.com:NativeScript/template-hello-world.git template-hello-world")
    assert not ("fatal" in output), "Failed to clone git@github.com:NativeScript/template-hello-world.git"
    
    # Execute tests
    ExecuteTests()
    
    # Stop running emulators 
    if ('TESTRUN' in os.environ) and (not "SMOKE" in os.environ['TESTRUN']):       
        StopEmulators()
    
    # Exit        
    AnalyzeResultAndExit()