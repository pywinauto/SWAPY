# Script to build with PyInstaller
# Authors: Denis Matiychuk
# License: CC0 1.0 Universal: http://creativecommons.org/publicdomain/zero/1.0/


function BuildExe ($python_version, $architecture, $python_home, $build_type) {
    Write-Host "Building with PyInstaller" $python_version "for" $architecture "bit architecture to" $python_home
	$pyinstaller_path = $python_home + "\Scripts\pyinstaller.exe"
	if ($build_type -eq "release") {
	    $args = "--clean swapy.spec"
	    $input_filename = "swapy.exe"
        if ($architecture -eq "32") {
            $out_filename = "swapy32bit.exe"
        } else {
            $out_filename = "swapy64bit.exe"
        }
    } else {
        $args = "--clean swapy-debug.spec"
        $input_filename = "swapy-debug.exe"
        if ($architecture -eq "32") {
            $out_filename = "swapy32bit-debug.exe"
        } else {
            $out_filename = "swapy64bit-debug.exe"
        }
    }

	Write-Host "Start building" $pyinstaller_path $args
    Start-Process -FilePath $pyinstaller_path -ArgumentList $args -Wait -Passthru

	Write-Host "Copy out file" .\dist\$input_filename .\$out_filename
	Copy-Item .\dist\$input_filename .\$out_filename
	
}

function main () {
	BuildExe $env:PYTHON_VERSION $env:PYTHON_ARCH $env:PYTHON "release"
	BuildExe $env:PYTHON_VERSION $env:PYTHON_ARCH $env:PYTHON "debug"
}

main
