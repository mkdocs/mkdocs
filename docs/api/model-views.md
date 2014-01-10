<a class="github" href="model_views.py"></a>

# Model Views

The model views provide a simple set of generic views for working with Django querysets and model instances.

They replicate the functionality of Django's existing `ListView`, `DetailView`, `CreateView`, `UpdateView` and `DeleteView`, but present a simpler API and implementation.

	View -- GenericModelView --+-- ListView
	                           |
	                           +-- DetailView
	                           |
	                           +-- CreateView
	                           |
	                           +-- UpdateView
	                           |
	                           +-- DeleteView

---

## GenericModelView

The `GenericModelView` class is used as the base class for all of the model views, and provides methods allowing for a default set of viewing, listing and editing actions.

### Attributes

#### model

The model class that the view operates on.  This is used as a shortcut to provide default behavior for the view.  The default behaviour may be overridden by setting more specific attributes, or by overriding methods on the view.

#### queryset

The base queryset that should be used for list views, or used when performing object lookups for detail views.  If set to `None` then a default queryset will be used based on the `model` attribute.  Defaults to `None`.

#### lookup_field

The name of the model field that should be used for object lookups.  Defaults to `'pk'`.

#### lookup_url_kwarg

The name of the URLconf keyword argument that should be used for object lookups.  If unset this defaults to the same value as `lookup_field`.

#### form_class

The form class that should be used for create or update views.  If set to `None` then a default form class will be used based on the `model` and `fields` attributes.  Defaults to `None`.

#### fields

A list of strings, representing the fields that should be displayed by the form.  This may be used along with the `model` attribute, as a shortcut to setting the `form_class` attribute.  Defaults to `None`.

#### paginate_by

The number of items to return in each page.  Set to a positive integer value to enable pagination.  If set to `None` then pagination is disabled.  Defaults to `None`.

#### page_kwarg

The name of the URL query parameter that is used to select the active page in a paginated list.  For example: `http://example.com/widget_list?page=6`.  Defaults to `'page'`.

#### template_name

A string representing the template name that should be used when rendering the response content.  If set to `None`, then the template name will be automatically generated based on the `model` attribute.  Defaults to `None`.

#### template_name_suffix

A suffix that should be appended when automatically generating template names based on the `model` attribute.  Defaults to `None`, but is set to an appropriate value of either `'_detail'`, `'_list'` or `'_form'` by each of the model view subclasses.

#### context_object_name

A key to use when passing the queryset or instance as context to the response.  If set to `None` then the context object name will be automatically generated based on the `model` attribute.  Defaults to `None`.

---

### Methods

#### get_queryset(self)

This method should return a queryset representing the set of instances that the view should operate on.

The default behavior of this method is:

* If the `queryset` attribute is set, then return that.
* Otherwise fallback to returning the default queryset for the model class as determined by the `model` atttibute.
* If neither the `queryset` or `model` attributes are set then a configuration error will be raised.

You can customize how the querysets for the view are determined by overriding this method.  For example:

    def get_queryset(self):
        """
        Custom queryset that only returns book instances owned by the logged-in user.
        """
        return Book.objects.filter(owner=self.request.user)

#### get_object(self)

This method should return a single model instance that the view should operate on, and is used by `DetailView`, `UpdateView` and `DeleteView`.

The default behavior for this method is:

* Call `get_queryset()` to determine the base queryset to use for the lookup.
* Perform the object lookup based on the `lookup_field` and  `lookup_url_kwarg` attributes.
* Raise an `HTTP 404 Not Found` response if the instance does not exist.

You can perform custom object lookups by overriding this method.  For example:

    def get_object(self):
        """
        Custom object lookup that returns an instances based on both the
        'account' and 'slug' as provided in the URL keyword arguments.
        """
        queryset = self.get_queryset()
        account = self.kwargs['account']
        slug = self.kwargs['slug']
        return get_object_or_404(queryset, account=account, slug=slug)

#### get_form_class(self)

This method returns the class that should be used for generating forms.

The default behavior of this method is:

* If the `form_class` attribute is set, then return that.
* Otherwise fallback to returning an automatically generated form class based on the `model` attribute.
* If neither the `form_class` or `model` attributes are set then a configuration error will be raised.

You can customize how the form class for the view is determined by overriding this method.  For example:

    def get_form_class(self):
        is self.request.user.is_staff():
            return AccountForm
        return BasicAccountForm

#### get_form(self, data=None, files=None, **kwargs)

The method instantiates and returns the form instance that should be used for the view.

By default this method simply calls `get_form_class`, and then instantiates the class with the parameters that have been passed to it.

You can customize this method in order to supply additional arguments to the form class, add initial data, or other customizations.  For example:

    def get_form(self, data=None, files=None, **kwargs):
        kwargs['user'] = self.request.user
        return AccountForm(data, files, **kwargs)

#### get_paginate_by(self)

Returns an integer representing the number of items to display on each page of a paginated list.  Returns `None` if pagination is not enabled.

By default this method simply returns value of the `paginate_by` attribute.

You can override this method to provide more complex behavior.  For example, to allow the user to override the default pagination size using a query parameter in the URL, you might write something like this:

    def get_paginate_by(self):
        try:
            return int(self.request.GET('page_size', self.paginate_by))
        except ValueError:
            return None

#### get_paginator(self, queryset, page_size)

Given a queryset and a page size, returns a paginator instance to use for a paginated list view.

By default this method simply instantiates Django's standard `Paginator` class with the arugments passed.

If you need to customize how the paginator is instantiated you can override this method.  For example to ensure that the final page must always contain more than a single item, you could write something like this:

    def get_paginator(self, queryset, page_size):
        return Paginator(queryset, page_size, orphans=2)

#### paginate_queryset(self, queryset, page_size)

Given a queryset and a page size, this method should return a `page` instance representing the current page that should be displayed in a paginated list view.  You can override this method if you need to customize how the page object is determined, but the default behavior should typically be sufficient.

#### get_context_object_name(self, is_list=False)

This method returns a descriptive name that should be used when passing the object or object list as context to the template.  The name is used *in addition* to the default `'object'` or `'object_list'` context name.

The method takes a single parameter `is_list`, which is a boolean indicating if the context object should be named as representing a list of data, or if it should be named as representing a single object.

The default behavior of this method is:

* If the `context_object_name` attribute is set, then use that.
* Otherwise fallback to automatically using `<model_name>` or `<model_name>_list` based on the `model` attribute.
* If neither the `context_object_name` or `model` attributes are set, then only the standard `'object'` or `'object_list'` key will be used.  

#### get_context_data(self, **kwargs)

This method takes a set of keyword arguments supplied by the view and returns a dictionary to use as context when rendering the response template.

The default behavior of this method is to return a dictionary populated with the following keys:

* `view` - A reference to the view instance.
* `object` or `object_list` - The instance or queryset being operated on by the view.
* `<context_object_name>` - A more descriptive name for the instance or queryset as returned by `get_context_object_name`.
* Any additional keyword arguments supplied to the method.  In particular, the model editing views include the `form` context key. 

You can override the method either to add additional context data:

    def get_context_data(self, **kwargs):
		context = super(MyView, self).get_context_data(**kwargs)
        context['is_admin'] = self.request.user.is_admin
        return context

Or to specify the complete set of context data explicitly:

    def get_context_data(self, **kwargs):
        kwargs['view'] = self
        kwargs['is_admin'] = self.request.user.is_admin
        kwargs['account'] = self.object
        return kwargs

#### get_template_names(self)

Returns a list of strings that should be used for determining the template name when rendering the response.

The default behavior for this method is:

* If `template_name` is specified on the view then use that.
* Otherwise fallback to automatically generating a template name as `{app_label}/{model_name}{suffix}.html`, using the `model` attribute as set on the view.
* If neither of `template_name` or `model` attributes are set then raise a configuration error.

#### render_to_response(self, context)

Generates the response that should be returned by the view.  Takes a single argument which should be a dictionary of context data to use when rendering the response template.

The default behaviour of this method is to return an instance of Django's standard `TemplateResponse`.

You can override this method if you need to customize how the response is generated.  For example, to return a response with the `text/plain` content type instead of the standard `text/html`, you could write something like this:

    def render_to_response(context):
    	template = self.get_template_names()
        return TemplateResponse(self.request, template, context, content_type='text/plain')

You can also override this class in order to use a subclass of Django's standard `HttpResponse` or `TemplateResponse`.  For example, if you had a written a custom `JSONResponse` class, you might override the method like this:

    def render_to_response(context):
        return JSONResponse(self.request, context)

---

## ListView

A page representing a list of objects.  Optionally this may be present a paginated view onto the list.

The `object_list` attribute will be set on this view, and will typically be a queryset instance.

#### allow_empty

A boolean indicating if empty lists may be returned using the standard page template, or if they should cause an `HTTP 404 Not Found` response to be returned.  Defaults to `True`, indicating that empty pages should be allowed.

---

## DetailView

A page representing a single object.

The `object` attribute will be set on this view, and will typically be a model instance.

---

## CreateView

A page which allows the user to create objects.

If successfully created, then the `object` attribute will be set on this view.

#### success_url

The URL that should be used when redirecting after a successful form submission.

#### form_valid(self, form)

This method will be run when a valid form submission occurs, and should return a response object.  The default behavior is to return a redirect response as determined by calling `get_success_url()`.

#### form_invalid(self, form)

This method will be run when a valid form submission occurs, and should return a response object.  The default behavior is to return a `TemplateResponse` which renders the form errors.

#### get_success_url()

Returns the URL that should be used when redirecting after a successful form submission.  Defaults to returning the value of the `success_url` attribute if it is set, or will be the return value of calling `get_absolute_url()` on the object instance.

**Note**: If you are customizing the view behavior, we'd typically recommend overriding the `form_valid()` method directly rather than overriding `get_success_url()`, as it will result in simpler, more obvious flow control.

---

## UpdateView

A page which allows the user to update an existing object.

The `object` attribute will be set on this view.

#### success_url

The URL that should be used when redirecting after a successful form submission.

#### form_valid(self, form)

This method will be run when a valid form submission occurs, and should return a response object.  The default behavior is to save the updated object instance and then return a redirect response as determined by calling `get_success_url()`.

#### form_invalid(self, form)

This method will be run when a valid form submission occurs, and should return a response object.  The default behavior is to return a `TemplateResponse` which renders the form errors.

#### get_success_url()

Returns the URL that should be used when redirecting after a successful form submission.  Defaults to returning the value of the `success_url` attribute if it is set, or will be the return value of calling `get_absolute_url()` on the object instance.

**Note**: If you are customizing the view behavior, we'd typically recommend overriding the `form_valid()` method directly rather than overriding `get_success_url()`, as it will result in simpler, more obvious flow control.

---

## DeleteView

The `object` attribute will be set on this view.

#### success_url

The URL that should be used when redirecting after a successful form submission.

#### get_success_url()

Returns the URL that should be used when redirecting after a successful form submission.  Defaults to returning the value of the `success_url` attribute.

**Note**: If you are customizing the view behavior, we'd typically recommend overriding the `post()` methhod directly rather than overriding `get_success_url()`, as it will result in simpler, more obvious flow control.
