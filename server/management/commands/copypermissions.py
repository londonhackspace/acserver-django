from django.core.management.base import BaseCommand, CommandError
from server.models import Permission


class Command(BaseCommand):
    help = "Copies permissions from tool A to tool B"

  def add_arguments(self, parser):
        parser.add_argument('toola', type=int)
        parser.add_argument('toolb', type=int)

    def handle(self, *args, **options):
        toola = options['toola']
        toolb = options['toolb']

        fromTool = Permission.objects.filter(tool_id=toola)
        for perm in fromTool:
            newperm = None
            try:
                newperm = Permission.objects.get(tool_id=toolb, user=perm.user)
            except:
                pass
            if newperm is None:
                newperm = Permission(tool_id=toolb,
                                     user=perm.user,
                                     permission=perm.permission,
                                     addedby=perm.addedby,
                                     date=perm.date)
            else:
                newperm.permission = perm.permission
            newperm.save()
