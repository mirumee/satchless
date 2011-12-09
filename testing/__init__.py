import django_nose

class NoseTestSuiteRunner(django_nose.NoseTestSuiteRunner):
    def run_tests(self, test_labels, extra_tests=None):
        self.build_suite(test_labels, extra_tests)
        return super(NoseTestSuiteRunner, self).run_tests(
            test_labels=test_labels, extra_tests=extra_tests)