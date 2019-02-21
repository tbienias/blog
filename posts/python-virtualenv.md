# Python - Virtual Environment on Linux #

This post is about setting up a virtual environent for Python on Linux.

## [](#why-virtual-env)Why Virtual Environment?
### [](#samba)My own Package
By the time of writing this, I was developing my own Python Package. Another project I had ongoing was relying on a specific version of this package.
To overcome this problem with system-wide packages, Python has a so-called virtual environment. The idea is to have an independent Python installation
in a separate directory. Another advantage is that you don't pollute your OS with system-wide pip packages anymore.
## [](#lets-get-started)Let's Get Started
### [](#setting-up)Setting Up
We move to the top-level directory, which shall contain the folder for our virtual environment. 
First, let us assume that we're currently in our home directory */home/jacksonmeister*.
Then we create a new virtual environment called *my_env*:

```bash
python -m venv ./my_env
```

After that, we need to source the environment so that our bash recognizes it:

```bash
source ./my_env/bin/activate
```

We can easily check whether or not it worked. We do so by looking for our Python Interpreter:

```bash
which python
```

This prints us: ```/home/jacksonmeister/my_env/bin/python```.

### [](#installing-site-packages)Installing site-packages
Now we can use *pip* for installing any site-packages we need. For example:

```bash
pip install requests
```

This will install requests into our *my_env* tree - fantastic!

### [](#leaving-virtual-environment)Leaving Virtual Environment
To get back to your regular environment simply type:

```bash
deactivate
```

And you're back to your daily business!

## [](#conclusion)Conclusion
In this post we covered how to setup a virtual environment for Python. We also showed how to activate the environment and how to install new packages into the newly created virtual environment.
