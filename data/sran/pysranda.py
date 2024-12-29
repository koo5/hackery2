pySRalNAto


# we "might" have an in-memory, "directly accessible" store, but it would probably be best to only treat it as a cache, or to only have a cache tied to a particular (distributed) database.

#it's ok to have this simple events array for testing and basic examples though

events = [

]

def loop():

	while True:







		pass


class IOChannel





class RobotPlayground1(IOChannel):
	pass




class InferenceStrategy(IOChannel):
	pass




class MyTopDownInference(InferenceStrategy):
	"""
	i think this is what might be missing from nars for actual agi?

	knowing a-priori some high-level ideas that we want the robot to have,
	and encoding them in some form,
	for an example of a substantial undertaking in this direction, taking a commonsense kb,
	and encoding the kind of shit like "elephants have four legs",

	*we* decide how to identify "elephant" and how to encode "four legs",
	and i assume nars has a "has a" association/operator?,, or is that just like a strong undirected association?

	or:
	"if something is open, it's usually possible to go through it" (that is, unless we're talking electrical circuits)
	- is probably something nars would encode as a series of events:
	<<x>> is_opened  -- at time 1
	<<y>> passess_through <<x>>  -- at time 2


	then we may try to backtrack from the top-level events down, generating events that would possibly have given rise to that high-level event.


	sran will simply latch on to these pre-generated structures at some point, as an inference module pattern-matches one of those pregenerated terms.





	"""



class IOControl:
	"""
	sometimes we may want to killl some long running in-progress queries
	"""
	pass









"""
guidance notes

SELF is ambiguous nonsense
why self, why not identify actual actors or subsystems that took place in an interaction?






"""
