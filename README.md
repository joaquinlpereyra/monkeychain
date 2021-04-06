# Running the project

The project depends on Python 3.7 to run. I **earnestly** recommend you use 
Poetry and Pyenv to help you run the project as it will deal with your python
versions and all and any dependency the project may use. You can follow
[this guide](https://medium.com/@cjolowicz/hypermodern-python-d44485d9d769)
to install both. 

Once you have the environment set up, you can just do

```
$ poetry install # only need to do this once
$ FLASK_DEBUG=1 poetry run flask run
```

