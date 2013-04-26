Greetings
=========

It seems you're trying to help us build Satchless. Here are some ground rules:

* **Test your code.** The testing harness is set to fail if test coverage falls
  below a certain value¹.

* **Write documentation.** Code people don't know how to use is as good as code
  that does not exist.

* Don't be afraid to open pull requests. Open them early and use them to
  discuss proposed changes.

¹ That value is currently set to 100%. *Yes, 100%.*


Testing your changes
--------------------

Once you've changed the code you might (and should!) want to check if your
changes do not break existing code. To test your code, run the following
command:

    $ python setup.py nosetests

Or, if you're lucky enough to use Python 3.x:

    $ python3 setup.py nosetests


Python support
--------------

We do most of our work using Python 2.7 but the CI server is set to run tests
using versions 2.6, 2.7, 3.2 and 3.3. The rationale is that some popular
distributions and hosting sites still rely on older versions of Python.

Python 3.x support uses `2to3` conversion and all code should be written with
Python 2 in mind.


Style guide
-----------

* Follow PEP8.

* Always use dot notation for relative imports.

* Learn to love code checking tools like `pyflakes`. Chances are you can
  integrate it with your editor or IDE.

* Use new style exception handling as it's easier to read and far less
  ambiguous:

        try:
            # …
        except Exception as e:
            # …
