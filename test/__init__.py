# coding: utf8
import sys
import os
import doctest
import unittest
import unittest2


PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))

# These packages are tested by default
DYKO_PACKAGES = ['kalamar', 'koral', 'kraken', 'test']


def run_with_coverage(run_function):
    import coverage
    import werkzeug
    c = coverage.coverage()
    c.exclude('return NotImplemented')
    c.exclude('raise NotImplementedError')
    c.exclude('except ImportError:')
    c.start()
    run_function()
    c.stop()
    filenames = []
    for package in DYKO_PACKAGES:
        for module in werkzeug.find_modules(package, include_packages=True,
                                            recursive=True):
            __import__(module)
            filenames.append(sys.modules[module].__file__)
    c.report(filenames)


def profile(function, filename):
    import cProfile
    cProfile.runctx('function()', {}, locals(), filename)

class DoctestLoader(unittest2.TestLoader):
    """
    A test loader that also loads doctests.
    """
    def loadTestsFromModule(self, module, use_load_tests=True):
        suite = unittest2.TestLoader.loadTestsFromModule(self, module,
                                                         use_load_tests)
        try:
            doctests = doctest.DocTestSuite(module)
        except ValueError, e:
            # doctest.DocTestSuite throws ValueError when there is no test
            if len(e.args) != 2 or e.args[1] != "has no tests":
                raise
        else:
            suite.addTest(doctests)
        return suite

def make_suite(names=None):
    """Build a test suite each from each package, module, 
    test case class or method name."""
    suite = unittest2.TestSuite()
    loader = DoctestLoader()
    for name in names or sys.argv[1:] or DYKO_PACKAGES:
        # Try unittest2’s discovery
        try:
            suite.addTest(loader.discover(name, '*.py', PROJECT_DIR))
        except ImportError:
            # name could be a class or a method
            suite.addTest(loader.loadTestsFromName(name))
    return suite


def run_suite(suite):
    """
    Run a test suite with output buferring and ctrl-C catching
    """
    # Control-C during the test run waits for the current test to end and then
    # Same as --catch :
    # reports all the results so far. A second control-C raises the normal
    # KeyboardInterrupt  exception.
    unittest2.installHandler()
    
    unittest2.TextTestRunner(buffer=True).run(suite)
    
def main():
    run_suite(make_suite())

def main_coverage():
    print "Running tests with coverage."
    run_with_coverage(main)

def main_profile(filename='./profile_results'):
    print "Profiling tests."
    profile(main, filename)
    print "Profile results saved in %r. " \
          "Use the pstats module to read it." % filename

