simple and safe functionality that does not require authentication, ideal for an always-listening voice agent

```
sudo ln -s /home/koom/hackery2/data/ambi/ambient-agent.service /etc/systemd/system/ambient-agent.service
sudo systemctl daemon-reload                                                                  
sudo systemctl enable ambient-agent.service                                                   
sudo systemctl start ambient-agent.service                                                    
```
