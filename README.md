# Code Retriever

A simple tool to download source code of [SPOJ](https://www.spoj.com) submissions and [Codeforces](https://www.codeforces.com) submissions including both regular and gym contests submissions.

## Features

* Download all accepted SPOJ submissions (requires spoj user and password)
* Download all accepted Codeforces submissions of a user (can use any handle)
* Download all accepted Codeforces gym submissions (requires your codeforces password) 
* If there are multiple accepted submissions for a problem, the last submission will be downloaded
* Keeps track of downloaded submissions so everytime you run it only new submissions will get downloaded
* Downloaded files path for SPOJ submissions will be `/spoj/user/problem_name` (ex: `/spoj/mohd_a/ACODE.cpp`)
* Downloaded files path for Codeforces will be `/codeforces/handle/` and then depends on what you choose:
    * If you choose to separate gym and regular contests, there will be `/codeforces/handle/gym` and `/codeforces/handle/regular`
    * If you choose to separate each contest in a different folder, a folder with contest's ID will be created for the submissions

Example paths:
    * Separated gym/regular and separated folders for contests: `/codeforces/handle/regular(or gym)/1266/A.cpp` 
    * Separated gym/regular but no separated folders for each contest: `/codeforces/handle/regular(or gym)/1266A.cpp` 
    * Not separated gym/regular but separated folders for each contest: `/codeforces/handle/1266/A.cpp` 
    * Not seperated gym/regular and no separated folders for each contest: `/codeforces/handle/1266A.cpp` 

## Getting Started

Below is a list of requirements and dependencies 

### Requirements

* [Python3](https://www.python.org) to run the tool
* Clone the repository:
```
git clone
```

### Dependencies

* **pip** - to install the required packages
* **requests** - used to get submissions pages
* **bs4** - BeautifulSoup to scrape pages and extract the source code of submissions

Install [pip](https://pip.pypa.io/en/stable/installing/) if you don't already have it installed

To download all dependencies use the following command:

```
pip3 install -r requirements.txt
```

or if you want to install one by one:

```
pip3 install bs4
pip3 install requests
```

## Usage

Navigate to the cloned repository's directory and run main.py

```
cd CodeRetriever
python3 main.py
```

If you want to use this in your existing project, copy `retriever.py` to your project's directory and use it as the following:

```python
from retriever import Retriever

starter = Retriever()
starter.start()

# you can also skip the input part and specifiy the arguments directly
starter = Retriever(cf_handle='handle', cf_password='password', spoj_handle='user', spoj_password='password', codeforces=True, spoj=True, get_regular=True, get_gym=True, split_gym=True, folders=True, verbose=True)
starter.start()

# spoj is a boolean specifying whether you want to download spoj submissions or not
# codeforces is a boolean specifying whether you want to download codeforces submissions or not
# get_regular is a boolean specifying whether you want to download regular contests submissions for codeforces
# get_gym is a boolean specifying whether you want to download gym contests submissions for codeforces
# split_gym is a boolean specifying whether you want gym submissions to be separated from regular ones, (gym and regular folders will be created)
# folders is a boolean specifying whether you want to separate each contest's submissions in a different folder (contest ID as folder name)
```

Codeforces password is only needed if `get_gym` is set to `True`, you can skip `password` if you want to get regular contest submissions only. Set `verbose` to `False` to run it without an output about status

## Author

* **Mohammed Al-Abdulhadi** - [Mohd-3](https://github.com/Mohd-3)

