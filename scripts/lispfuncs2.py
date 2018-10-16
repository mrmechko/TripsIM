import glob, os, sys, re

functionList = {}

def findFuncs(dir):
    os.chdir(dir)
    # Populate list of functions
    """
    for file in glob.glob("*.lisp"):
        functionList[file] = []
        text = open(file, 'r').read()
        inds = [m.start() for m in re.finditer('defun', text)]
        for i in inds:
            functionList[file].append(text[i+6:text[i+6:].find('(')-1 + i + 6].replace(' nil', '').replace('\n', ''))
    """
    funcs = []
    text = open(sys.argv[2], 'r').read()
    inds = [m.start() for m in re.finditer('defun', text)]
    for i in inds:
        funcs.append(text[i+6:text[i+6:].find('(')-1 + i + 6].replace(' nil', '').replace('\n', ''))

    print("Functions defined in MatchEngine.lisp: ")
    for func in funcs:
        print("\t" + func)
    print("")

    # Check each file to see which functions from match engine are called
    for file in glob.glob("*.lisp"):
        print(file + ": ")
        i = 0
        for line in open(file, 'r').readlines():
            for func in funcs:
                if (line.find("(" + func + " ") != -1 or line.find("(" + func + "(") != -1) and line.find("defun " + func) == -1:
                    print("\t" + str(i) + ": " + func)
            i = i + 1

def main():
    findFuncs(sys.argv[1])

if __name__ == "__main__":
    main()