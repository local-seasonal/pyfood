Contribute
===========

Development installation
------------------------

If you want to contribute to Pyfood, you will need to install the test dependencies. You can do so with

.. code-block:: console
    
    $ pip install pyfood[tests,examples]
    $ pytest tests/

Uploading the distribution archives
-----------------------------------

* Clone pyfood from the source code
* Create a Python 3.6+ virtual environment
* Install requirements

.. code-block:: console
    
    $ git clone https://github.com/MichelDeudon/pyfood.git
    $ pip install requirements.txt
    $ python -m pip install --user --upgrade setuptools wheel
    $ python setup.py sdist bdist_wheel

This command should output a lot of text and once completed should generate two files in the ``dist/`` directory:
``pyfood-x.x.x-py3-none-any.whl`` and ``pyfood-x.x.x.tar.gz``


* Register an account on `TestPyPi <https://test.pypi.org/account/register/>`_ and create an `API token <https://test.pypi.org/help/#apitoken>`_
* Install Twine to upload the distribution packages
* Upload all of the archives under dist/

.. code-block:: console
    
    $ python -m pip install --user --upgrade twine
    $ python -m twine upload -u __token__ -p pypi-API-token --repository testpypi dist/* --verbose

Once uploaded your package should be viewable on TestPyPI. You can use pip to install your package and verify that it works.

.. code-block:: console
    
    $ python -m pip install --index-url https://test.pypi.org/simple/ --no-deps pyfood

You can test that it was installed correctly by importing the package.

.. code-block:: python
    
    import pyfood

| When you are ready to upload a real package to the Python Package Index you can do much the same as in this tutorial.
| Register an account on `https://pypi.org <https://pypi.org>`_ - note that these are two separate servers and the login details from the test server are not shared with the main server.

Use twine upload dist/* to upload your package and enter your credentials for the account you registered on the real PyPI. Now that you’re uploading the package in production, you don’t need to specify --repository; the package will upload to `https://pypi.org <https://pypi.org>`_ by default.

Install your package from the real PyPI using

.. code-block:: console
    
    $ pip install pyfood


Build documentation
------------------------

.. code-block:: console
    
    $ make clean
    $ sphinx-build -b html . build
