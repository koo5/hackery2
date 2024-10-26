const zmq = require("zeromq");

async function dealer() {
  const sock = new zmq.Dealer();

  sock.receiveHighWaterMark = 1;
  sock.sendHighWaterMark = 1;

  sock.connect("tcp://127.0.0.1:5555");

  console.log("Dealer connected to port 5555");

  // Send a request
  const request = "Hello, Server!";
  console.log("Sending request:", request);
  await sock.send(request);

  setInterval(async () => {
    const request = "Ping, Server!";
    console.log("Sending request:", request);
    await sock.send(request);
  }, 1000);

  while (true) {
    const [reply] = await sock.receive();
    console.log("Received:", reply.toString());

    if (Math.random() < 0.1) {
      console.log("client is busy...");
      await new Promise(resolve => setTimeout(resolve, 3000));
    }

  }
}

dealer();
