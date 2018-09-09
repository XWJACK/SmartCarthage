#! /usr/local/bin/python3
import sys
import os
import shutil

carthage_file = 'Cartfile'
# Only Supporting iOS
carthage_path = 'Carthage/Build/iOS/'

openStep_runScript_begin = '/* Begin PBXShellScriptBuildPhase Carthage section */\n'
openStep_runScript_end = '/* End PBXShellScriptBuildPhase Carthage section */\n'

openStep_FrameworkSearchPath_Key = 'FRAMEWORK_SEARCH_PATHS'
openStep_FrameworkSearchPath_Carthage = '$(PROJECT_DIR)/Carthage/Build/iOS'

openStep_TargetBuildPhases_Isa = 'isa = PBXNativeTarget;'
openStep_TargetBuildPhases_ProductType_Key = 'productType = '
openStep_TargetBuildPhases_ProductType = 'com.apple.product-type.application'
openStep_TargetBuildPhases = 'buildPhases = ('

openStep_Carthage_Debug_UUID = 'AAAABBBBCCCCDDDDEEEEFFFF'
openStep_Carthage_Release_UUID = 'FFFFEEEEDDDDCCCCBBBBAAAA'

current_path = os.path.dirname(os.path.abspath('__file__'))

def restoryProjectFiles():
    pass

project_name = ''
xcodeproj_path = ''
def findProjectFile():
    global project_name
    global xcodeproj_path
    project_paths = [ f for f in os.listdir(current_path) if f[-10:] == '.xcodeproj' ]
    if len(project_paths) != 0:
        project_name = project_paths[0]
        xcodeproj_path = os.path.join(project_name, 'project.pbxproj')
        print('Find project name' + project_name)
    else:
        print('Can not search xcode project automic, you should specific a xcodeproj file and retry again.')
        sys.exit(1)

debug_list = []
release_list = []
def parseCarthageFile():
    global debug_list
    global release_list
    carthage_fp = open(carthage_file, 'r')
    for line in carthage_fp.readlines():
        if line[-9:] == '#[Debug]\n':
            debug_list.append(line)
        elif line[-11:] == '#[Release]\n':
            release_list.append(line)
    carthage_fp.close()


def carthageUpdate(argv):
    os.system('/usr/local/bin/carthage ' + ' '.join(argv))


frameworks = []
def listFrameworks():
    global frameworks
    framework_path = os.path.join(current_path, carthage_path)
    frameworks = [ f for f in os.listdir(framework_path) if f[-9:] == 'framework' ]
    print(frameworks)


def parseProject():
    # Read xcodeproj all lines
    lines = []
    with open(xcodeproj_path, 'r') as fp:
        lines = fp.readlines()

    def configFrameworkSearchPath():
        for index, line in enumerate(lines):
            if openStep_FrameworkSearchPath_Key in line:
                isAleardySearchFrameworkPath = False
                for subIndex, subLine in enumerate(lines[index:]):
                    if openStep_FrameworkSearchPath_Carthage in subLine:
                        isAleardySearchFrameworkPath = True
                        print('Carthage search path config right.')
                        break
                    if ');' in subLine:
                        if not isAleardySearchFrameworkPath:
                            lines.insert(index + subIndex, '\t\t\t\t\t"%s",\n' % openStep_FrameworkSearchPath_Carthage)
                            print('Add %s to %s.' % (openStep_FrameworkSearchPath_Carthage, openStep_FrameworkSearchPath_Key))
                        break
        # else:
        #     print('⚠️ SmartCarthage could not find %s config, may be you need add %s manual.' % (openStep_FrameworkSearchPath_Key, openStep_FrameworkSearchPath_Carthage))

    isNewInDebug = False
    isNewinRelease = False

    def configBuildPhases():
        for index, line in enumerate(lines):
            if openStep_TargetBuildPhases_Isa in line:
                # Find application target
                isApplicationTarget = False
                for subIndex, subLine in enumerate(lines[index:]):
                    if openStep_TargetBuildPhases_ProductType_Key in subLine:
                        if openStep_TargetBuildPhases_ProductType in subLine:
                            isApplicationTarget = True
                            break
                        else:
                            break

                if isApplicationTarget:
                    for subIndex, subLine in enumerate(lines[index:]):
                        if openStep_TargetBuildPhases in subLine:
                            isAleardyHasDebugUUID = False
                            isAleardyHasReleaseUUID = False
                            for ssIndex, ssLine in enumerate(lines[index + subIndex:]):
                                if openStep_Carthage_Debug_UUID in ssLine:
                                    isAleardyHasDebugUUID = True
                                    print('UUID for Debug is aleardy have in line: %d' % int(index + subIndex + ssIndex))
                                if openStep_Carthage_Release_UUID in ssLine:
                                    isAleardyHasReleaseUUID = True
                                    print('UUID for Release is aleardy have in line: %d' % int(index + subIndex + ssIndex))
                                if isAleardyHasDebugUUID and isAleardyHasReleaseUUID:
                                    break
                                if ');' in ssLine:
                                    if not isAleardyHasDebugUUID:
                                        lines.insert(index + subIndex + ssIndex, '\t\t\t\t%s /* Smart Carthage Copy Framework [Debug] */,\n' % openStep_Carthage_Debug_UUID)
                                        isAleardyHasDebugUUID = True
                                        isNewInDebug = True
                                        print('Inseart new UUID for Debug in line: %d' % int(index + subIndex + ssIndex))
                                    if not isAleardyHasReleaseUUID:
                                        lines.insert(index + subIndex + ssIndex, '\t\t\t\t%s /* Smart Carthage Copy Framework [Release] */,\n' % openStep_Carthage_Release_UUID)
                                        isAleardyHasReleaseUUID = True
                                        isNewinRelease = True
                                        print('Inseart new UUID for Release in line: %d' % int(index + subIndex + ssIndex))
                                    break
                            # Stop search if aleardy have.
                            if isAleardyHasDebugUUID and isAleardyHasReleaseUUID:
                                break

#    modeConfig = """
#    """
#    def configRunScripte():
#        for index, line in enumerate(lines):
#            if 'rootObject = ' in line:
#                if isNewInDebug:


    configFrameworkSearchPath()
    configBuildPhases()

    # Write new xcdoeproj config
    with open(xcodeproj_path, 'w') as fp:
        fp.writelines(lines)

def main():
    findProjectFile()
    parseCarthageFile()
    # carthageUpdate(sys.argv[1:])
    listFrameworks()
    parseProject()
    
    
    
    

if __name__ == '__main__':
    main()

# rfp = open('./project.pbxproj', 'r')

# for line in rfp.readlines():
#     if line == '/* Begin PBXShellScriptBuildPhase section */\n':
