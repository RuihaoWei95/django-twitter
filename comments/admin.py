from django.contrib import admin
from comments.models import Comment
# Register your models here.


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('tweet', 'user', 'content', 'created_at', 'updated_at')
    data_hierarchy = 'created_at'

# Register your models here.
