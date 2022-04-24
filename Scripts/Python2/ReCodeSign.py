# -*- coding: utf-8 -*-
import sys
import os
import shutil

appName = ''
baseDir = ''
entitlementsFilePath = ''

def validateParam(dirPath, extension = ''):
    if not isinstance(dirPath, basestring):
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


def reCodeSignApp(resigningIPAPath, certificationName, provisionFilePath, bundleIdentifier, newName = ''):
    prepareForReCodeSign(resigningIPAPath, provisionFilePath)
    unzipIPA(resigningIPAPath)
    reCodeSignFrameworks(certificationName)
    replaceProvisionFile(provisionFilePath)
    mofidyInfoPlist(bundleIdentifier)
    resignApp(certificationName)
    zipAndNaming(newName)
    finishWork()

reCodeSignApp(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])