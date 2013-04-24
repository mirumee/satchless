:mod:`satchless.process` --- multi-step processes
=================================================

.. module:: satchless.process

The purpose of this module is to aid with creation of multi-step processes such as online store checkout. We solve this by providing a step class and a process class that are typically bound to data that is persisted between the steps. Each time a single step is completed you can ask the manager which step needs to be completed next until the whole process is considered complete.

We do not define what a step is. It could be a Django view or a call to an external API. It can be anything as long as it can determine its own state (usually passed to its constructor by the process manager) and decide whether it's valid or not.


Available Types
---------------

.. exception:: InvalidData

   An exception raised when a step is invalid.

.. class:: Step
   :noindex:

   A single step in a multi-step process.

.. class:: ProcessManager
   :noindex:

   A multi-step process manager.


:class:`Step` Objects
---------------------

.. class:: Step

   A :class:`Step` instance is a single step in a process. For example a single checkout step.

Instance methods:

.. method:: __str__()

   Returns the step ID. The same step must always return the same ID and the ID has to be unique within the process.

   Default implementation will raise an :exc:`NotImplementedError` exception.

.. method:: validate()

   Validates the step and raises :exc:`InvalidData` if the step requires further attention.

   Default implementation will raise an :exc:`NotImplementedError` exception.

Example use:

   >>> from satchless.process import InvalidData, Step
   >>> class LicenseAcceptance(Step):
   ...     def __init__(self, data): self.data = data
   ...     def __str__(self): return 'license'
   ...     def validate(self):
   ...         if not self.data.get('license_accepted'):
   ...             raise InvalidData('Nice try')
   ...
   >>> data = {}
   >>> step = LicenseAcceptance(data)
   >>> str(step)
   'license'
   >>> step.validate()
   Traceback (most recent call last):
     File "<stdin>", line 1, in <module>
     File "<stdin>", line 6, in validate
   satchless.process.InvalidData: Nice try
   >>> data['license_accepted'] = True
   >>> step.validate()

:class:`ProcessManager` Objects
-------------------------------

.. class:: ProcessManager

   A :class:`ProcessManager` instance represents a single process. For example the checkout process in a typical online store.

Instance methods:

.. method:: ProcessManager.__iter__()

   Returns an iterator that yields :class:`Step` objects that define the process.

   Default implementation will raise an :exc:`NotImplementedError` exception.

.. method:: ProcessManager.__getitem__(step_id)

   Returns the :class:`Step` object whose :meth:`Step.__str__` method returns ``step_id``.

   If no such step is found, :exc:`KeyError` will be raised.

.. method:: ProcessManager.is_complete()

   Returns `True` if all the steps of the process are valid. `False` otherwise.

.. method:: ProcessManager.get_next_step()

   Returns the first step that does not validate.

   If all steps are valid, ``None`` is returned.

.. method:: ProcessManager.get_errors()

   Returns a :class:`dict` whose keys are IDs of steps that did not validate and the values are the exceptions raised by the steps.

Example use::

   >>> from satchless.process import InvalidData, ProcessManager, Step
   >>> class LicenseAcceptance(Step):
   ...     def __init__(self, data): self.data = data
   ...     def __str__(self): return 'license'
   ...     def __repr__(self): return 'LicenseAcceptance(%r)' % (self.data, )
   ...     def validate(self):
   ...         if not self.data.get('license_accepted'):
   ...             raise InvalidData('Nice try')
   ...
   >>> class SingleStepProcessManager(ProcessManager):
   ...     def __init__(self, data): self.data = data
   ...     def __iter__(self):
   ...         yield LicenseAcceptance(self.data)
   ...
   >>> data = {}
   >>> process = SingleStepProcessManager(data)
   >>> list(process)
   [LicenseAcceptance({})]
   >>> process['license']
   LicenseAcceptance({})
   >>> process.is_complete()
   False
   >>> process.get_next_step()
   LicenseAcceptance({})
   >>> process.get_errors()
   {'license': InvalidData('Nice try',)}
   >>> data['license_accepted'] = True
   >>> process.is_complete()
   True
   >>> process.get_next_step()
   >>> process.get_errors()
   {}
