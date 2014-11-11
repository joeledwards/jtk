#!/usr/bin/env python
import os
import shlex
import subprocess
import sys
import threading
import time

"""
This Shell object simplifies the process of writing scripts.

execute(command, [stdin], [stdout], [stderr], [die]) - this method can be used in order to execute shell commands.

log(message, [category]) - this method can be used to log information whose lines
are cleanly differentiated from the exec output
"""
class Shell(object):
    def __init__(self, simulate=False):
        object.__init__(self)
        self.simulate=simulate

    def log(self, message, category=None):
        now = time.time()
        millis = int(now / 1.0 * 1000 % 1000)
        format = "%%Y-%%m-%%d %%H:%%M:%%S.%03d UTC" % millis
        time_str = time.strftime(format, time.gmtime(now))
        if category is not None:
            category = " " + category
        else:
            category = ""
        print "[%s]%s> %s" % (time_str, category, message)

    def run(self):
        self.script()

    def script(self):
        raise NotImplementedError("The script() method must be replaced with the functionality of your script.")

    def execute(self, command, stdin=None, stdout=sys.stdout, stderr=sys.stderr, die=False):
        exec_func = self.simulation_exec if self.simulate else self.real_exec
        return exec_func(command, stdin=stdin, stdout=stdout, stderr=stderr, die=die)

    def simulation_exec(self, command, stdin=None, stdout=sys.stdout, stderr=sys.stderr, die=False):
        print "[simulation] command> %s" % command
        return 0

    def real_exec(self, command, stdin=None, stdout=sys.stdout, stderr=sys.stderr, die=False):
        cmd = Command(command, stdin=stdin, stdout=stdout, stderr=stderr)
        status_code = cmd.execute()

        if die and status_code != 0:
            sys.exit(status_code)

        return status_code

"""
This class wraps the logic for executing a command and forwarding input/output.
"""
class Command(object):
    def __init__(self, command, stdin=None, stdout=None, stderr=None):
        object.__init__(self)

        self.command = command
        self.process = None

        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

        self.stdin_pipe = None
        self.stdout_pipe = None
        self.stderr_pipe = None

    def execute(self):
        stdin_method = None
        if (self.stdin is not None):
            stdin_method = subprocess.PIPE

        stdout_method = None
        if (self.stdout is not None):
            stdout_method = subprocess.PIPE

        stderr_method = None
        if (self.stderr is not None):
            stderr_method = subprocess.PIPE

        self.process = subprocess.Popen(shlex.split(self.command), stdout=stdout_method, stderr=stderr_method, stdin=stdin_method)

        self.start_pipes()
        self.process.wait()
        self.halt_pipes()

        return self.process.returncode

    def get_return_code(self):
        return self.return_code

    def kill(self):
        self.process.kill()
        self.halt_pipes()

    def start_pipes(self):
        if (self.stdin is not None):
            self.stdin_pipe = Pipe(self.stdin, self.process.stdin)
            self.stdin_pipe.start()

        if (self.stdout is not None):
            self.stdout_pipe = Pipe(self.process.stdout, self.stdout)
            self.stdout_pipe.start()

        if (self.stderr is not None):
            self.stderr_pipe = Pipe(self.process.stderr, self.stderr)
            self.stderr_pipe.start()

    def halt_pipes(self):
        if (self.stdin_pipe is not None):
            self.stdin_pipe.halt()
            self.stdin_pipe.join()

        if (self.stdout_pipe is not None):
            self.stdout_pipe.halt()
            self.stdout_pipe.join()

        if (self.stderr_pipe is not None):
            self.stderr_pipe.halt()
            self.stderr_pipe.join()

"""
This class wraps the logic for forwarding the output of a file-like object to
the input of another file-like object.
"""
class Pipe(threading.Thread):
    def __init__(self, input, output):
        threading.Thread.__init__(self)
        self.running = False
        self.input = input
        self.output = output

    def halt(self):
        self.running = False

    def run(self):
        self.running = True
        c = 'a'

        try:
            while self.running or (c is not None and c != ''):
                c = self.input.read(1)
                self.output.write(c)
                self.output.flush()
        except Exception, e:
            sys.stderr.write("Error while forwarding pipe data: %s\n" % str(e))

class TestShell(Shell):
    def __init__(self):
        Shell.__init__(self)

    def script(self):
        self.log("Testing simple directory listing...")
        code = self.execute("ls -l")

        if code == 0:
            self.log("Done.")
        elif code is None:
            self.log("Did not wait for subprocess to complete!")
        else:
            self.log("Operation failed.")

class TestKill(Shell):
    def __init__(self):
        Shell.__init__(self)
        self.cmd = Command("sleep 2")

    def run(self):
        self.log("launching kill thread...")
        threading.Thread(target=self.kill).start()
        self.log("executing command...")
        self.cmd.execute()
        self.log("done.")

    def kill(self):
        time.sleep(0.50)
        self.log("killing command...")
        self.cmd.kill()
        self.log("dead.")

def main():
    print "Testing simple Shell implementation..."
    TestShell().run()

    time.sleep(1.0)

    print "Testing killing of active Command..."
    TestKill().run()

if __name__ == "__main__":
    main()

