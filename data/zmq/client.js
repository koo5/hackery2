const zmq = require("zeromq");

let q = [];
let replyCount = 0;

async function dealer() {
  const sock = new zmq.Dealer();

  sock.receiveHighWaterMark = 100;
  sock.sendHighWaterMark = 100;

 sock.connect("tcp://127.0.0.1:5555");
 //sock.connect("ipc:///tmp/test.ipc");

 console.log("Dealer connected to port 5555");

  // Send a request
  const request = "Hello, Server!";
  console.log("Sending request:", request);
  q.push(request);

  setInterval(async () => {
    const request = "Ping, Server!";
    console.log("Sending request:", request);
    q.push(request);
  }, 1000);

  setInterval(async () => {
    if (q.length > 0) {
      const request = q.shift();
      try {
       await sock.send(request);
      }
      catch (err) {
        console.error(err);
      }
    }
  }, 0);

  while (true) {
    const [reply] = await sock.receive();
    replyCount++;
    if (replyCount % 1000 === 0)
     console.log("Reply count:", replyCount);
    //console.log("Received.");//, reply.toString());

    /*if (Math.random() < 0.1) {
      console.log("client is busy...");
      await new Promise(resolve => setTimeout(resolve, 3000));
    }*/
  }
}

dealer();



/*
 node client.js
Dealer connected to port 5555
Sending request: Hello, Server!
Sending request: Ping, Server!
Sending request: Ping, Server!
/home/koom/hackery2/data/zmq/client.js:29
      await sock.send(request);
                 ^

Error: Socket is busy writing; only one send operation may be in progress at any time
    at Timeout._onTimeout (/home/koom/hackery2/data/zmq/client.js:29:18)
    at listOnTimeout (node:internal/timers:569:17)
    at process.processTimers (node:internal/timers:512:7) {
  errno: 16,
  code: 'EBUSY'
}

Node.js v18.20.4

 */