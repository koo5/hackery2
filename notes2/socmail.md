# client


fat client displays content, handles user interaction
possible kinds of clients:
  voice assistant
  desktop app
  web app (part of the node)
  
although the node serves a web version of the fat client, such fat client is not limited to connecting to the serving node. The node provides an api to the fat client. The fat client can maintain connections to multiple nodes, and it can also initiate http requests (or other kinds of connections?) to other kinds of services.


# server

Socmail network is composed of servers. Each server is a self-sovreign identity that can communicate with other servers. Servers are connected in a network, forming a graph. Each server has a unique identifier, and a public key. Servers can send messages to each other, and messages are signed with the sender's private key. Servers can also send messages to clients, and messages are signed with the server's private key. Servers can also send messages to other servers on behalf of clients, and messages are signed with the server's private key. 


## identity and security
Much of today's internet relies on the system of domain names and certificates. This system is centralized, and it is vulnerable to attacks. The Yellow Network is decentralized, and it does not rely on domain names or certificates. Instead, each server has a unique identifier, and a public key. 

### messages
Servers can send messages to each other, and messages are signed with the sender's private key. Servers can also send messages to clients, and messages are signed with the server's private key. Servers can also send messages to other servers on behalf of clients, and messages are signed with the server's private key.


### inter-server communication
nodes only send opaque json blobs among themselves, as directed by user interaction on the originating node


## server domains and discovery

## homeserver

A domain name is an unchangeable identifier of the abstract concept of a "homeserver". However, DNS names can be spoofed and HTTPS certificate trust roots can be subverted, therefore, a successful initiation of a connection to a homeserver is not considered a strong-enough proof of authenticity. A system of private/public key pairs is thus employed.



## delegated server:

A single IP address can host multiple web applications serving different DNS domains. This may be implemented and administered by a logic internal to the server software.

Steps 3.4 and 5 are deprecated because they use a service name not registered by IANA. They may be removed in a future version of the specification. Server admins are encouraged to use .well-known over any form of SRV records
 - https://spec.matrix.org/unstable/server-server-api/

GET /.well-known/matrix/server
 - Gets information about the delegated server for server-server communication between Matrix homeservers. 



## verifying server public keys

### pubkey database


### notary servers
Each homeserver publishes its public keys under /_matrix/key/v2/server. Homeservers query for keys by either getting /_matrix/key/v2/server directly or by querying an intermediate notary server using a /_matrix/key/v2/query/{serverName} API. Intermediate notary servers query the /_matrix/key/v2/server API on behalf of another server and sign the response with their own key. A server may query multiple notary servers to ensure that they all report the same public keys.





# related projects / resources / meta
https://nate.mecca1.net/posts/2024-01-30_microblogging-protocols/


## matrix
https://github.com/adrianrudnik/matrix-wellknown-server

https://spec.matrix.org/latest/


## bsky
https://atproto.com/

https://bsky.app/feeds

https://blog.paulbohm.com/p/blue-sky-farcaster-substack-notes


## farcaster
Any Ethereum address can register a Farcaster account by making an onchain transaction.

https://docs.farcaster.xyz/reference/frames/spec

https://blockprotocol.org/docs/blocks/environments#your-own-application

https://github.com/farcasterxyz/protocol/blob/main/docs/OVERVIEW.md

https://www.supercast.xyz/


## nostr
https://nostr.com/


## ?
https://yup.io/

https://neynar.com

