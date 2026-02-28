from django.contrib import admin

from .models import Fact, FactVersion, MediaAsset, Person, Relationship, Tree, TreeMembership

admin.site.register(Tree)
admin.site.register(TreeMembership)
admin.site.register(Person)
admin.site.register(Relationship)
admin.site.register(MediaAsset)
admin.site.register(Fact)
admin.site.register(FactVersion)
