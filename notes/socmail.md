# motivation

## improvement over e-mail protocols

### spam and spam filtering
### migration


# binary protocol 

https://ably.com/blog/websocket-authentication


## https://datatracker.ietf.org/doc/html/draft-ietf-webtrans-overview-07
>The WebTransport Protocol Framework enables clients constrained by the Web security model to communicate with a remote server using a secure multiplexed transport. It consists of a set of individual protocols that are safe to expose to untrusted applications, combined with an abstract model that allows them to be used interchangeably.
...
>WebTransport avoids all of those issues by letting applications create a single transport object that can contain multiple streams multiplexed together in a single context (similar to SCTP, HTTP/2, QUIC and others), and can be also used to send unreliable datagrams (similar to UDP).

>
WebTransport session establishment is an asynchronous process. A session is considered ready from the client's perspective when the server has confirmed that it is willing to accept the session with the provided origin and URI. WebTransport protocols MAY allow clients to send data before the session is ready; however, they MUST NOT use mechanisms that are unsafe against replay attacks without an explicit indication from the client.


>A datagram is a sequence of bytes that is limited in size (generally to the path MTU) and is not expected to be transmitted reliably. The general goal for WebTransport datagrams is to be similar in behavior to UDP while being subject to common requirements expressed in Section 2.

>Streams SHOULD be sufficiently lightweight that they can be used as messages.

>the creation of new streams is flow controlled as well: an endpoint may only open a limited number of streams until the peer explicitly allows creating more streams. From the perspective of the client, this is presented as a size-bounded queue of incoming streams.

>For example, the client must not be able to distinguish between a network address that is unreachable and one that is reachable but is not a WebTransport server.

>WebTransport does not support any traditional means of HTTP-based authentication. It is not necessarily based on HTTP, and hence does not support HTTP cookies or HTTP authentication.

- https://datatracker.ietf.org/doc/html/draft-ietf-webtrans-overview-07

https://www.rfc-editor.org/rfc/rfc9297



>The webtransport HTTP Upgrade Token uses the Capsule Protocol as defined in [HTTP-DATAGRAM].


>WebTransport CONNECT requests and responses MAY contain the Priority header field (Section 5 of [RFC9218]); clients MAY reprioritize by sending PRIORITY_UPDATE frames (Section 7 of [RFC9218]).

>Session IDs are used to demultiplex streams and datagrams belonging to different WebTransport sessions. On the wire, session IDs are encoded using the QUIC variable length integer scheme described in [RFC9000].The client MAY optimistically open unidirectional and bidirectional streams, as well as send datagrams, for a session that it has sent the CONNECT request for, even if it has not yet received the server's response to the request. On the server side, opening streams and sending datagrams is possible as soon as the CONNECT request has been received.

> A stream ID is a 62-bit integer

>A server can also grant clients a session ticket that can be used to reconnect to a server without going through a full handshake. This reduces the number of client-server connects and allows fast, secure reconnections.

>UIC itself does not depend on any state being retained when resuming a connection unless 0-RTT is also used; see Section 7.4.1 of [QUIC-TRANSPORT] and Section 4.6.1. Application protocols could depend on state that is retained between resumed connections.Clients can store any state required for resumption along with the session ticket. Servers can use the session ticket to help carry state.Session resumption allows servers to link activity on the original connection with the resumed connection, which might be a privacy issue for clients. Clients can choose not to enable resumption to avoid creating this correlation. Clients SHOULD NOT reuse tickets as that allows entities other than the server to correlate connections;


>[RFC8441] defines an extended CONNECT method in Section 4, enabled by the SETTINGS_ENABLE_CONNECT_PROTOCOL setting. That setting is defined for HTTP/3 by [RFC9220]. A server supporting WebTransport over HTTP/3 MUST send both the SETTINGS_WEBTRANSPORT_MAX_SESSIONS setting with a value greater than "0" and the SETTINGS_ENABLE_CONNECT_PROTOCOL setting with a value of "1". To use WebTransport over HTTP/3, clients MUST send the SETTINGS_ENABLE_CONNECT_PROTOCOL setting with a value of "1".


>Quick UDP Internet Connections (QUIC) is a general-purpose transport layer protocol designed to replace the Transmission Control Protocol (TCP) through its flexibility, built-in security, fewer performance issues, and faster adoption rate. Originally developed by Google, QUIC uses User Datagram Protocol (UDP) as the low‑level transport mechanism for moving packets between client and server. Notably, QUIC also incorporates Transport Layer Security (TLS) as an integral component, not as an additional layer like HTTP/1.1 and HTTP/2.

>HTTP/3, based on QUIC, is the third major version of the Hypertext Transfer Protocol (HTTP) and was adopted as an IETF standard in 2022. QUIC+HTTP/3 were created to solve inherent limitations with TCP that constrain performance and user experience.




https://github.com/grpc/grpc-web#wire-format-mode

https://github.com/grpc/grpc-web#server-side-streaming

https://docs.rs/tonic-web/latest/tonic_web/



> Například implicitní TCP port pro HTTPS je 443, aby se odlišil od portu 80 pro obyčejné HTTP. Nicméně v roce 1997 Internet Engineering Task Force doporučilo, aby aplikační protokoly vždy zahajovaly činnost bez zabezpečení a místo samostatných portů nabídly způsob pro přechod na TLS. S tím se jednoduché balení aplikačních dat do TLS, jaké používá Stunnel, nedokáže vypořádat. 
 
## webtransport
https://github.com/haproxy/haproxy/issues/2256
https://github.com/w3c/webtransport/issues/525



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


Modules
Modules are parts of the Client-Server API which are not universal to all endpoints. Modules are strictly defined within this specification and should not be mistaken for experimental extensions or optional features. A compliant server implementation MUST support all modules and supporting specification (unless the implementation only targets clients of certain profiles, in which case only the required modules for those feature profiles MUST be implemented). A compliant client implementation MUST support all the required modules and supporting specification for the Feature Profile it targets.

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
There is no implicit ordering or hierarchy to room versions, and their principles are immutable once placed in the specification. Although there is a recommended set of versions, some rooms may benefit from features introduced by other versions. Rooms move between different versions by "upgrading" to the desired version. Due to versions not being ordered or hierarchical, this means a room can "upgrade" from version 2 to version 1, if it is so desired.


---

All data exchanged over Matrix is expressed as an “event”. Typically each client action (e.g. sending a message) correlates with exactly one event. Each event has a type which is used to differentiate different kinds of data. type values MUST be uniquely globally namespaced following Java’s package naming conventions, e.g. com.example.myapp.event.

---




For example, for client A to send a message to client B, client A performs an HTTP PUT of the required JSON event on its homeserver (HS) using the client-server API. A’s HS appends this event to its copy of the room’s event graph, signing the message in the context of the graph for integrity. A’s HS then replicates the message to B’s HS by performing an HTTP PUT using the server-server API. B’s HS authenticates the request, validates the event’s signature, authorises the event’s contents and then adds it to its copy of the room’s event graph. Client B then receives the message from his homeserver via a long-lived GET request.


---




The purpose of the transaction ID is to allow the homeserver to distinguish a new request from a retransmission of a previous request so that it can make the request idempotent.

The transaction ID should only be used for this purpose.

From the client perspective, after the request has finished, the {txnId} value should be changed by for the next request (how is not specified; a monotonically increasing integer is recommended).


---

>It is realistic to expect that some clients will be written to be run within a web browser or similar environment. In these cases, the homeserver should respond to pre-flight requests and supply Cross-Origin Resource Sharing (CORS) headers on all requests.

>Servers MUST expect that clients will approach them with OPTIONS requests, allowing clients to discover the CORS headers. All endpoints in this specification support the OPTIONS method, however the server MUST NOT perform any logic defined for the endpoints when approached with an OPTIONS request.

----

On the other hand, Matrix has often got stuck in focusing on solving the Hard Problems of decentralisation, decentralised end-to-end encryption, and the logistical complexities of supporting a massive heterogeneous public communication network and its surrounding heterogeneous ecosystem. It’s fair to say that in the early days our focus was on making something that worked at all - and then later, we shifted to focusing on something that worked and scaled correctly… but we hadn’t managed to focus on ensuring that Matrix provides the building blocks necessary to create blazingly fast, hyper-efficient communication apps which has potential to outperform the centralised mainstream messaging services…

---




---



## protobuf / grpc

https://github.com/grpc/grpc-web#wire-format-mode



https://blog.postman.com/postman-now-supports-grpc/

https://www.miroslavholec.cz/blog/grpc-nastroje

https://www.miroslavholec.cz/blog/grpc-navrh-sluzeb

## encryption
https://signal.org/docs/specifications/doubleratchet/
These properties gives some protection to earlier or later encrypted messages in case of a compromise of a party's keys.

## oauth
https://matrix.org/blog/2023/09/better-auth/



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

=======
## encryption inside TLS
https://medium.com/@chathurabimalka/the-importance-of-encrypting-the-entire-payload-even-over-an-https-tls-connection-6999e3d27a53

```
Profile photo for Assistant
Assistant
Bot
Nov 30

Using HTTPS for a REST API provides a good baseline level of security by encrypting the data transmitted between the client and the server. However, depending on the sensitivity of the data being transmitted and the potential threats your system may face, you may want to consider additional encryption measures.

One option is to implement message-level encryption within the REST API, which would involve encrypting the payload of the API requests and responses using techniques such as symmetric or asymmetric encryption. This can provide an extra layer of protection for the data being transmitted.

<<<<<<< Updated upstream
Ultimately, the decision to implement additional encryption on top of HTTPS for a REST API should be based on a thorough assessment of your security requirements and potential threats. Consulting with a security expert or team may be beneficial in making this determination.
```


```
Related
Do I have to use SSL with jwt? Is jwt enough?
=======


user_register_user
POST /_matrix/client/v3/delete_devices 


SSL and JWT solve very different problems...

A JWT token brings authentication / authorization to its bearer. It is not encrypted. To prevent someone stealing the token, SSL is your best option.

For instance, during login the user sends a user/password to the server. The server checks the password, and sends a token to the user.
This token states: "this is user <user_id> and his role is <role1, role2>". It is signed by the server, so the server can check later that its content is not altered.

For the next requests, the client will only send his token, not his username or password. The server will check the token's validity, and can assume that the information it contains is valid because it signed the token itself!
```

Now if someone can get hold of this token, then they can impersonate the user.

SSL helps by:

    avoiding the client sending a user/password in clear on the network
    making it impossible to steal the token
```

```


HTTP Public Key Pinning (HPKP) is an obsolete Internet security mechanism delivered via an HTTP header which allows HTTPS websites to resist impersonation by attackers using misissued or otherwise fraudulent digital certificates.[1] A server uses it to deliver to the client (e.g. web browser) a set of hashes of public keys that must appear in the certificate chain of future connections to the same domain name.

For example, attackers might compromise a certificate authority, and then mis-issue certificates for a web origin. To combat this risk, the HTTPS web server serves a list of “pinned” public key hashes valid for a given time; on subsequent connections, during that validity time, clients expect the server to use one or more of those public keys in its certificate chain. If it does not, an error message is shown, which cannot be (easily) bypassed by the user.

The technique does not pin certificates, but public key hashes. This means that one can use the key pair to get a certificate from any certificate authority, when one has access to the private key. Also the user can pin public keys of root or intermediate certificates (created by certificate authorities), restricting site to certificates issued by the said certificate authority.

Due to HPKP mechanism complexity and possibility of accidental misuse (potentially causing a lockout condition by system administrators), in 2017 browsers deprecated HPKP and in 2018 removed its support in favor of Certificate Transparency.[2][3]
```








https://www.prisma.io/docs/orm/prisma-client/queries/crud
https://www.prisma.io/docs/orm/prisma-client/queries/pagination
https://semantic-ui.com/modules/dropdown.html



https://solid.github.io/chat/
https://forum.solidproject.org/t/exploring-a-hybrid-protocol-stack-solid-at-protocol-activitypub/8252/7


https://github.com/BelledonneCommunications/lime




MLS
When a client is part of a Group, it is called a Member. A group in MLS is defined as the set of clients that have knowledge of the shared group secret established in the group key establishment phase. Note that until a client has been added to the group and contributed to the group secret in a manner verifiable by other members of the group, other members cannot assume that the client is a member of the group; for instance, the newly added member might not have received the Welcome message or been unable to decrypt it for some reason.
---
Upon joining the system, each client stores its initial cryptographic key material with the Delivery Service. This key material, called a KeyPackage, advertises the functional abilities of the client such as supported protocol versions, supported extensions, and the following cryptographic information:
* A credential from the Authentication Service attesting to the binding between the identity and the client's signature key.
* The client's asymmetric encryption public key.
---
RECOMMENDATION: Use credentials uncorrellated with specific users to help prevent DoS attacks, in a privacy preserving manner. Note that the privacy of these mechanisms has to be adjusted in accordance with the privacy expected from secure transport links. (See more discussion in the next section.)
---
Update messages SHOULD be sent at regular intervals of time as long as the group is active, and members that don't update SHOULD eventually be removed from the group. It's left to the application to determine an appropriate amount of time between Updates. Since the purpose of sending an Update is to proactively constrain a compromise window, the right frequency is usually on the order of hours or days, not milliseconds. For example, an application might send an Update each time a member sends an application message after receiving any message from another member, or daily if no application messages are sent.
---




https://code.briarproject.org/briar/briar-mailbox
https://code.briarproject.org/briar/briar/-/wikis/A-Quick-Overview-of-the-Protocol-Stack
https://code.briarproject.org/briar/briar-spec/blob/master/protocols/BTP.md
https://code.briarproject.org/briar/briar/-/wikis/threat-model
---
Bramble Transport Protocol (BTP) is a transport layer security protocol suitable for delay-tolerant networks. It provides a secure channel between two peers, ensuring the confidentiality, integrity, authenticity and forward secrecy of their communication across a wide range of underlying transports.
BTP's main components are a time-based key management protocol and a wire protocol for securely carrying streams of data.
BTP can operate over any transport that can deliver a stream of bytes from one device to another on a best-effort basis, meaning that streams may be delayed, lost, reordered or duplicated. The underlying transport is not required to provide any security properties.
The BTP wire protocol includes optional padding and does not use any timeouts, handshakes or plaintext headers. This makes BTP compatible with traffic analysis prevention techniques such as traffic morphing, with the goal of making it difficult to distinguish BTP from other protocols.
BTP does not attempt to conceal the identities of the communicating parties or the fact that they are communicating - in other words, it does not provide anonymity, unlinkability or unobservability. If such properties are required, BTP can use an anonymity system such as Tor as the underlying transport.
Forward secrecy is achieved by establishing an initial root key between two peers and using a one-way key derivation function to derive a series of temporary keys from the root key. Once both peers have deleted a given key, it cannot be re-derived if the peer devices are later compromised.
---

