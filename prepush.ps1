# Go to the home directory of the project (location where this script is)
Set-Location -Path $PSScriptRoot

# Run the linters
flake8 --ignore=E501 .

# Run pylint
# $lint_files = @(Get-ChildItem -Path $PSScriptRoot -Filter *.py -r | % { $_.FullName })
# Foreach ($file in $lint_files) {
#     if (-Not($file -like "*__init__.py")) {
#         echo $file
#         pylint $file
#     }
# }

# Run the unittests
pytest


# Use "pip list --outdated" to check outdated packages
#
# Upgrade all packages
# type "powershell" in terminal
# run "pip freeze | %{$_.split('==')[0]} | %{pip install --upgrade $_}"