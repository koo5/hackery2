http://www.tclcommunityassociation.org/wub/proceedings/Proceedings-2013/JeanFrancoisLarvoire/A%20simpler%20and%20shorter%20representation%20of%20XML%20data%20inspired%20by%20Tcl.pdf
https://news.ycombinator.com/item?id=9547101


SML is a human-friendly almost-equvalent syntax for XML. You can convert between the formats freely.
```
Known limitations:
	-The converted files use the local operating system line endings (a combination of \r and \n). So if theinitial XML file was encoded with line endings for another operating system, converting it to SML thenback will not be binary equal to the initial file. But it will still be logically equal, as the XML spec statesthat all line endings are equivalent to \n.
	-As of 2013-09-22, complex !doctype declarations with locally defined !elements are not supported.
```
note: locally defined `!ELEMENT` means:  
```
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE greeting [
  <!ELEMENT greeting (#PCDATA)>
]>
<greeting>Hello, world!</greeting>
```
-- https://www.w3.org/TR/xml/


