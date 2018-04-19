import requests
import json

debug_print = False##True

def main():
	url = "http://localhost:18332/"
	headers = {'content-type': 'application/json'}

	payload = {
       		"method": "getblockcount",
       		"jsonrpc": "1.0",
	        "id": 0,
	}
	
	response = requests.post(url, data=json.dumps(payload), 
				headers=headers, auth=('a123','a123')).json()
	
	block = response['result']
	#block = 1288010

	while True:
		if block % 10000 == 0:
			print ("block " + str(block))
		payload = {
	       		"method": "omni_listblocktransactions",
			"params": [block],
        		"jsonrpc": "1.0",
		        "id": 0,
		}
	
		block -= 1

		response = requests.post(url, data=json.dumps(payload), 
					headers=headers, auth=('a123','a123')).json()

		if debug_print:
			print(response)

		if response["error"] == {'code': -8, 'message': 'Block height is out of range'}:
			break
		
		for tx_id in response["result"]:
		
			payload = {
				"method": "omni_gettransaction",
				"params": [tx_id],
				"jsonrpc": "1.0",
				"id": 0}
	
			response = requests.post(url, data=json.dumps(payload), 
					headers=headers, auth=('a123','a123')).json()

			if debug_print:
				print(response)
			result = response['result']

			if 'referenceaddress' in result:
#				if result['referenceaddress'] == '2NDGciY4XU6nA62jHVdZnqfUjXxUY6cGkg2':
				if result['referenceaddress'] == '2NEyLPf1BXaZkJoVyy9WqSpWetufK2idYre':
					print (result)
					exit()


			payload = {
				"method": "omni_getsto",
				"params": [tx_id, "*"],
				"jsonrpc": "1.0",
				"id": 0}
	
			response = requests.post(url, data=json.dumps(payload), 
					headers=headers, auth=('a123','a123')).json()

			if debug_print:
				print(response)
			result = response['result']

			if 'referenceaddress' in result:
				if result['referenceaddress'] == '2NEyLPf1BXaZkJoVyy9WqSpWetufK2idYre':
					print (result, "!!!")
					exit()


			#print(result)
			if 'recipients' in result:
				print(result)
				for j in result['recipients']:
					if j['address'] == '2NEyLPf1BXaZkJoVyy9WqSpWetufK2idYre':
						print (result, "!!!")
						exit()

	print("done")

if __name__ == "__main__":
    main()
