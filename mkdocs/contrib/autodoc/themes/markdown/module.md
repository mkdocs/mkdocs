{{ title.split('.')[-1] }}
=================================
{% if breadcrumbs %}
from {{ '.'.join(breadcrumbs) }}
{% endif %}

{% if brief %}
{{ brief }} [More...](#details)
{% elif page.raw_docs %}
{{ page.raw_docs }}
{% endif %}

{% include '_summary.md' %}

{% if brief %}
Details
------------------
{{ page.raw_docs }}
{% endif %}

Functions
------------------
{% include '_details.md' %}

