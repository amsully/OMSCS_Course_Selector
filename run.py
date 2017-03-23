# Check compatibility
import sys

print("############################################")
print("Welcome to the OMSCS Course Selector Script!")
print("############################################")
assert sys.version_info >= (3,0), "\nRequires python 3. You are using: %r" % sys.version

import selector
main = selector.Selector()
main.run()