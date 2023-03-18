```
sudo apt install python3-pip
virtualenv -p /usr/bin/python3.10 venv; . venv/bin/activate.fish
python3 -m pip install --upgrade Pillow opencv-contrib-python pytesseract
```

```
(venv) [02:39:11] koom@jj /home/koom/hackery2/data/ocr
> ./ocr.py /d1/screenshots/ 0
```

```
[02:39:34] koom@jj /home/koom/hackery2/data/ocr
> tail -f data/output.txt
```


