tunnel:
```
s1 -R 4242:localhost:4242
```
server:
```
sudo apt install quassel-core
```
client:
```
sudo apt install quassel-client 
```
then just follow the wizard.





how to search the logs:
```
CHANNEL="#btrfs" SEARCH="5\.15" begin cd /home/sfi/dumplog-0.0.1/; sudo ./dumplog.py -d /var/lib/quassel/quassel-storage.sqlite -u rstuniriewfseiew -n libera -c "$CHANNEL" -o /tmp/irclog; cat /tmp/irclog | grep -a -v "has joined" | grep -a -v " Quit (" | grep -a -E (string join '' '^\[.*\].*' "$SEARCH" '.*') | cat ; end
```
