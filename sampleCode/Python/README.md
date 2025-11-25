# IMPLAN Impact API - Python Workflow Examples

## Introduction
This is a collection of example workflow scripts written for modern Python - `3.13.5`.  

## ⚡ Installation and Execution

- Two environment variables must be specified for authentication:
  - `IMPLAN_USERNAME` = Your IMPLAN username
  - `IMPLAN_PASSWORD` = Your IMPLAN password
- You may also create an `.env` file in the same directory as `main.py` that specifies them:
  ```env
  # IMPLAN Impact API Auth Variables
  IMPLAN_USERNAME="{YOUR USER NAME HERE}"
  IMPLAN_PASSWORD="{YOUR PASSWORD HERE}"
  ```
  - **Note:** You might need to include the first comment line for the `.env` file to be read properly.
- You may need to install several Python packages in order to run these scripts.
  - [Installing Packages](https://packaging.python.org/en/latest/tutorials/installing-packages/)
- Execution starts in `main.py`; examine that file for more details on what examples are available.
- It is fully intended for the code in this project to be copied + pasted, modified, and reused for your purposes; this code is release under [The MIT License](https://opensource.org/license/mit). 


## 📂 Folders
- The `endpoints` folder contains a collection of classes that implement `ApiEndpoint`, all of these group together related Impact API endpoints into simple methods.
- The `models` folder contains Python class definitions for various Models used by the endpoints, such a Projects, Groups, and Events.
- The `utilites` folder contains several classes that assist with Authorization/Authentication, json serialization, logging, and sending and receiving REST requests.
- The `workflow_examples` folder contains several example scripts that perform various common workflows.
- While running the scripts, several folders may be created:
  - `logs` - Will contain logging information from this script's operation, useful for debugging.
  - `reports` - Exported Reports will be stored in this directory by default.

## 🔗 Links

### IMPLAN
- [Impact API Wiki](https://github.com/Implan-Group/api/wiki)
- [Impact API github](https://github.com/Implan-Group/api/)

### 🐍 [Python](https://www.python.org/)
- [Beginner's Guide](https://wiki.python.org/moin/BeginnersGuide/Download)

### 🗔 IDEs
- [PyCharm](https://www.jetbrains.com/pycharm/) - from JetBrains, **free**, used to develop these scripts
  - [Installation](https://www.jetbrains.com/help/pycharm/installation-guide.html)
  - [Quick Start Guide](https://www.jetbrains.com/help/pycharm/quick-start-guide.html)
  - [Getting Started](https://www.jetbrains.com/help/pycharm/getting-started.html)
- [Visual Studio Code](https://code.visualstudio.com/) - from Microsoft, **free**
  - [VSC Python Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) - extension for Python development
- [Spyder](https://www.spyder-ide.org/) - **free** community IDE

### 📦 Packages used in these scripts:
- [uuid](https://docs.python.org/3/library/uuid.html) - [uuid | guid](https://en.wikipedia.org/wiki/Universally_unique_identifier) support
- [typing](https://docs.python.org/3/library/typing.html) - support for type hints
- [logging](https://docs.python.org/3/library/logging.html) - logging
- [os](https://docs.python.org/3/library/os.html) - operating system support for environment variables and file access
- [requests](https://pypi.org/project/requests/) - sending REST requests
- [sys](https://docs.python.org/3/library/sys.html) - system console access to set encoding to properly display logs
- [datetime](https://docs.python.org/3/library/datetime.html) - date and time support
- [json](https://docs.python.org/3/library/json.html) - JSON support
- [humps](https://humps.readthedocs.io/en/latest/) - String case conversion
- [pathvalidate](https://pypi.org/project/pathvalidate/) - OS Path validation and sanitization
---

Written without the use of any 'AI' tools.