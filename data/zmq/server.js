const zmq = require("zeromq");

let clientId = null;
let clientIdHex = null;

async function handleMessages(sock) {
  while (true) {
   let msg;
    [clientId, msg] = await sock.receive();
    clientIdHex = clientId.toString('hex');
    console.log("Received message:", msg.toString(), "from client", clientIdHex);

    let nice_timestamp = new Date().toISOString();
    const reply = `Reply to ${clientIdHex}: ${nice_timestamp}`;
    console.log("Sending reply:", reply);
    await sock.send([clientId, reply]);
  }
}

async function router() {
  const sock = new zmq.Router();

  sock.receiveHighWaterMark = 1;
  sock.sendHighWaterMark = 1;

  await sock.bind("tcp://127.0.0.1:5555");


  console.log("Router bound to port 5555");

  setInterval(async () => {
    if (clientIdHex) {
     let nice_timestamp = new Date().toISOString();
     const event = `Event to ${clientIdHex}: ${nice_timestamp}`;
     console.log("Sending event:", event);
     await sock.send([clientId, event]);
    }
  }, 0);

  handleMessages(sock);
}

router();