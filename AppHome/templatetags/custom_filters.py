from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='filter_by_attr')
def filter_by_attr(items, attr):
    """
    Filtra uma lista de objetos por um atributo especificado
    Exemplo de uso no template:
    {{ items|filter_by_attr:"periodo=Manhã" }}
    """
    if not items:
        return []
    
    # Extrai o nome do atributo e valor (ex: "periodo=Manhã")
    attr_name, attr_value = attr.split('=')
    
    return [item for item in items if str(getattr(item, attr_name, '')) == attr_value]

@register.filter(name='sort_by')
def sort_by(items, attr):
    """
    Ordena uma lista de objetos por um atributo especificado
    Exemplo de uso no template:
    {{ items|sort_by:"projecao" }}
    """
    if not items:
        return []
    
    reverse_sort = attr.startswith('-')
    attr = attr.lstrip('-')
    
    return sorted(items, key=lambda x: getattr(x, attr, 0), reverse=reverse_sort)

# Adicione outros filtros customizados conforme necessário
