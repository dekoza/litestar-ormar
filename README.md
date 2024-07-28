# Litestar-Ormar

[![image](https://img.shields.io/pypi/v/litestar_ormar.svg)](https://pypi.python.org/pypi/litestar_ormar)

[![image](https://img.shields.io/travis/dekoza/litestar_ormar.svg)](https://travis-ci.com/dekoza/litestar_ormar)

[![Documentation Status](https://readthedocs.org/projects/litestar-ormar/badge/?version=latest)](https://litestar-ormar.readthedocs.io/en/latest/?version=latest)

Ormar integration for Litestar.

-   Free software: Apache Software License 2.0
-   Documentation: <https://litestar-ormar.readthedocs.io>.

## Features

-   Provides convenient Repository for Ormar adhering to Litestar\'s
    AbstractRepository.

```python
from litestar_ormar import OrmarRepository

class MyObjectRepository(OrmarRepository):
    model_type = MyObject

```

...and you're done.

## Credits

Created by Dominik Kozaczko
