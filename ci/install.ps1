# Script to install wxPython
# Authors: Denis Matiychuk
# License: CC0 1.0 Universal: http://creativecommons.org/publicdomain/zero/1.0/

$WX_32_URL = "http://www.lfd.uci.edu/~gohlke/pythonlibs/3i673h27/wxPython-3.0.2.0-cp27-none-win32.whl"
$WX_64_URL = "http://www.lfd.uci.edu/~gohlke/pythonlibs/3i673h27/wxPython-3.0.2.0-cp27-none-win_amd64.whl"
$WX_COMMON_URL = "http://www.lfd.uci.edu/~gohlke/pythonlibs/3i673h27/wxPython_common-3.0.2.0-py2-none-any.whl"


function InstallWX ($python_version, $architecture, $python_home) {
    Write-Host "Installing wxPython" $python_version "for" $architecture "bit architecture to" $python_home
	$pip_path = $python_home + "\Scripts\pip.exe"

    if ($architecture -eq "32") {
        $wx_wheel = $WX_32_URL
    } else {
        $wx_wheel = $WX_64_URL
    }
	$args = "install " + $wx_wheel + " " + $WX_COMMON_URL
	Write-Host "Install wheels" $args "by" $pip_path
    Start-Process -FilePath $pip_path -ArgumentList $args -Wait -Passthru
}


function main () {
	InstallWX $env:PYTHON_VERSION $env:PYTHON_ARCH $env:PYTHON
}

main
