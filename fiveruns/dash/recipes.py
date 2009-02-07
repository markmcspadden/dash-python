import metrics
import logging

logger = logging.getLogger('fiveruns.dash.recipes')
registry = {}

class Recipe(metrics.MetricSetting):

    def __init__(self, name, url):
        super(Recipe, self).__init__()
        self.name = name
        self.url = url
        self._register()

    def _add_metric(self, *args, **options):
        "Add a metric"
        options['recipe_name'] = self.name
        options['recipe_url'] = self.url
        super(Recipe, self)._add_metric(*args, **options)

    def _register(self):
        "Register this recipe"
        key = (self.name, self.url)
        if registry.has_key(key):
            raise DuplicateRecipe(self.name, self.url)
        else:
            registry[key] = self
            logger.debug("Registered recipe `%s' for `%s'" % (self.name, self.url))

    def _replay_recipe(self, recipe):
        logger.debug("Adding %d metric(s) from recipe `%s' for `%s' to recipe `%s' for `%s'" % (
            len(recipe.metrics),
            recipe.name, recipe.url,
            self.name, self.url))
        super(Recipe, self)._replay_recipe(recipe)

def find(name, url):
    "Find a registered recipe"
    if registry.has_key((name, url)):
        return registry[(name, url)]
    elif not url:
        matching = [r for k, r in registry.iteritems() if k[0] == name]
        number = len(matching)
        if number == 1:
            return matching[0]
        elif number > 1:
            raise AmbiguousRecipe(name, [u for (n, u) in matching])    
        else:
            raise UnknownRecipe(name, url)
    else:
        raise UnknownRecipe(name, url)

class RecipeError(NameError):

    def __init__(self, name, urls):
        self.name = name
        self.urls = urls

    def __str__(self):
        return "`%s' defined for `%s'" % (self.name, self.urls)

class UnknownRecipe(NameError):
    """
    Raised when fiveruns.dash.recipes.find cannot find a requested recipe
    """

    def __init__(self, name, url):
        self.name = name
        self.url = url

    def __str__(self):
        return "`%s' for `%s'" % (self.name, self.url)
        
class AmbiguousRecipe(RecipeError):
    """
    Raised when fiveruns.dash.recipes.find matches multiple requested recipes
    """
    pass

class DuplicateRecipe(RecipeError):
    """
    Raised when fiveruns.dash.recipes.find cannot register a recipe due to a duplicate
    """        
    pass