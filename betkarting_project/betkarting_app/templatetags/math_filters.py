from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiplie l'argument par la valeur."""
    try:
        # Nous devons convertir en float ou Decimal pour garantir la multiplication
        # des types numériques. Les Decimal sont préférables pour les montants monétaires.
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''