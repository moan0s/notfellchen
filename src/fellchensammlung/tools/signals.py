import logging


def _get_perms(permission_name_list):
    from django.contrib.auth.models import Permission
    permissions = []
    for permission_name in permission_name_list:
        try:
            permission = Permission.objects.get(codename=permission_name)
            permissions.append(permission)
        except Permission.DoesNotExist:
            logging.warning("Permissions not correctly migrated, please run the migration again")
    return permissions


def ensure_groups(sender, **kwargs):
    from django.contrib.auth.models import Group
    from django.contrib.auth.models import Permission


    member_permissions = []
    coordinator_permissions = ["create_active_adoption_notice"]
    moderator_permissions = coordinator_permissions + ["view_report", "add_moderationaction", "change_user"]
    admin_permissions = moderator_permissions

    admins, created = Group.objects.get_or_create(name="Admins")
    admins.permissions.set(_get_perms(admin_permissions))

    moderators, created = Group.objects.get_or_create(name="Moderators")
    moderators.permissions.set(_get_perms(moderator_permissions))

    coordinators, created = Group.objects.get_or_create(name="Coordinators")
    coordinators.permissions.set(_get_perms(coordinator_permissions))

    members, created = Group.objects.get_or_create(name="Members")
    members.permissions.set(_get_perms(member_permissions))

def ensure_languages(sender, **kwargs):
    from fellchensammlung.models import Language
    Language.objects.get_or_create(name="Deutsch", languagecode="de")
    Language.objects.get_or_create(name="English", languagecode="en")
