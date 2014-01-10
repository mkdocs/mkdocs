# Django Braces compatibility

The `django-vanilla-views` package is almost completely compatible with the mixin classes provided by the popular [`django-braces`][django-braces] package.

The full set of mixins is listed below.  If you believe any of these entries to be incorrect, or if new mixins are added that are not listed here, then please [open an issue on GitHub][issues] so we can keep the information up to date.

## Access Mixins

<table border=1>
<tr><th>Mixin class</th><th>API compatible</th></tr>
<tr><td>LoginRequiredMixin</td><td>Yes</td></tr>
<tr><td>PermissionRequiredMixin</td><td>Yes</td></tr>
<tr><td>MultiplePermissionsRequiredMixin</td><td>Yes</td></tr>
<tr><td>GroupRequiredMixin</td><td>Yes</td></tr>
<tr><td>SuperuserRequiredMixin</td><td>Yes</td></tr>
<tr><td>StaffuserRequiredMixin</td><td>Yes</td></tr>
</table>

## Form Mixins

<table border=1>
<tr><th>Mixin class</th><th>API compatible</th></tr>
<tr><td>CsrfExemptMixin</td><td>Yes</td></tr>
<tr><td>UserFormKwargsMixin</td><td>No (*)</td></tr>
<tr><td>UserKwargModelFormMixin</td><td>Yes</td></tr>
<tr><td>SuccessURLRedirectListMixin</td><td>Yes</td></tr>
<tr><td>FormValidMessageMixin</td><td>Yes</td></tr>
<tr><td>FormInvalidMessageMixin</td><td>Yes</td></tr>
<tr><td>FormMessagesMixin</td><td>Yes</td></tr>
</table>

(*) The `UserFormKwargsMixin` class is not compatible because it overrides the `get_form_kwargs()` method, which does not exist in `django-vanilla-views`.

You can instead write a `django-vanilla-views` compatible mixin, like this:

    class UserFormKwargsMixin(object):
        def get_form(self, data=None, files=None, **kwargs):
            kwargs['user'] = self.request.user
            return super(UserFormKwargsMixin, self).get_form(data=data, files=files, **kwargs)

## Other Mixins

<table border=1>
<tr><th>Mixin class</th><th>API compatible</th></tr>
<tr><td>SetHeadlineMixin</td><td>Yes</td></tr>
<tr><td>SelectRelatedMixin</td><td>Yes</td></tr>
<tr><td>PrefetchRelatedMixin</td><td>Yes</td></tr>
<tr><td>JSONResponseMixin</td><td>Yes</td></tr>
<tr><td>JsonRequestResponseMixin</td><td>Yes</td></tr>
<tr><td>AjaxResponseMixin</td><td>Yes</td></tr>
<tr><td>OrderableListMixin</td><td>Yes</td></tr>
<tr><td>CanonicalSlugDetailMixin</td><td>Yes (*)</td></tr>
</table>

(*) The `CanonicalSlugDetailMixin` is not compatible in the current `1.2.2` PyPI release, but is compatible in the current `master` branch, and should be compatible in the next upcoming PyPI release.

Note that if using `CanonicalSlugDetailMixin` you **must** also set a `slug_url_kwarg` on the view.

[django-braces]: https://github.com/brack3t/django-braces
[issues]: https://github.com/tomchristie/django-vanilla-views/issues
