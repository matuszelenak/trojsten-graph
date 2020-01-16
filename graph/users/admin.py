from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.template.loader import get_template
from django.urls import reverse

from users.models import ContentSuggestion, EmailPatternWhitelist, InviteCode


@admin.register(ContentSuggestion)
class ContentSuggestionAdmin(admin.ModelAdmin):
    list_display = ('short_suggestion', 'status', 'submitted_by', 'date_created', 'date_resolved')
    readonly_fields = ('suggestion', 'submitted_by', 'date_created')
    list_filter = ['status', 'submitted_by']

    def short_suggestion(self, obj):
        if len(obj.suggestion) >= 80:
            return f'{obj.suggestion[:77]}...'
        return obj.suggestion


@admin.register(EmailPatternWhitelist)
class EmailPatternWhitelistAdmin(admin.ModelAdmin):
    list_display = ('pattern',)


class InviteCodeForm(forms.Form):
    number = forms.IntegerField()


@admin.register(InviteCode)
class InviteCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'copy_to_clipboard', 'user')
    change_list_template = 'people/admin/invite_code_changelist.html'
    ordering = ['-user']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        self.request = request
        if request.method == 'POST' and 'generate_invites' in request.POST:
            form = InviteCodeForm(request.POST)
            if form.is_valid():
                codes = InviteCode.objects.bulk_generate(form.cleaned_data['number'])
                messages.success(request, f'Successfully created {len(codes)} codes')
                return HttpResponseRedirect(reverse('admin:users_invitecode_changelist'))

        return super().changelist_view(request, extra_context=extra_context)

    def copy_to_clipboard(self, obj):
        if not obj.user:
            link = f'{self.request.scheme}://{self.request.get_host()}' + reverse('registration') + f'?code={obj.code}'
            return get_template('people/admin/copy_invite_link.html').render({'link': link})
