# -*- coding: utf-8 -*-
import sys
import os
import shutil

appName = ''
baseDir = ''
entitlementsFilePath = ''

def validateParam(dirPath, extension = ''):
    if not isinstance(dirPath, str):
        raise AssertionError(str("You should pass the " + extension + " path to this script calling."))
    if len(extension) > 0 and not dirPath.endswith(extension):
        raise AssertionError(str("File extension should be " + extension))
    return dirPath

def prepareForReCodeSign(ipaPath, provisionPath):
    resigningIPAPath = validateParam(ipaPath, '.ipa')
    provisionFilePath = validateParam(provisionPath, '.mobileprovision')
    os.system("security cms -D -i " + provisionFilePath + " > pendingProvision.plist")
    os.system("/usr/libexec/PlistBuddy -x -c \'Print:\'Entitlements\'\' pendingProvision.plist > entitlements_ori.plist")
    global appName
    appName = os.path.splitext(resigningIPAPath)[0]
    global baseDir
    baseDir = os.path.dirname(os.path.realpath(resigningIPAPath))
    global entitlementsFilePath
    entitlementsFilePath = "entitlements_ori.plist"
    os.system("rm -rf " + payloadPath())
    os.system("rm -rf pendingProvision.plist")

def payloadPath():
    path = os.path.join(baseDir, 'Payload')
    return path

def appFilePath():
    path = os.path.join(payloadPath(), appName + ".app")
    return path

def unzipIPA(ipaPath):
    os.system("unzip " + ipaPath)

def rebindBinary(embedFilePath):
    dylibPath = embedFilePath
    embedDylibFile = embedFilePath
    if embedDylibFile.endswith('.framework'):
        fileName = os.path.splitext(os.path.basename(embedDylibFile))[0]
        embedFilePath = os.path.join(fileName + ".framework", fileName)
        dylibPath = os.path.join(embedDylibFile, fileName)
    else:
        embedFilePath = os.path.join("Frameworks/", embedDylibFile)
    print(("Rebinding: " + embedFilePath))
    binaryPath = os.path.join(appFilePath(), appName)
    script = "install_name_tool -id @rpath/" + embedFilePath +" " + dylibPath
    # script = "install_name_tool -add_rpath @rpath/" + embedFilePath + " " + binaryPath    #use optool instead
    os.system("chmod +x " + binaryPath)
    print(("Rebind script: " + script))
    os.system(script)

def doInjection(injectionDir):
    if not injectionDir:
        print("ignore injection.")
        return
    frameworks = [f for f in os.listdir(injectionDir)]
    if len(frameworks) == 0:
        print("Nothing to inject.")
    else:
        print("List Injections:")
        print(frameworks)
        dirPath = os.path.join(appFilePath(), "Frameworks")
        for f in frameworks:
            source = os.path.join(injectionDir, f)
            if f.endswith('.DS_Store'):
                os.system("rm -f " + source)
            else:
                dest = os.path.join(dirPath, f)
                if os.path.exists(dest):
                    shutil.rmtree(dest)
                shutil.copytree(source, dest)
                rebindBinary(dest)
        print("Injection done.")
    

def reCodeSignFrameworks(certName):
    dirPath = os.path.join(appFilePath(), "Frameworks")
    frameworks = [os.path.join(dirPath, f) for f in os.listdir(dirPath)]
    for f in frameworks:
        os.system("codesign -fs \"" + certName + "\" " + f)

def replaceProvisionFile(provisionPath):
    dest = os.path.join(appFilePath(), "embedded.mobileprovision")
    shutil.copyfile(provisionPath, dest)

def mofidyInfoPlist(bundleId):
    filePath = appFilePath() + "/Info.plist"
    # os.system("plutil -convert xml1 " + filePath)
    os.system("plutil -replace CFBundleIdentifier -string " + bundleId + " " + filePath)
    # os.system("defaults write " + filePath + " CFBundleIdentifier -string " + bundleId)
    # os.system("/usr/libexec/PlistBuddy -c \'Set:CFBundleIdentifier string " + bundleId + "\' " + filePath)
    # os.system("plutil -convert binary1 " + filePath)

def resignApp(certName):
    os.system("codesign -fs \"" + certName + "\" --entitlements " + entitlementsFilePath + " " + appFilePath())

def zipAndNaming(name = ''):
    newName = name
    if len(name) == 0:
        newName = appName + "_resigned"
    os.system("cd " + baseDir + " run the commands")
    os.system("zip -ry " + newName + ".ipa Payload")

def finishWork():
    os.system("rm -rf " + payloadPath())
    os.system("rm -rf " + entitlementsFilePath)


def reCodeSignApp(resigningIPAPath, certificationName, provisionFilePath, bundleIdentifier, newName = '', injectionDir = None):
    prepareForReCodeSign(resigningIPAPath, provisionFilePath)
    unzipIPA(resigningIPAPath)
    doInjection(injectionDir)
    reCodeSignFrameworks(certificationName)
    replaceProvisionFile(provisionFilePath)
    mofidyInfoPlist(bundleIdentifier)
    resignApp(certificationName)
    zipAndNaming(newName)
    finishWork()

params = sys.argv
paramCount = len(params)
if paramCount <= 5:
    reCodeSignApp(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
elif paramCount ==  6:
    reCodeSignApp(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
else:
    reCodeSignApp(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])