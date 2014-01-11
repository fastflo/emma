import sys
import datetime


class OutputHandler:
    def __init__(self, print_stdout=False, log_file=None, log_flush=False):
        self.stdout = sys.stdout
        self.print_stdout = print_stdout
        self.log_flush = log_flush
        sys.stdout = self
        if log_file:
            self.log_fp = file(log_file, "a+")
        else:
            self.log_fp = None
        self.debug = print_stdout or log_file

    def write(self, s):
        if self.print_stdout:
            self.stdout.write(s)
            if self.log_flush:
                self.stdout.flush()
        if self.log_fp:
            s = s.strip("\r\n")
            if not s:
                # do not write empty lines to logfile
                return 
            timestamp = str(datetime.datetime.now())[0:22]
            self.log_fp.write("%s %s\n" % (timestamp, s.replace("\n", "\n " + (" " * len(timestamp)))))
            if self.log_flush:
                self.log_fp.flush()