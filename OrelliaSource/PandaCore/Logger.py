import sys

#File like object that writes to stdout and one or more files
class Logger(object):
    def __init__(self, *args):
        self.terminal = sys.stdout
        self.logs = []
        for filename in args:
            try:
                f = open(filename, "a")
            except IOError as e:
                self.write("Could not write to file: " + filename +'\n')
            else:
                self.logs.append(f)

    def write(self, message):
        self.terminal.write(message)
        for log in self.logs:
            log.write(message)  