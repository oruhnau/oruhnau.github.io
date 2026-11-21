{# Override of RenderCV's typst/SectionBeginning.j2.typ. Change: section titles in the light weight. #}
== #text(weight: "light")[{{section_title}}]
{% if entry_type in ["ReversedNumberedEntry"] %}

#reversed-numbered-entries(
  [
{% endif %}
