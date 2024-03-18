from django.contrib.auth.models import User
from model_bakery.recipe import Recipe, seq
from fellchensammlung.models import *

location = Recipe(
    Location,
    name=seq('Ort_'),
    description=seq('Detaillierte Beschreibung_'),
    postcode=seq("7322"),
)

rescue_org = Recipe(
    RescueOrganization,
    name=seq('Rattennothilfe_'),
    location=location.make()
)

rat = Recipe(
    Animal,
    name=seq('Ratte_'),
)

cat = Recipe(
    Animal,
    name=seq('Katze_'),
)
