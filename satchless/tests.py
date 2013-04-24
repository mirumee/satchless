from unittest import TestSuite, TestLoader

TEST_MODULES = [
    'satchless.cart.tests',
    'satchless.item.tests',
    'satchless.process.tests']

suite = TestSuite()
loader = TestLoader()
for module in TEST_MODULES:
    suite.addTests(loader.loadTestsFromName(module))
