# Migration Guide

## Model Views

This document provides the complete set of API changes between Django's existing model views and the corresponding `django-vanilla-views` implementations.

It covers `ListView`, `DetailView`, `CreateView`, `UpdateView` and `DeleteView`.  For the base views please [see here][base-views].

Wherever API points have been removed, we provide examples of what you should be using instead.

This scope of this migration guide may appear intimidating at first if you're intending to port your existing views accross to using `django-vanilla-views`, but you should be able to approach refactorings in a fairly simple step-by-step manner, working through each item in the list one at a time.

Although a large amount of API has been removed, the functionality that the views provide should be identical to Django's existing views.  If you believe you've found some behavior in Django's generic class based views that can't also be trivially achieved in `django-vanilla-views`, then please [open a ticket][tickets], and we'll treat it as a bug.

---

#### `pk_url_field`, `slug_url_field`, `slug_url_kwarg`, `get_slug_field()`

---

**These have been replaced** with a simpler style using `lookup_field` and `lookup_url_kwarg`.

If you need non-pk based lookup, specify `lookup_field` on the view:

    class AccountListView(ListView):
        model = Account
        lookup_field = 'slug'

If you need a differing URL kwarg from the model field name, you should also set `lookup_url_kwarg`.

    class AccountListView(ListView):
        model = Account
        lookup_field = 'slug'
        lookup_url_kwarg = 'account_name'

For more complex lookups, override `get_object()`, like so:

    class AccountListView(ListView):
		def get_object(self):
		    queryset = self.get_queryset()
		    return get_object_or_404(queryset, slug=self.kwargs['slug'], owner=self.request.user)

---

#### `initial`, `prefix`, `get_initial()`, `get_prefix()`, `get_form_kwargs()`

---

**These are all removed**.  If you need to override how the form is intialized, just override `get_form()`.

For example, instead of this:

	def get_form_kwargs(self):
	    kwargs = super(AccountEditView, self).get_form_kwargs
	    kwargs['user'] = self.request.user
	    return kwargs

You should write this:

    def get_form(self, data, files, **kwargs):
        kwargs['user'] = self.request.user
        return AccountForm(data, files, **kwargs)

---

#### `template_name_field`

---

**This is removed**.  If you need to dynamically determine template names, you should override `get_template_names()`.

    def get_template_names(self):
        return [self.object.template]

---

#### `content_type`, `response_cls`

---

**These are removed**.  If you need to customize how responses are rendered, you should override `render_to_response()`.

    def render_to_response(context):
        return JSONResponse(self.request, context)

If you needed to override the content type, you might write:

    def render_to_response(context):
    	template = self.get_template_names()
        return TemplateResponse(self.request, template, context, content_type='text/plain')

---

#### `paginator_cls`, `paginate_orphans`, `get_paginate_orphans()`

---

**These are removed**.  If you need to customize how the paginator is instantiated, you should override `get_paginator()`.

    def get_paginator(self, queryset, page_size):
        return CustomPaginator(queryset, page_size, orphans=3)

---

#### `paginate_queryset()`

---

The **return value has been simplified**.  Instead of returning a 4-tuple it now simply returns a page object.  Instead of this:

	(page, paginator, queryset, is_paginated) = self.paginate_queryset(queryset, page_size)

You should write this:

    page = self.paginate_queryset(queryset, page_size)

The page object contains a `paginator` attribute, an `object_list` attribute, and a `has_other_pages()` method, so you still have access to the same set of information that is available in the 4-tuple return style.

---

#### `get_object()`

---

The **call signature has been simplified**.  The `get_object()` method no longer takes an optional `queryset` parameter.

---

#### `get_form_class()`

---

The behavior has been **refactored to use less magical behavior**.  In the regular Django implementation, if neither `model` or `form_class` is specified on the view, then `get_form_class()` will fallback to attempting to automatically generate a form class based on either the object currently being operated on, or failing that to generate a form class by calling `get_queryset` and determining a default model form class from that.  Failing both of those it'll raise a configuration error.

In `django-vanilla-views`, if neither the `model` or `form_class` is specified, it'll raise a configuration error.  If you need any more complex behavior that that, you should override `get_form_class()`.

---

#### `get_template_names()`

---

The behavior has been **refactored to use less magical behavior**.  In the regular Django implementation if `template_name` has been defined that will be the preferred option.  Failing that, if `template_name_field` is defined, and `object` is set on the view, then a template name given by a field on the object will be the next most preferred option.  Next, if `object` is set on the view then `{app}/{model_name}{suffix}.html` will be used based on the class of the object.  Finally if `model` is set on the view then  `{app}/{model_name}{suffix}.html` will be used.

In `django-vanilla-views`, if `template_name` is defined that will be used, otherwise if `model` is defined it'll use `{app}/{model_name}{suffix}.html`.  If neither is defined it'll raise a configuration error.  If you need any more complex behavior that that, you should override `get_template_names()`.

---

#### `get_form()`

---

**This is refactored**, instead of taking a single `form_class` argument it instead takes the form `data` and `files` arguments, plus optional extra keyword arguments.  This results in a simpler, more direct control flow in the implementation.

Instead of this in your views:

    form_cls = self.get_form_class()
    form = self.get_form(form_cls)

You should write this:

    form = self.get_form(request.DATA, request.FILES, instance=self.object)

[base-views]: base-views.md
[tickets]: https://github.com/tomchristie/django-vanilla-views/issues
