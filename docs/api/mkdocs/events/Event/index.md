Event
==========================
from <a href="api/mkdocs">mkdocs</a>.<a href="api/mkdocs/events">events</a>



Inherited by <a href="api/mkdocs/events/Execute">Execute</a>, <a href="api/mkdocs/events/GenerateContent">GenerateContent</a>, <a href="api/mkdocs/events/PreBuild">PreBuild</a>, <a href="api/mkdocs/events/BuildPage">BuildPage</a>



Abstract event extension class for mkdocs 




### Public Method


def [broadcast](#def-broadcast)()









Methods
---------------











### `def broadcast()`




Broadcasts this event to all the listening callbacks.  If any callback consumes this event, then
it will stop processing for all other events and return that it has already been processed.

:return     <bool> | consumed


