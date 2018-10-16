import glob, os, sys, re

functionList = {}

def findFuncs(dir):
    os.chdir(dir)
    # Populate list of functions
    for file in glob.glob("*.lisp"):
        functionList[file] = []
        text = open(file, 'r').read()
        inds = [m.start() for m in re.finditer('defun', text)]
        for i in inds:
            functionList[file].append(text[i+6:text[i+6:].find('(')-1 + i + 6].replace(' nil', '').replace('\n', ''))

    # Check each file to see which global functions are called
    for file in glob.glob("*.lisp"):
        text = open(file, 'r').read()
        print(file + ": ")
        for file2, functions in functionList.items():
            if file != file2:
                uses = []
                for function in functions:
                    if text.find("(" + function + " ") != -1 or text.find("(" + function + "(") != -1:
                        uses.append(function)
                if len(uses) > 0:
                    print("\t uses " + file2 + " with functions: ")
                    for u in uses:
                        print("\t\t" + u)
        print("")


def main():
    findFuncs(sys.argv[1])

if __name__ == "__main__":
    main()