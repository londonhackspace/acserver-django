from django.core.management.base import BaseCommand, CommandError
from server.models import Permission

class Command(BaseCommand):
    args = "<from> <to>"
    help = "Copies permissions from tool A to tool B"

    def handle(self, *args, **options):
        if len(args) != 2:
            raise CommandError('Please supply two tool IDs')

        fromTool = Permission.objects.filter(tool_id=int(args[0]))
        for perm in fromTool:
            newperm = Permission.objects.get(tool_id=int(args[1]), user=perm.user)
            if newperm is None:
                newperm = Permission(tool_id=int(args[1]),
                                     user=perm.user,
                                     permission=perm.permission,
                                     addedby=perm.addedby,
                                     date=perm.date)
            else:
                newperm.permission = perm.permission
            newperm.save()
