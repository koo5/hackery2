
# dependency management
## Python Package Management is a Nightmare!
https://medium.com/@damngoodtech/the-great-python-package-management-war-49f25df33d26
## setup.py, setup.cfg, requirements.txt, Pipfile, pyproject.toml – oh my!
https://venthur.de/2021-06-26-python-packaging.html
## Managing Python Dependencies – Everything You Need To Know 
https://www.activestate.com/resources/quick-reads/python-dependencies-everything-you-need-to-know/

## my plan (?)
### 1) use apt or `pip install --user` to install exclusively python package management tools
#### pipreqs
```pip install pipreqs```
| Create a requirements.in file and list just the direct dependencies of your app. 
```pipreqs --savepath requirements.in```


#### https://pypa.github.io/pipx/
| pipx — Install and Run Python Applications in Isolated Environments
```
python3 -m pip install --user pipx
pipx ensurepath
register-python-argcomplete --shell fish pipx >~/.config/fish/completions/pipx.fish

```

### venv as usual
```
virtualenv -p /usr/bin/python3.10 venv
. venv/bin/activate.fish
```
where python3.10 obviously magically corresponds to the python version inside your dockers or whatever..

#### or maybe
venv in a centralized location in you home, as the various wrapper libraries make you do. Doesn't seem to matter that much. But at least they shouldn't ask you for a name for the venv. 

If you're copying your sources directory(repo) around, you have to make an embedded venv relocatable anyway..

Anyway, here's a fish script to source in your `.config/fish/config.fish` for some semi-reasonable automatic local venv activation: `hackery2/data/setup/data/fish/functions/auto_venv.fish`



#### pip-tools must go inside the venv
```
pip install pip-tools
```

| pip-compile command lets you compile a requirements.txt file from your dependencies, specified in either pyproject.toml, setup.cfg, setup.py, or requirements.in.
pip-tools seems to require a virtualenv and to be installed in that virtualenv .. will see.. but i guess it's reasonable to always maintain a virtualenv even for pycharm etc..
```
pip-compile --resolver=backtracking
```

