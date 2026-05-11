-- this defines the schema where the model will be saved.
{% macro generate_schema_name(custom_schema_name,node)%}
    {% if custom_schema_name %}
        {{custom_schema_name}}
    {% else %}
        {{target.schema}}
    {% endif %}
{% endmacro %}