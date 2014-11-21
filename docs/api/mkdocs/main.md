main
=================================

from <a href="api/mkdocs">mkdocs</a>.main






### Public Function


def [arg_to_option](#def-arg_to_option)(arg)



def [main](#def-main)(cmd, args, options=None)



def [run_main](#def-run_main)()







Functions
------------------



### `def arg_to_option(arg)`




Convert command line arguments into two-tuples of config key/value pairs.





### `def main(cmd, args, options=None)`




Build the documentation, and optionally start the devserver.





### `def run_main()`




Invokes main() with the contents of sys.argv

This is a separate function so it can be invoked
by a setuptools console_script.



