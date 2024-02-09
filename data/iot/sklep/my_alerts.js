


function Test(check, note, max_silence=100)
{
	this.check = check
	this.note = note
	this.max_silence = max_silence
	this.incoming_messages = []
	this.last_beat = 0
}



tests = {
	"heartbeat_check_loop": Test('true', note=`Publish this topic to test clients' deadman switch alerting. Think of heartbeat_check_loop as a sensor with its own heartbeat, produced by the continuous lack of beats on this topic. When this topic is published, the heartbeat_check_loop will stop producing the "has no heartbeat" alerts, and clients should notice that. Additionally, publish a false to see that checks work.`),
	
	"sklep/adc1/value": Test('value < 30')
}



async function check_loop()
{
	while (true)
	{	
		now = time.time()
		
		//next_wakeup = 99999
		
		for (topic, test in tests)
		{
			while (message = test.incoming_messages.pop())
			{
				check_result = eval_check(ctest.check, message.value)
				if (!check_result)
					alert('${topic} is ${message.value}, should be ${test.check}', topic, value)
			}
			
			const silence = now - test.last_beat
			if (silence > test.max_silence)
			{
				alert('${topic} last beat was at ${test.last_beat}, ${silence} seconds ago')')
			}

			//next_wakeup = Math.min(next_wakeup, now - test.last_beat + max_silence)
			
		}
		await sleep(1)

		// wakeups.get(timeout=next_wakeup)
	}
}



function eval_check(check, value)
{
	result = eval(check)
	if (typeof check_result !== 'boolean') alert("bad check: eval(${check}) is not a boolean");
	return result				
}

	
	
function alert(msg, sensor, value)
{
	r = requests.post("http://localhost:9093/api/v1/alerts", json={
		// and this is how you can tell the system is rotten:
		"labels": {
			"sensor": sensor
		},
		"annotations": {
			"value": value
		}
	})
}



function incoming_message(topic, value)
{
	test = tests[topic]
	if (test)
	{
		test.incoming_messages.push({topic, value})
		test.last_beat = time.time()
	}
}



for (mqtt_config in mqtt_configs)
{
	mqtt = new MqttClient(mqtt_config)
	mqtt.on_message = incoming_message
	mqtt.subscribe('#')
}



await check_loop()



/*
test alert once a day
*/
function scheduleFunction() {
    const now = new Date();
    const millisTill9 = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 21, 0, 0, 0) - now;
    if (millisTill9 < 0) {
        millisTill9 += 86400000; // it's after 21:00, schedule it for the next day
    }
    setTimeout(function() {
        // Your function to execute
        console.log("It's 21:00!");
        alert("It's 21:00!");
        // Reschedule the function for the next day
        scheduleFunction();
    }, millisTill9);
}

// Start the function initially
scheduleFunction();
