events
=================================

from <a href="api/mkdocs">mkdocs</a>.events






### Public Class


[BuildPage](api/mkdocs/events/BuildPage) 



[Event](api/mkdocs/events/Event) 



[Execute](api/mkdocs/events/Execute) 



[GenerateContent](api/mkdocs/events/GenerateContent) 



[PreBuild](api/mkdocs/events/PreBuild) 





### Public Function


def [register_callback](#def-register_callback)(event_type, callback)







Functions
------------------













### `def register_callback(event_type, callback)`




Registers a callback method to the given event type.

:param      event_type | subclass of <Event>
            callback   | <callable>



