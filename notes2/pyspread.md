### seems to work just as well with python3 so far.
```
gcl https://gitlab.com/pyspread/pyspread.git
cd pyspread/
virtualenv -p python3.8 venv
pip3 install --user -r requirements.txt
./bin/pyspread
```


### trying with python2: 
```
virtualenv -p python2 venv2
. venv2/bin/activate.fish 
pip install --user -r requirements.txt 
```
pip's telling me that PyQt5 isn't available (for python2 i guess).
luckily:
```
sudo apt install python-pyqt5
```
works on my Ubuntu 18.04.5 LTS.

So now i'm commenting out PyQt5 from requirements.txt and trying again:
```
pip install --user -r requirements.txt 
```
bingo!


## observations
the UI could use some improvement: To make one cell a sum of a few other cells, follow these steps exactly:
* click on a cell
* click above on "Entry line"
* press insert
* click-drag-release a selection of cells
* click above on "Entry line"
* press return.

idk, maybe there are some shortcuts.

you get a nice comprehensive help after pressing F1..

	


