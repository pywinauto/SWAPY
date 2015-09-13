# Script to build with PyInstaller
# Authors: Denis Matiychuk
# License: CC0 1.0 Universal: http://creativecommons.org/publicdomain/zero/1.0/


function BuildExe ($python_version, $architecture, $python_home) {
    Write-Host "Building with PyInstaller" $python_version "for" $architecture "bit architecture to" $python_home
	$pyinstaller_path = $python_home + "\Scripts\pyinstaller.exe"
	$args = "--clean swapy.spec"
	
	Write-Host "Run PyInstaller" $pyinstaller_path $args
    Start-Process -FilePath $pyinstaller_path -ArgumentList $args -Wait -Passthru

    if ($architecture -eq "32") {
        $out_filename = "swapy32bit.exe"
    } else {
        $out_filename = "swapy64bit.exe"
    }
	
	Write-Host "Copy out file" .\dist\swapy.exe .\$out_filename
	Copy-Item .\dist\swapy.exe .\$out_filename
	
}


function main () {
	BuildExe $env:PYTHON_VERSION $env:PYTHON_ARCH $env:PYTHON
}

main
