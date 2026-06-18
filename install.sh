sudo apt install pipx
pipx ensurepath
sudo pipx ensurepath --global # optional to al


sudo apt install -y jq libpq-dev
pipx install -e . --force

# Editable-install the schnabel SDK into hackery2's pipx venv so backup.py et al
# can `from schnabel import EventLog`. See src/schnabel/docs/decisions.md D-009.
pipx runpip hackery2 install -e ./src/schnabel

