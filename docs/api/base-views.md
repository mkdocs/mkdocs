<a class="github" href="views.py"></a>

# Base Views

The base views provide a simple set of generic views for working with Django querysets and model instances.

They replicate the functionality of Django's existing `TemplateView` and `FormView` but present a simpler API and implementation.  Django's standard `RedirectView` is also included for completeness.

	View --+-------------------- RedirectView
	       |
	       +-- GenericView --+-- TemplateView
	                         |
	                         +-- FormView

---

## GenericView

The `GenericView` class is used as the base class for both `TemplateView` and `FormView`, and provides methods allowing for a default set of simple template and form actions.

### Attributes

#### form_class

The form class that should be used for edit views.  If you are using `FormView`, or your own custom view that calls `get_form()`, then you should either set this attribute, or override one of the form generation methods.  Defaults to `None`.

#### template_name

A string representing the template name that should be used when rendering the response content.  You should either set this attribute or override one of the methods controlling how responses are rendered.  Defaults to `None`.

### Methods

#### get_form_class(self)

This method returns the class that should be used for generating forms.

The default behavior for this method is:

* If `form_class` is specified on the view then use that.
* Otherwise raise a configuration error.

You can customize how the form class for the view is determined by overriding this method.  For example:

    def get_form_class(self):
        is self.request.user.is_staff():
            return AccountForm
        return BasicAccountForm

#### get_form(self, data=None, files=None, **kwargs)

The method instantiates and returns the form instance that should be used for the view.

By default this method simply calls `get_form_class()`, and then instantiates the class with the parameters that have been passed to it.

You can customize this method in order to supply additional arguments to the form class, add initial data, or other customizations.  For example:

    def get_form(self, data=None, files=None, **kwargs):
        kwargs['user'] = self.request.user
        return AccountForm(data, files, **kwargs) 

#### get_context_data(self, **kwargs)

This method takes a set of keyword arguments supplied by the view and returns a dictionary to use as context when rendering the response template.

The default behavior of this method is to return a dictionary populated with the following keys:

* `view` - A reference to the view instance.
* Any additional keyword arguments supplied to the method.  In particular, `FormView` includes the `form` context key. 

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
* Otherwise raise a configuration error.

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

## RedirectView

For completeness, Django's standard `RedirectView` is included in the `django-vanilla-views` package.  The class does not have any implementation or API differences from Django's implementation.

You should [refer to the Django documentation][redirect-view-docs] for further information.

---

## TemplateView

A page which simply returns a template response.

The context passed to the response template will be:

* `view` - The view instance.

---

## FormView

A page which allows the user to preview and submit a form.

The context passed to the response template will be:

* `view` - The view instance.
* `form` - The form instance.

#### success_url

The URL that should be used when redirecting after a successful form submission.

#### form_valid(self, form)

This method will be run when a valid form submission occurs, and should return a response object.  The default behavior is to return a redirect response as determined by calling `get_success_url()`.

#### form_invalid(self, form)

This method will be run when a valid form submission occurs, and should return a response object.  The default behavior is to return a `TemplateResponse` which renders the form errors.


#### get_success_url()

Returns the URL that should be used when redirecting after a successful form submission.  Defaults to returning the value of the `success_url` attribute.

**Note**: If you are customizing the view behavior, we'd typically recommend overriding the `form_valid()` method directly rather than overriding `get_success_url()`, as it will result in simpler, more obvious flow control.

[redirect-view-docs]: https://docs.djangoproject.com/en/dev/ref/class-based-views/base/#redirectview
