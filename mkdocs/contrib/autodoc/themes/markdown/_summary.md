{% for section, members in sections %}
{% if section != 'Private Variable' %}
### {{ section }}
{% for member, typ in members %}
{% if member.kind == 'Enum' %}
[{{ member.name }}](#{{ member.name }})
{% elif member.kind == 'Class' %}
[{{ member.name }}]({{ member.url }}) 
{% elif member.kind == 'Module' %}
[{{ member.name }}]({{ member.url }})
{% elif 'Function' in member.kind or 'Method' in member.kind or 'Builtin' in member.kind %}
def [{{ member.name }}](#def-{{ member.name.lower() }}){{ member.args }}
{% else %}
{{ member.name }} : {{ type }}
{% endif %}
{% endfor %}
{% endif %}
{% endfor %}