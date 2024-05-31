from django.contrib.auth.models import User
from model_bakery.recipe import Recipe, seq
from fellchensammlung.models import *

location = Recipe(
    Location,
    place_id=seq(''),
    name=seq('Location_'),
    longitude=seq(""),
    latitude=seq(""),
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
