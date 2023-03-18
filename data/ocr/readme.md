```
sudo apt install python3-pip
virtualenv -p /usr/bin/python3.10 venv; . venv/bin/activate.fish
python3 -m pip install --upgrade Pillow opencv-contrib-python pytesseract pygame
```

```
(venv) [03:52:39] koom@jj /home/koom/hackery2/data/ocr
> PYTHONUNBUFFERED=1 ./ocr.py /d1/screenshots/

```

