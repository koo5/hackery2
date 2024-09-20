simple and safe functionality that does not require authentication, ideal for an always-listening voice agent

```
# Install required system packages
sudo apt update
sudo apt install -y python3-pip python3-venv

# Create a virtual environment
python3 -m venv ambi_env
source ambi_env/bin/activate

# Install required Python packages
pip install spacy whisper numpy sounddevice

# Download and install spaCy model
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_sm

# Set up the systemd service
sudo ln -s /home/koom/hackery2/data/ambi/ambient-agent.service /etc/systemd/system/ambient-agent.service
sudo systemctl daemon-reload
sudo systemctl enable ambient-agent.service
sudo systemctl start ambient-agent.service

# To check the status of the service
sudo systemctl status ambient-agent.service

# To view logs
sudo journalctl -u ambient-agent.service -f
```
