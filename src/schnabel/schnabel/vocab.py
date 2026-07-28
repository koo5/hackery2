"""Predicate constants. Predicates earn their place by being used (D-002);
this module is the de-facto vocab record, not an upfront ontology.

Convention: ``urn:schnabel:vocab:<area>:<term>``. Areas are short ASCII tokens
that map to emitting tools/domains. Add new areas as files in this module's
namespace (or as additional ``Namespace`` constants below) when they appear.
"""

from rdflib import Namespace, URIRef

# Common schnabel terms (not tied to a single emitter).
SCHNABEL = Namespace("urn:schnabel:vocab:core:")

# Activity-level pointers used by the EventLog itself.
latest_invocation = SCHNABEL.latest_invocation
points_to = SCHNABEL.points_to

# Per-area vocabularies. Each is a separate namespace so a future SPARQL query
# can prefix-filter by emitter.
BFG = Namespace("urn:schnabel:vocab:bfg:")
"""``bfg:`` — btrfsgit (https://github.com/koo5/btrfsgit) invocation events."""

BACKUP = Namespace("urn:schnabel:vocab:backup:")
"""``backup:`` — backup.py orchestration events."""

INTENTION = Namespace("urn:schnabel:vocab:intention:")
"""``intention:`` — dev-intention tracker events. Phase 5."""

# Seed predicates we expect to emit early. Don't add anything here until it's
# actually written into the store by code somewhere; that's the contract.
__all__ = [
    "SCHNABEL",
    "BFG",
    "BACKUP",
    "INTENTION",
    "latest_invocation",
    "points_to",
]
