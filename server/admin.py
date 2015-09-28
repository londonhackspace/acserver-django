from django.contrib import admin

from models import Tool, User, Card, Permissions

class ToolAdmin(admin.ModelAdmin):
  pass
              
class UserAdmin(admin.ModelAdmin):
  pass
              
class CardAdmin(admin.ModelAdmin):
  pass

class PermissionsAdmin(admin.ModelAdmin):
  pass
              
admin.site.register(Tool, ToolAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Card, CardAdmin)
admin.site.register(Permissions, PermissionsAdmin)
