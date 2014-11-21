{{ title }}
==========================
from {{ '.'.join(breadcrumbs) }}

{% if inherits %}
Inherits {{ ', '.join(inherits) }}
{% endif %}
{% if inherited_by %}
Inherited by {{ ', '.join(inherited_by) }}
{% endif %}

{% if brief %}
{{ brief }} [More...](#details)
{% elif page.raw_docs %}
{{ page.raw_docs }}
{% endif %}

{% include '_summary.md' %}

{% if brief %}
Details
---------------
{{ page.raw_docs }}
{% endif %}

Methods
---------------
{% include '_details.md' %}
