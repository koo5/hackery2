type Ref = number;
type ValMap = Map<Ref, Val>;
/* a Mapping from Refs to actual values.*/
//vals: ValMap;
/* a map of domain-specific materializations */
type MatMap = Map<Val, any>;
/* a Map of Materialization Maps.  */
mats: MatMap;

