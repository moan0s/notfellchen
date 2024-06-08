import logging

from django.core.management.base import BaseCommand, CommandError
from django.core.files import File

from fellchensammlung import baker_recipes
from model_bakery import baker

from fellchensammlung.models import AdoptionNotice, Species, Animal, Image, ModerationAction, User, Rule, \
    Report, Comment, ReportAdoptionNotice


class Command(BaseCommand):
    help = "Populates the database with test data"

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing data",
        )

    @staticmethod
    def populate_db(clear=False):
        if clear:
            ModerationAction.objects.all().delete()
            Report.objects.all().delete()
            Rule.objects.all().delete()
            Comment.objects.all().delete()
            AdoptionNotice.objects.all().delete()
            Animal.objects.all().delete()
            User.objects.all().delete()

        # Check if there already is and AdoptionNotice named Vermittung1TestSalt9227. If it is, the database
        # is already populated and no data will be added again
        try:
            AdoptionNotice.objects.get(name="Vermittlung1TestSalt9227")
            print("Database already populated. No additional data will be created")
            return
        except AdoptionNotice.DoesNotExist:
            pass

        rescue1 = baker.make_recipe(
            'fellchensammlung.rescue_org'
        )
        rescue2 = baker.make_recipe(
            'fellchensammlung.rescue_org'
        )

        adoption1 = baker.make(AdoptionNotice,
                               name="Vermittlung1TestSalt9227",
                               organization=rescue1,
                               location=baker.make_recipe("fellchensammlung.location"))

        adoption2 = baker.make(AdoptionNotice,
                               name="Vermittung2",
                               organization=rescue2,
                               location=baker.make_recipe("fellchensammlung.location"))

        cat = baker.make(Species, name="Katze")
        rat = baker.make(Species, name="Farbratte")

        rat1 = baker.make(Animal,
                          name="Rat1",
                          adoption_notice=adoption1,
                          species=rat,
                          description="Eine unglaublich süße Ratte")
        rat2 = baker.make(Animal, name="Rat2", adoption_notice=adoption1, species=rat)
        cat1 = baker.make(Animal, name="Cat1", adoption_notice=adoption2, species=cat)

        animal_photo_combination = [(cat1, "cat1.jpeg"), (rat1, "rat1.jpg"), (rat2, "rat2.jpg")]
        for animal, filename in animal_photo_combination:
            image_object = Image()
            image_object.alt_text = f"Picture of {animal}"
            image_object.title = f"Picture of {animal}"
            image_object.image.save(f"{filename}", File(open(f"./src/tests/assets/{filename}", 'rb')))
            image_object.save()

            animal.photos.add(image_object)

        rule1 = baker.make(Rule, title="Be excellent ot each other", rule_text="This is **markdown**")
        rule2 = baker.make(Rule,
                           title="Keep al least the minimum number of animals for species",
                           rule_text="This is not markdown")
        rule3 = baker.make(Rule,
                           title="Rule three",
                           rule_text="Everything needs at least three rules")

        report1 = baker.make(ReportAdoptionNotice, adoption_notice=adoption1, reported_broken_rules=[rule1, rule2],
                             user_comment="This seems sketchy")

        moderation_action1 = baker.make(ModerationAction,
                                        report=report1,
                                        action=ModerationAction.COMMENT,
                                        public_comment="This has been seen by a moderator")
        moderation_action1 = baker.make(ModerationAction,
                                        report=report1,
                                        action=ModerationAction.DELETE,
                                        public_comment="A moderator has deleted the reported content")

        User.objects.create_user('test', password='foobar')
        admin1 = User.objects.create_superuser(username="admin", password="admin", email="admin1@example.org",
                                               trust_level=User.ADMIN)

        mod1 = User.objects.create_user(username="mod1", password="mod", email="mod1@example.org",
                                        trust_level=User.MODERATOR)

        comment1 = baker.make(Comment, user=admin1, text="This is a comment", adoption_notice=adoption1)
        comment2 = baker.make(Comment,
                              user=mod1,
                              text="This is a reply",
                              adoption_notice=adoption1,
                              reply_to=comment1)

    def handle(self, *args, **options):
        self.populate_db(options["clear"])
