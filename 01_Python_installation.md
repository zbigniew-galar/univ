#### Basic Python installation set up
**Install Python from:**
https://www.python.org/downloads/release/python-3113/

**Install VS Code from:**
https://code.visualstudio.com/

1. Create folders for your code and data files in your main drive for example:

**Script files storage example folder:**
C://Repositories//Project//src//code

**Data storage example folder:**
C://Repositories//Project//src//data

2. Lunch MS Visual Studio Code.

3. In "Extensions" of VS Code install Python.

4. **Choose working directory:**

File -> Open Folder -> C://Repositories//Project//.

**To store Python abilities for our project we create a "venv" subfolder via terminal:**

##### Creating and activating environment
**If in PowerShell terminal (default for VS Code):**
``` powershell
py -m venv .venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\Activate.ps1
```
##### If in Command Prompt terminal
``` cmd
py -m venv .venv
.venv\Scripts\activate.bat
```
**For Mac:**
``` bash
# Prefer this (inside your project folder)
python3 -m venv .venv
source .venv/bin/activate

# Or with absolute path
python3 -m venv /Users/User_name/venv1
source /Users/User_name/venv1/bin/activate
```
**Upgrading libraries installation engine and installing libraries:**
``` powershell
# Upgrading
(venv) PS C:\Repositories\Project>python.exe -m pip install --upgrade pip
```
**Install data processing capabilities:**
``` powershell
(venv) PS C:\Repositories\Project>pip install pandas
```
**Install Excel processing capabilities:**
``` powershell
(venv) PS C:\Repositories\Project>pip install xlsxwriter
```
**or alternative Excel processing capabilities:**
``` powershell
(venv) PS C:\Repositories\Project>pip install openpyxl
```
**For Mac:**
``` bash
pip install pandas xlsxwriter openpyxl
```
**Check the python version:**
``` powershell
py 3 --version
```
**For Mac:**
``` powershell
python3 --version
```
