{% macro add_images(data) %}
    {% for item in data %}
        < img src="{{ item }}.jpg "  /  >
    {% endfor %}
{% endmacro %}