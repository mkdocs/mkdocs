{% for member in members %}
{% if member.kind not in ('Module', 'Class', 'Member', 'Variable') %}
{% if 'Static' in member.kind or 'Class' in member.kind %}
### `def {{ member.name }}{{ member.args }}` **[{{ member.kind.lower() }}]**
{% else %}
### `def {{ member.name }}{{ member.args }}`
{% endif %}
{% if member.reimpliments %}
_Reimpliments: {{ member.reimpliments }}_
{% endif %}
{% if member.reimplimented %}
_Reimplimented: {{ member.reimplimented }}_
{% endif %}
{% if member.raw_docs %}
{{ member.raw_docs }}
{% endif %}
{% endif %}
{% endfor %}