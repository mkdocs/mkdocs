# Django Extra Views Compatibility

You can use the views in `django-vanilla-views` alongside the additional views that are supplied by [`django-extra-views`][django-extra-views] just fine, although it will mean that you'll be working with Django's mixin style for some of your views, and the Vanilla style for other views.

A good candidate for a future PyPI package would be a version of [`django-extra-views`][django-extra-views], that uses the `django-vanilla-views` views as the base and is implemented in a more vanilla-like style.

There are also a couple of stand-alone mixin classes provided by [`django-extra-views`][django-extra-views], both of which are fully API compatible with `django-vanilla-views`.  The mixins are listed below.  If you believe either of these entries to be incorrect, or if new mixins are added that are not listed here, then please [open an issue on GitHub][issues] so we can keep the information up to date.

## Mixin classes

<table border=1>
<tr><th>Mixin class</th><th>API compatible</th></tr>
<tr><td>SortableListMixin</td><td>Yes</td></tr>
<tr><td>SearchableListMixin</td><td>Yes</td></tr>
</table>

[django-extra-views]: https://github.com/andrewingram/django-extra-views
[issues]: https://github.com/tomchristie/django-vanilla-views/issues
