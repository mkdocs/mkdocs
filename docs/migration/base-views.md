# Migration Guide

## Base Views

This document provides the complete set of API changes between Django's existing basic generic views and the corresponding `django-vanilla-views` implementations.

It covers `RedirectView`, `TemplateView` and `FormView`.  For the model views please [see here][model-views].

Wherever API points have been removed, we provide examples of what you should be using instead.

Although a large amount of API has been removed, the functionality that the views provide should be identical to Django's existing views.  If you believe you've found some behavior in Django's generic class based views that can't also be trivially achieved in `django-vanilla-views`, then please [open a ticket][tickets], and we'll treat it as a bug.

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

#### `get_form()`

---

**This is refactored**, instead of taking a single `form_class` argument it instead takes the form `data` and `files` arguments, plus optional extra keyword arguments.  This results in a simpler, more direct control flow in the implementation.

Instead of this in your views:

    form_cls = self.get_form_class()
    form = self.get_form(form_cls)

You should write this:

    form = self.get_form(request.DATA, request.FILES)

[model-views]: model-views.md
[tickets]: https://github.com/tomchristie/django-vanilla-views/issues
