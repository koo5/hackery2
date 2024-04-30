# motivation

## improvement over e-mail protocols

### spam and spam filtering



# binary protocol 

https://github.com/grpc/grpc-web#wire-format-mode

https://github.com/grpc/grpc-web#server-side-streaming

https://docs.rs/tonic-web/latest/tonic_web/



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
m
Steps 3.4 and 5 are deprecated because they use a service name not registered by IANA. They may be removed in a future version of the specification. Server admins are encouraged to use .well-known over any form of SRV records
 - https://spec.matrix.org/unstable/server-server-api/

GET /.well-known/matrix/server
 - Gets information about the delegated server for server-server communication between Matrix homeservers. 



## verifying server public keys

### pubkey database


### notary servers
Each homeserver publishes its public keys under /_matrix/key/v2/server. Homeservers query for keys by either getting /_matrix/key/v2/server directly or by querying an intermediate notary server using a /_matrix/key/v2/query/{serverName} API. Intermediate notary servers query the /_matrix/key/v2/server API on behalf of another server and sign the response with their own key. A server may query multiple notary servers to ensure that they all report the same public keys.





# related projects and protocols / resources / meta 
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

https://neynar.com
* https://docs.neynar.com/reference/fname-availability

## nostr
https://nostr.com/


## an android multi-client
https://yup.io/






# concepts

https://en.wikipedia.org/wiki/Public_key_infrastructure




----

Homeservers are federated: the Matrix specification defines a Sever-Server API (also known as Federation API) to describe interactions between servers. Whenever a user is in a room, their homeserver needs to have a local copy of that room.

---


The APIs are implemented using HTTPS requests between each of the servers. These HTTPS requests are strongly authenticated using public key signatures at the TLS transport layer and using public key signatures in HTTP Authorization headers at the HTTP layer.

---
There are three main kinds of communication that occur between homeservers:

Persistent Data Units (PDUs): These events are broadcast from one homeserver to any others that have joined the same room (identified by Room ID). They are persisted in long-term storage and record the history of messages and state for a room.

Like email, it is the responsibility of the originating server of a PDU to deliver that event to its recipient servers. However PDUs are signed using the originating server’s private key so that it is possible to deliver them through third-party servers.

Ephemeral Data Units (EDUs): These events are pushed between pairs of homeservers. They are not persisted and are not part of the history of a room, nor does the receiving homeserver have to reply to them.

Queries: These are single request/response interactions between a given pair of servers, initiated by one side sending an HTTPS GET request to obtain some information, and responded by the other. They are not persisted and contain no long-term significant history. They simply request a snapshot state at the instant the query is made.

EDUs and PDUs are further wrapped in an envelope called a Transaction, which is transferred from the origin to the destination homeserver using an HTTPS PUT request.
---



Note

Events are not limited to the types defined in this specification. New or custom event types can be created on a whim using the Java package naming convention. For example, a com.example.game.score event can be sent by clients and other clients would receive it through Matrix, assuming the client has access to the com.example namespace.

----



The mandatory baseline for server-server communication in Matrix is exchanging JSON objects over HTTPS APIs. More efficient transports may be specified in future as optional extensions.

---

If the token refresh fails and the error response included a soft_logout: true property, then the client can treat it as a soft logout and attempt to obtain a new access token by re-logging in. If the error response does not include a soft_logout: true property, the client should consider the user as being logged out.

Handling of clients that do not support refresh tokens is up to the homeserver; clients indicate their support for refresh tokens by including a refresh_token: true property in the request body of the /login and /register endpoints. For example, homeservers may allow the use of non-expiring access tokens, or may expire access tokens anyways and rely on soft logout behaviour on clients that don’t support refreshing.
---




"everything is a room"? One-to-one conversation is no different than multi-user?
this concept may or may not hold depending on the cryptographic algorithms used, and the concept of a "room" might eventually come to mean just a nameless channel with no intrinsic properties.
ie.: it may not always even store messages on behalf of its users.
compare with the concept of a conversation (a client feature)


https://spec.matrix.org/latest/server-server-api/
TLS

Server-server communication must take place over HTTPS.

The destination server must provide a TLS certificate signed by a known Certificate Authority.

Requesting servers are ultimately responsible for determining the trusted Certificate Authorities, however are strongly encouraged to rely on the operating system’s judgement. Servers can offer administrators a means to override the trusted authorities list. Servers can additionally skip the certificate validation for a given whitelist of domains or netmasks for the purposes of testing or in networks where verification is done elsewhere, such as with .onion addresses.

Servers should respect SNI when making requests where possible: a SNI should be sent for the certificate which is expected, unless that certificate is expected to be an IP address in which case SNI is not supported and should not be sent.

Servers are encouraged to make use of the Certificate Transparency project.


---
ensure that they all report the same public keys.

This approach is borrowed from the Perspectives Project, but modified to include the NACL keys and to use JSON instead of XML. It has the advantage of avoiding a single trust-root since each server is free to pick which notary servers they trust and can corroborate the keys returned by a given notary server by querying other servers.

---
## protobuf / grpc

https://github.com/grpc/grpc-web#wire-format-mode



https://blog.postman.com/postman-now-supports-grpc/

https://www.miroslavholec.cz/blog/grpc-nastroje

https://www.miroslavholec.cz/blog/grpc-navrh-sluzeb

## encryption
https://signal.org/docs/specifications/doubleratchet/
These properties gives some protection to earlier or later encrypted messages in case of a compromise of a party's keys.










###
```
casove omezit challenge string



1. moznost:
prihlasovaci tanecek probehne pri kazdym otevreni WS spojeni
2. moznost: 
  pri prihlaseni se vygeneruje random token, kterym se client authenticuje pri nasledujicich otevrenich WS
3. moznost:
  jwt




moduly prihlasovani / overovani uzivatelu:
  jeden server druhymu potvrzuje existenci a authenticitu uzivatele, to je asi oauth flow


odstavec k notary serverum jako dalsi alternative DKIM



porovnat overeni protejsiho serveru(2x) s matrix spec



    TODO - sepsat, jak se přesně navazuje spojení, jestli je tam nějaký endpoint pro WebTransport apod.

 "command": "admin_login_request",
 
 
 Spojení server-server


```








