import requests
import time
from secrets import secret

server = secret('server')

x1 = 0
x2 = 0
x3 = 0

for i in range(3000) :
  response = requests.post(f'http://{server}:3000/api/live/push/custom_stream_id', data='sma,sma=cpu5,host=smar usage_softirq='+str(x1)+',usage_guest='+str(x2)+',usage_guest_nice='+str(x3), headers={'Authorization':'Bearer '+ secret('token')})
  x1+=1
  x2+=2
  x3+=3
  print(response)
  time.sleep(0.4)
