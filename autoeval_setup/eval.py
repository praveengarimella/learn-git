import os.path, subprocess
from subprocess import STDOUT,PIPE
import re
import sys
import platform
import os.path
import hashlib
import base64
import json
# import crypt
def get_platform():
    platforms = {
        'linux1' : 'Linux',
        'linux2' : 'Linux',
        'darwin' : 'OS X',
        'win32' : 'Windows'
    }
    if sys.platform not in platforms:
        return sys.platform
    return platforms[sys.platform]

def check_git():
    try:
        run_proc = subprocess.Popen(['git'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except Exception as e:
        return False

def check_if_repo():
    run_proc = subprocess.Popen(['git', 'status'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = run_proc.communicate()
    if stderr: return False
    return True

def check_if_user():
    run_proc = subprocess.Popen(['git','config','user.name'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = run_proc.communicate()
    if stdout: return str(stdout)
    return False

def submit_score(score_obj,msg,cases,totalcases,score,totalscore):
    """ Take a score object and submit it to an endpoint
        kwargs:
        score object -- (<problemid>,<user.name>,<score>)
    """
    with open('md5/problem_id.txt', 'r') as f:
        data = f.read()
        if computeMD5hash(score_obj[0]) != data:
            print('Something is wrong with the problem ID. Result not generated.')
            return
    try:
        os.makedirs('result')
    except:
        pass

    try:
        scorejson = {'problem_id':score_obj[0],'user_id':score_obj[1].rstrip(),'score':score_obj[2],'pylint_score':score_obj[3]}
        with open('result/score.json','w') as f:
            json.dump(scorejson,f)
        with open('md5/score.txt','w') as f:
            f.write(computeMD5hash(str(f)))
        runProcess(["git","add", "."])
        runProcess(["git","commit", "-m","\""+ msg +" -> " + str(cases) + " of " + str(totalcases) + " passed." + " pylint: " + str(score) + "/" + str(totalscore) + " \""])
        runProcess(["git","push","-u","origin","master"])
        # r = requests.post("http://google.com", data={'problem_id':score_obj[0],'user_id':score_obj[1],'score':score_obj[2]})
        # if r.status_code == 200:
        #     print("A version of your code is submitted along with score.")
        # else:
        #     print("Something is not right with server. Report this error to incharge.")
    except Exception as e:
        print(e)
        print("Caution: Couldn't submit your code. Check internet connection or Git repo.")
        pass
    # return score_obj

def runProcess(command):
    run_proc = subprocess.Popen(command, stdout=subprocess.PIPE)
    proc_out = run_proc.stdout.read().decode('utf-8')
    print(proc_out)
    return proc_out
       

def which_python():
    if (sys.version_info > (3, 0)):
        return 3
    else:
        return 2

python_version = which_python()

def computeMD5hash(stringg):
    m = hashlib.md5()
    if python_version == 2:
        m.update(stringg.encode('utf8'))
    else:
        m.update(stringg)
    return m.hexdigest()

def get_content(filename):
    with open(filename, "rb") as f:
        return f.read()

def execute(file, stdin):
    from threading import Timer
    
    filename,ext = os.path.splitext(file)
    if ext == ".java":
        subprocess.check_call(['javac', "Solution.java"])     #compile
        cmd = ['java', "Solution"]                     #execute
    elif ext == ".c":
        subprocess.check_call(['gcc',"-o","Solution","Solution.c"])     #compile
        if(platform.system() == "Windows"):
            cmd = ['Solution']              #execute for windows OS.
        else:
            cmd = ['./Solution']            #execute for other OS versions
    else:
        cmd = ['python', file]
    
    kill = lambda process: process.kill()
    proc = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    
    my_timer = Timer(10, kill, [proc])
    try:
        my_timer.start()
        stdout,stderr = proc.communicate(stdin)
    except Exception as e:
        stdout = 'Caution: Your program is running for more than 10 seconds.'
    finally:
        my_timer.cancel()
    
    return stdout

def run_test(testcase_input,testcase_output):
    input1 = get_content('testcases/'+testcase_input)
    md5input = get_content("md5/"+testcase_input)
    output = get_content('testcases/'+testcase_output)
    md5output = get_content("md5/"+testcase_output)
    your_output = execute(program_name, input1)

    if python_version == 3:
        md5input = md5input.decode('utf-8')
        md5output = md5output.decode('utf-8')

    if computeMD5hash(input1) != md5input or computeMD5hash(output) != md5output:
        print(computeMD5hash(input1),md5input,computeMD5hash(output),md5output)
        return False

    if python_version == 3:
        your_output = your_output.decode('UTF-8').replace('\r','').rstrip() #remove trailing newlines, if any
        output = output.decode('UTF-8').replace('\r','').rstrip()
    else:
        your_output = your_output.replace('\r','').rstrip() #remove trailing newlines, if any
        output = output.replace('\r','').rstrip()

    return input1,output,your_output,output==your_output

def run_tests(inputs,outputs,extension):
    passed = 0
    problemid = get_content("testcases/problem_id.txt")
    for i in range(len(inputs)):
        result = run_test(inputs[i],outputs[i])
        if result == False:
            print("########## Testcase "+str(i)+": Failed ##########")
            print("Something is wrong with the testcase.\n")
        elif result[3] == True:
            print("########## Testcase "+str(i)+": Passed ##########")
            print("Expected Output: ")
            print(result[1]+"\n")
            print("Your Output: ")
            print(result[2]+"\n")
            passed+=1
        else:
            print("########## Testcase "+str(i)+": Failed ##########")
            print("Expected Output: ")
            print(result[1]+"\n")
            print("Your Output: ")
            print(result[2]+"\n")
        print("----------------------------------------")
    print("Result: "+str(passed)+"/"+str(len(inputs))+" testcases passed.")
    return (problemid, passed, len(inputs))

inputs = []
outputs = []

# populate input and output lists
for root,dirs,files in os.walk('testcases/'):
    for file in files:
        if 'input' in file and '.txt' in file and "md5" not in file:
            inputs.append(file)
        if 'output' in file and '.txt' in file and "md5" not in file:
            outputs.append(file)
    break

# if get_platform() == 'Windows':
if not check_git():
    raise Exception('git not available')

if not check_if_repo():
    raise Exception('You are not in git repo')

if not check_if_user():
    raise Exception('user not logged in')

inputs = sorted(inputs)
outputs = sorted(outputs)

if len(sys.argv)==2 and os.path.isfile(sys.argv[1]):
    if sys.argv[1].endswith(".java"):
        program_name = sys.argv[1]
        extension = ".java"
        result = run_tests(inputs,outputs,extension)

    elif sys.argv[1].endswith(".py"):
        program_name = sys.argv[1]
        extension = ".py"
        result = run_tests(inputs,outputs,extension)
    elif sys.argv[1].endswith(".c"):
        program_name = sys.argv[1]
        extension = ".c"
        result = run_tests(inputs,outputs,extension)
    elif sys.argv[1] == "eval.py":
        print("eval.py cannot be passed as argument")
    else:
        print("Invalid Extension.\nPass only .java or .py files")
else:
    print("File not found.\nPass a valid filename with extension as argument.\npython eval.py <filename>")

problemid, cases, totalcases = result
proc_out = runProcess(["pylint",program_name])
proc_out = re.findall("Your code has been rated at (.*)/(.*) \(.*\)", proc_out)
score, totalscore = 0,0
if proc_out:
    score = int(float(proc_out[0][0]))
    totalscore = int(float(proc_out[0][1]))
msg = ""
submit_score((problemid,check_if_user(),str(cases)+'/'+str(totalcases),str(score)+'/'+str(totalscore)), msg, cases, totalcases, score, totalscore)
