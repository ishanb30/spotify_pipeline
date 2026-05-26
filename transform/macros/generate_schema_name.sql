{#
 Overrides dbt's default schema name generation. Uses the custom schema
 configured in dbt_project.yml (+schema:) if provided, otherwise falls
 back to the target schema from profiles.yml.
#}

{% macro generate_schema_name(custom_schema_name) %}
    {% if custom_schema_name %}
        {{ custom_schema_name }}
    {% else %}
        {{ target.schema }}
    {% endif %}
{% endmacro %}