#!/usr/bin/env python
import glob
import optparse
import os 
import re
import stat
import sys

"""
A simple tool, similar to the ls command, which provides the biggest missing feature:
  prefixing of listed files with their relative or canonical path
"""

PATHS_NONE      = 0
PATHS_ABSOLUTE  = 1
PATHS_CANONICAL = 2

class ListFiles(object):
    def __init__(self, depth=-1, path_mode=PATHS_NONE, ignore_symlinks=False, verbosity=0):
        object.__init__(self)

        self._depth = depth
        self._path_mode = path_mode
        self._ignore_symlinks = ignore_symlinks
        self._verbosity = verbosity

        # TODO: include a dictionary tracking the canonical paths of symlinked
        #       directories in order to detect loops

        # TODO: eventually we can determine whether a symlink steps outside of
        #       our source directory, and only recurse into those which do not

    def process(self, path_list):
        for path in path_list:
            path = os.path.abspath(path)
            if not os.path.exists(path):
                print "%s: path not found" % path
            else:
                self._process_path(path, self._depth)

    def _process_path(self, path, depth):
        if depth == 0: return
        if not os.path.exists(path):
            print "%s: path not found" % path
        if os.path.isdir(path):
            if os.path.basename(path) == ".ssh":
                print "%s: skipping SSH config directory " % path
                print "  (if you want this changed, do it yourself)"
            try:
                for extension in os.listdir(path):
                    self._process_path(os.path.abspath(path + '/' + extension), depth - 1)
            except OSError, e:
                print "%s: cannot read directory contents, permission denied" % path
        self._edit_permissions(path)

    def _edit_permissions(self, path):
        try:
            file_stat = os.stat(path)
        except:
            print "%s: cannot get permissions, permission denied" % path
            return
        mode = file_stat[stat.ST_MODE]
        if stat.S_ISDIR(mode):
            if (self._type == TYPE_FILE):
                if self._verbosity > 0:
                    print "skipping directory '%s'" % path
                return
        if stat.S_ISREG(mode):
            if (self._type == TYPE_DIR):
                if self._verbosity > 0:
                    print "skipping regular file '%s'" % path
                return
        if stat.S_ISCHR(mode):
            if (self._type != TYPE_ALL):
                if self._verbosity > 0:
                    print "skipping character device '%s'" % path
                return
        if stat.S_ISBLK(mode):
            if (self._type != TYPE_ALL):
                if self._verbosity > 0:
                    print "skipping block device '%s'" % path
                return
        if stat.S_ISFIFO(mode):
            if (self._type != TYPE_ALL):
                if self._verbosity > 0:
                    print "skipping fifo '%s'" % path
                return
        if stat.S_ISLNK(mode):
            if (self._type != TYPE_ALL):
                if self._verbosity > 0:
                    print "skipping symbolic link '%s'" % path
                return
        if stat.S_ISSOCK(mode):
            if (self._type != TYPE_ALL):
                if self._verbosity > 0:
                    print "skipping socket '%s'" % path
                return

        self._print_details(path, mode)

    def _print_details(self, path, mode):
        # TODO: add prefix and details
        print path

class Main:
    def __init__(self):
        option_list = []
        option_list.append(optparse.make_option("-a", "--absolute-paths", dest="absolute_paths", action="store_true", help="Will prefix every listed file/directory with its absolute path (not compatible with the -c option)."))
        option_list.append(optparse.make_option("-c", "--canonical-paths", dest="canonical_paths", action="store_true", help="Will prefix every listed file/directory with its canonical path (not compatible with the -a option)."))
        option_list.append(optparse.make_option("-d", "--depth", dest="depth", action="store", type="int", help="Recurse this many levels (includes current level). Must be an integer greater than zero."))
        option_list.append(optparse.make_option("-i", "--ignore-symlinks", dest="ignore_symlinks", action="store_true", help="Ignore symlinks to directories when recursing."))
        option_list.append(optparse.make_option("-r", "--recursive", dest="rescursive", action="store_true", help="Recursive directory traversal with no depth limit (see --depth option for limited depth recursion)."))
        option_list.append(optparse.make_option("-v", dest="verbosity", action="count", help="specify multiple times to increase verbosity"))
        self.parser = optparse.OptionParser(option_list=option_list)
        self.parser.set_usage("""Usage: %prog [options] [path1 [path2 ...]]

Lists out .""")

    def usage(self, message=''):
        if message != '':
            print "E:", message
        self.parser.print_help()
        sys.exit(1)

    def start(self):
        self.options, self.args = self.parser.parse_args()

        regex_mask = re.compile('^[DEIP]{3}$')

        depth     = 1 # No limit
        arg_paths = PATHS_NONE
        verbosity = 0
        ignore_symlinks = False

        if self.options.absolute_paths:
            if arg_paths > 0:
                self.usage("You may only supply one of -a, -c")
            arg_paths = PATHS_ABSOLUTE

        if self.options.canonical_paths:
            if arg_paths > 0:
                self.usage("You may only supply one of -a, -c")
            arg_paths = PATHS_CANONICAL

        mask = arg_user + arg_group + arg_other

        if self.options.depth:
            if depth != 1:
                self.usage("You may only supply one of -d, -r")
            if self.options.depth < 1:
                self.usage("Depth must be greater than zero")
            depth = self.options.depth

        if self.options.recursive:
            if depth != 1:
                self.usage("You may only supply one of -d, -r")
            depth = -1

        if self.options.ignore_symlinks:
            ignore_symlinks = self.options.ignore_symlinks

        if self.options.verbosity:
            verbosity = self.options.verbosity

        ListFiles(depth, path_mode, ignore_symlinks, verbosity).process(self.args)

if __name__ == '__main__':
    try:
        Main().start()
    except KeyboardInterrupt:
        print


