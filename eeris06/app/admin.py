from django.contrib import admin
from .models import CustomUser, Submission, Receipt

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['email','first_name','last_name', "date_joined", "is_superuser", "is_staff"]
    search_fields = ['email','first_name','last_name']
    ordering = ['-date_joined']  # newest accounts first
    show_facets = admin.ShowFacets.ALWAYS

admin.site.register(Submission)
admin.site.register(Receipt)



    



