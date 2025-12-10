# Code Retriever 2.0

_This has been fully rewritten since Codeforces and SPOJ use cloudflare turnstile now, and codeforces restricted submission view access to the owner._

A simple tool to download source code of [SPOJ](https://www.spoj.com) and [Codeforces](https://www.codeforces.com) submissions including both regular and gym contests.

## Features

- Download all accepted SPOJ submissions (requires spoj username and password)
- Download all accepted Codeforces submissions of a user (requires username and password)
- Download all accepted Codeforces gym submissions (requires username and password)
- If there are multiple accepted submissions for a problem, the last accepted submission will be downloaded
- Keeps track of downloaded submissions so everytime you run it only new submissions will get downloaded
- Downloaded files path for SPOJ submissions will be `/spoj/user/problem_name` (ex: `/spoj/user/ACODE.cpp`)
- Downloaded files path for Codeforces will be `/codeforces/handle/` and then depends on what you choose:
  - If you choose to separate gym and regular contests, there will be `/codeforces/handle/gym` and `/codeforces/handle/regular`
  - If you choose to separate each contest in a different folder, a folder with contest's ID will be created for the submissions

  Example paths:
  - Separated gym/regular and separated folders for contests: `/codeforces/handle/regular(or gym)/1266/A.cpp`
  - Separated gym/regular but no separated folders for each contest: `/codeforces/handle/regular(or gym)/1266A.cpp`
  - Not separated gym/regular but separated folders for each contest: `/codeforces/handle/1266/A.cpp`
  - Not seperated gym/regular and no separated folders for each contest: `/codeforces/handle/1266A.cpp`

## Getting Started

Below is a list of requirements and dependencies

### Requirements

- [Python3](https://www.python.org) to run the tool
- Clone the repository:

```
git clone https://github.com/Mohd-3/CodeRetriever.git
```

### Dependencies

Create a virtual environment:

```
python3 -m venv venv
source venv/bin/activate
```

Download the dependencies:

```
pip install -r requirements.txt
```

## Usage

**This is not headless anymore, a browser will launch for you to solve the turnstile/captcha before proceeding**

1.  Run:

```
python main.py
```

2. Enter the required input
3. Solve turnstile/captcha when the browser launches
4. Minimize everything while it downloads all accepted submissions

## Author

- **Mohammed Al-Abdulhadi** - [Mohd-3](https://github.com/Mohd-3)
