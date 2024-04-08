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



------

https://docs.farcaster.xyz/reference/frames/spec

Any Ethereum address can register a Farcaster account by making an onchain transaction.


https://spec.matrix.org/latest/

https://atproto.com/

https://bsky.app/feeds

https://blog.paulbohm.com/p/blue-sky-farcaster-substack-notes

https://blockprotocol.org/docs/blocks/environments#your-own-application

https://github.com/farcasterxyz/protocol/blob/main/docs/OVERVIEW.md

https://www.supercast.xyz/

https://yup.io/

https://neynar.com/


