from getpass import getpass
import os, time, requests, sys, traceback
from bs4 import BeautifulSoup as bs
from datetime import datetime
import colorama
import string

colorama.init()

COLOR_FAIL = "\033[91m"
COLOR_ENDC = "\033[0m"

class ErrorException(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return __repr__(self.message)

    def get_message(self):
        return self.message
        

class Submission:

    extensions = ((
            ('++', 'cpp'),
            ('GNU C', 'c'), 
            ('JavaScript', 'js'),
            ('Java', 'java'),
            ('Py', 'py'),
            ('Delphi', 'dpr'),
            ('FPC', 'pas'),
            ('C#', 'cs'),
            ('D', 'd'),
            ('Q#', 'qs'),
            ('Node', 'js'),
            ('Kotlin', 'kt'),
            ('Go', 'go'),
            ('Ruby', 'rb'),
            ('Rust', 'rs'),
            ('Perl', 'pl'),
            ('Scala', 'scala'),
            ('PascalABC', 'pas'),
            ('Haskell', 'hs'),
            ('PHP', 'php')
            ), (
            ('++', 'cpp'),
            ('gcc', 'c'), 
            ('clang', 'c'),
            ('JavaScript', 'js'),
            ('Java', 'java'),
            ('Python', 'py'),
            ('C#', 'cs'),
            ('D ', 'd'),
            ('Node', 'js'),
            ('Kotlin', 'kt'),
            ('Go ', 'go'),
            ('Ruby', 'rb'),
            ('Rust', 'rs'),
            ('Perl', 'pl'),
            ('Scala', 'scala'),
            ('Pascal', 'pas'),
            ('Haskell', 'hs'),
            ('PHP', 'php')
            ))

    def __init__(self, site, raw_data, gym, handle, merge):
        if site == 'codeforces':
            self.site = site
            self.contest_id = raw_data['contestId']
            self.submission_id = raw_data['id']
            self.creation_time = raw_data['creationTimeSeconds']
            self.problem_index = raw_data['problem']['index']
            self.language = raw_data['programmingLanguage']
            self.verdict = raw_data['verdict']
            self.problem = '{}{}'.format(self.contest_id, self.problem_index)
            self.contest_type = 'gym' if gym else 'contest'
            self.path = os.path.join('codeforces', handle)
            if not merge:
                if self.contest_type == 'contest':
                    self.path = os.path.join(self.path, 'normal')
                elif self.contest_type == 'gym':
                    self.path = os.path.join(self.path, 'gym')
        else:
            self.site = 'spoj'
            self.problem = raw_data['problem']
            self.language = raw_data['language']
            self.source = raw_data['source']
            self.submission_id = raw_data['id']
            self.path = os.path.join('spoj', handle)
        self.set_extension()

    def set_extension(self):
        self.extension = ''
        for key, value in self.extensions[self.site == 'spoj']:
            if key in self.language:
                self.extension = value
                break

    def get_id(self):
        return self.submission_id

    def get_creation_time(self):
        return datetime.fromtimestamp(self.creation_time)

    def get_contest(self):
        if self.site == 'codeforces':
            return self.contest_id
    
    def get_language(self):
        return self.language

    def get_verdict(self):
        return self.verdict

    def get_index(self):
        if self.site == 'codeforces':
            return self.problem_index

    def get_problem(self):
        return self.problem

    def is_gym(self):
        if self.site == 'codeforces':
            return self.contest_type == 'gym'

    def get_directory(self):
        return self.path

    def get_path(self):
        if self.site == 'codeforces':
            return '{}.{}'.format(self.problem_index, self.extension)
        return '{}.{}'.format(self.problem, self.extension)

    def __str__(self):
        if self.site == 'codeforces':
            return 'Platform: Codeforces, Submission: {}, Contest: {}, Problem: {}, Verdict: {}, When: {}'.format(self.get_id(), self.get_contest(), self.get_index(), self.get_verdict(), self.get_creation_time())
        return 'Platform: SPOJ, Submission: {}, Problem: {}'.format(self.get_id(), self.get_problem())


class Retriever:

    get_url = 'http://codeforces.com/{contest_type}/{contest_id}/submission/{submission_id}'

    def __init__(self, cf_handle=None, cf_password=None, spoj_handle=None, spoj_password=None, codeforces=None, spoj=None, get_regular=None, get_gym=None, split_gym=None, folders=None, verbose=True):
        self.cf_handle = cf_handle
        self.cf_password = cf_password
        self.codeforces = codeforces
        self.codeforces_once_more = True
        self.spoj = spoj
        self.spoj_handle = spoj_handle
        self.spoj_password = spoj_password
        self.get_regular = get_regular
        self.get_gym = get_gym
        self.split_gym = split_gym
        self.folders = folders
        self.verbose = verbose
   
    @staticmethod
    def check_path(path):
        if not os.path.exists(path):
            os.makedirs(path)
    
    @staticmethod
    def get_input(message):
        inp = ''
        while inp not in ('y', 'n'):
            inp = input(message).lower()
        return inp == 'y'
    
    def start(self):
        if self.codeforces is None:
            self.codeforces = self.get_input('Download codeforces submissions? [y/n]: ')
        if self.codeforces:
            if self.cf_handle is None:
                self.cf_handle = input('Enter your codeforces handle: ').lower()
            else:
                self.cf_handle = self.cf_handle.lower()
            if self.get_regular is None:
                self.get_regular = self.get_input('Download regular contests submissions? [y/n]: ')
            if self.get_gym is None:
                self.get_gym = self.get_input('Download gym contests submissions? [y/n]: ')
            if self.get_gym and self.cf_password is None:
                self.cf_password = getpass('Password is needed for gym contests, please enter password of {} : '.format(self.cf_handle))
            if self.split_gym is None:
                if not self.get_gym:
                    self.split_gym = True
                else:
                    self.split_gym = self.get_input('Separate regular and gym contests in different folders?: [y/n] ')
            if self.folders is None:
                    self.folders = self.get_input('Create folders separately for each contest? [y/n]: ')
        if self.spoj is None:
            self.spoj = self.get_input('Download spoj submissions? [y/n]: ')
        if self.spoj:
            if self.spoj_handle is None:
                self.spoj_handle = input('Enter your spoj username: ').lower()
            else:
                self.spoj_handle = self.spoj_handle.lower()
            if self.spoj_password is None:
                self.spoj_password = getpass('Enter your spoj password: ')
        if self.codeforces:
            while self.codeforces_once_more:
                if self.verbose:
                    print('Downloading codeforces submissions for : {}...'.format(self.cf_handle))
                self.gym_set = set()
                self.contests_set = set()
                with requests.Session() as self.req:
                    try:
                        self.get_info()
                        self.get_downloaded('codeforces', self.cf_handle)
                        self.errors = []
                        if self.get_gym and self.gym_set:
                            if not self.login():
                                raise ErrorException('Invalid handle/password')
                            if self.split_gym:
                                self.check_path(os.path.join(os.path.join('codeforces', self.cf_handle), 'gym'))
                            else:
                                self.check_path(os.path.join('codeforces', self.cf_handle))
                        if self.get_regular and self.contests_set:
                            if self.split_gym:
                                self.check_path(os.path.join(os.path.join('codeforces', self.cf_handle), 'normal'))
                            else:
                                self.check_path(os.path.join('codeforces', self.cf_handle))
                        self.data = self.req.get('http://codeforces.com/api/user.status?handle={}'.format(self.cf_handle)).json()
                        self.get_submissions()
                        self.set_downloaded('codeforces', self.cf_handle)
                        if self.errors:
                            if self.verbose:
                                print("Codeforces submissions for the following problems weren't downloaded:")
                                for error in set(self.errors):
                                    print(error)
                            self.codeforces_once_more = self.get_input('Do you want to run one more time to download them? [y/n]: ')
                        else:
                            self.codeforces_once_more = False
                        if self.verbose:
                            print('Done downloading codeforces submissions for : {}'.format(self.cf_handle))
                    except ErrorException as e:
                        if self.verbose:
                            print('Exception occured:\n{}'.format(e.get_message()))
                    except KeyboardInterrupt:
                        if self.downloaded:
                            self.set_downloaded('codeforces', self.cf_handle)
                        if self.verbose:
                            print('Keyboard interrupt (CTRL^C) was pressed, exiting.')
                        exit(0)
        if self.spoj:
            if self.verbose:
                print('Downloading spoj submissions...')
            with requests.Session() as self.req:
                try:
                    if not self.spoj_login():
                        raise ErrorException('Invalid username/password')
                    self.get_downloaded('spoj', self.spoj_handle)
                    self.errors = []
                    self.get_spoj_submissions()
                    self.set_downloaded('spoj', self.spoj_handle)
                    if self.errors and self.verbose:
                        print("SPOJ submissions for the following problems weren't downloaded:")
                        for error in set(self.errors):
                            print(error)
                        print('Run one more time to download them.')
                    if self.verbose:
                        print('Done downloading spoj submissions.')
                except ErrorException as e:
                    if self.verbose:
                        print('Exception occured:\n{}'.format(e.get_message()))
                except KeyboardInterrupt:
                    if self.downloaded:
                        self.set_downloaded('spoj', self.spoj_handle)
                    if self.verbose:
                        print('Keyboard interrupt (CTRL^C) was pressed, exiting.')
                    exit(0)

    def login(self):
        page = self.req.get('https://codeforces.com/enter')
        soup = bs(page.text, 'html.parser')
        time.sleep(2)
        data = {}
        token = soup.find('input', {"name":"csrf_token"})["value"]
        data['handleOrEmail'] = self.cf_handle
        data['password'] = self.cf_password
        data['csrf_token'] = token
        data['action'] = 'enter'
        chk = self.req.post('https://codeforces.com/enter', data=data)
        soup = bs(chk.text, 'html.parser')
        ret = soup.find('input', {'name': 'handleOrEmail'}) is None
        return ret
        
    def spoj_login(self):
        data = {'next_raw': '/', 'autologin': 1, 'login_user': self.spoj_handle, 'password': self.spoj_password}
        self.req.post('https://www.spoj.com', data=data)
        page = self.req.get('https://www.spoj.com/myaccount')
        soup = bs(page.text, 'html.parser')
        return soup.find('a', {'href': '/login'}) is None

    def get_info(self):
        for i, gym_status in enumerate(('false', 'true')):
            data = self.req.get('http://codeforces.com/api/contest.list?gym={}'.format(gym_status)).json()
            if data['status'] != 'OK':
                raise ErrorException('Error getting contests info.')
            for contest in data['result']:
                if i:
                    self.gym_set.add(contest['id'])
                else:
                    self.contests_set.add(contest['id'])

    def get_downloaded(self, site, handle):
        handle_path = os.path.join(site, handle)
        path = os.path.join(handle_path, 'downloaded')
        self.check_path(handle_path)
        if not os.path.exists(path):
            self.downloaded = set()
        else:
            with open(path, 'r') as f:
                self.downloaded = set(f.read().splitlines())
    
    def set_downloaded(self, site, handle):
        handle_path = os.path.join(site, handle)
        path = os.path.join(handle_path, 'downloaded')
        with open(path, 'w') as f:
            for x in self.downloaded:
                f.write(x + '\n')
        if self.errors:
            path = os.path.join(handle_path, 'errors')
            with open(path, 'w') as f:
                for x in self.errors:
                    f.write(x + '\n')

    def get_submissions(self):
        if self.data['status'] != 'OK':
            raise ErrorException('Error getting submission info.')
        submissions = (Submission('codeforces', raw_data, raw_data['contestId'] in self.gym_set, self.cf_handle, self.split_gym is False) for raw_data in self.data['result'])
        for submission in submissions:
            try:
                if submission.get_problem() in self.downloaded or (submission.is_gym() and not self.get_gym) or (not submission.is_gym() and not self.get_regular):
                    if self.verbose:
                        print('Already Downloaded for Problem {}, Skipping :{}'.format(submission.get_problem(), submission))
                    continue
                if submission.get_verdict().upper() != "OK":
                    if self.verbose:
                        print('Verdict : {}, Skipping :{}'.format(submission.get_verdict(), submission))
                    continue
                if self.verbose:
                    print('Downloading --> {}'.format(submission))
                self.get_source_code(submission)
                if self.result == '':
                    print(COLOR_FAIL + 'Source code fetch failed' + COLOR_ENDC)
                    self.errors.append(submission.get_problem())
                    continue
                self.process_submission(submission)
            except Exception as e:
                if self.verbose:
                    print(COLOR_FAIL + 'Exception occured:\n{}'.format(str(e)) + COLOR_ENDC)
                self.errors.append(submission.get_problem())

    def get_spoj_submissions(self):
        page = self.req.get('https://www.spoj.com/myaccount')
        soup = bs(page.text, 'html.parser')
        table = soup.find(id='user-profile-tables').find('table')
        rows = table.find_all('td')
        for row in rows:
            link = row.find('a')['href']
            splitted = link.split('/')[2].split(',')
            if len(splitted) == 1 or splitted[0] in self.downloaded or splitted[0] == '':
                continue
            page = self.req.get('https://spoj.com{}'.format(link))
            soup = bs(page.text, 'html.parser')
            edit = soup.find('a', {'title': 'Edit source code'})['href']
            page = self.req.get('https://spoj.com{}'.format(edit))
            sub_id = edit.split('=')[1]
            soup = bs(page.text, 'html.parser')
            lang = soup.find_all('option', {'selected': True})[0].text
            submission = Submission('spoj', {'language': lang, 'source': page.text, 'problem': splitted[0], 'id': sub_id}, False, self.spoj_handle, False)
            if self.verbose:
                print('Downloading --> {}'.format(submission))
            self.process_spoj_submission(submission)
            
    def get_source_code(self, submission):
        contest_type = 'gym' if submission.is_gym() else 'contest'
        page = self.req.get(self.get_url.format(contest_type=contest_type, contest_id=submission.get_contest(), submission_id=submission.get_id()))
        time.sleep(2)
        soup = bs(page.text, 'html.parser')
        ret = soup.find(id='program-source-text')
        if ret is None:
            self.result = ''
        else:
            self.result = ret.text.rstrip()
            printable = set(string.printable)
            self.result = ''.join(filter(lambda x: x in printable, self.result))

    def process_submission(self, submission):
        if self.folders:
            contest_path = os.path.join(submission.get_directory(), str(submission.get_contest()))
            self.check_path(contest_path)
            file_path = os.path.join(contest_path, submission.get_path())
        else:
            file_path = os.path.join(submission.get_directory(), submission.get_problem() + '.' + submission.extension)
        with open(file_path, 'w') as f:
            f.write('\n'.join(self.result.splitlines()))
        self.downloaded.add(submission.get_problem())
    
    def process_spoj_submission(self, submission):
        self.result = ''
        got = False
        cnt = 0
        for line in submission.source.splitlines():
            if 'textarea' in line:
                if got:
                    break
                got = True
            if got:
                if cnt == 0:
                    pos = line.index('>')
                    self.result += line[pos+1:]
                    cnt += 1
                else:
                    self.result += line
                self.result += '\n'
        if self.result:
            with open(os.path.join(submission.get_directory(), submission.get_path()), 'w') as f:
                f.write(self.result)
            self.downloaded.add(submission.get_problem())
        else:
            self.errors.append(submission.get_problem())

