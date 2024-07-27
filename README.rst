==============
Litestar-Ormar
==============


.. image:: https://img.shields.io/pypi/v/litestar_ormar.svg
        :target: https://pypi.python.org/pypi/litestar_ormar

.. image:: https://img.shields.io/travis/dekoza/litestar_ormar.svg
        :target: https://travis-ci.com/dekoza/litestar_ormar

.. image:: https://readthedocs.org/projects/litestar-ormar/badge/?version=latest
        :target: https://litestar-ormar.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status




Ormar integration for Litestar.


* Free software: Apache Software License 2.0
* Documentation: https://litestar-ormar.readthedocs.io.


Features
--------

* Provides convenient Repository for Ormar adhering to Litestar's AbstractRepository.

```python
from litestar_ormar import OrmarRepository

class MyObjectRepository(OrmarRepository):
    model_type = MyObject
```

...and you're done.


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
