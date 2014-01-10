# Frequently Asked Questions

## Usage

### Won't I lose functionality or flexiblity?

No.  Everything you can do with Django's standard class based views you can also do with `django-vanilla-views`.  The migration guides cover all the bits of API that have been removed, and explain how you can easily achieve the same functionality with vanilla views.

### Can I still use mixin classes?

Sure.  The `django-vanilla-views` package doesn't happen to use mixin classes, but there's no reason you shouldn't do so in your own code.  Overuse of mixin classes can make for poor style, but when used in moderation they're a powerful and useful tool.

### I've already learnt Django's GCBVs, is this worth my time?

Absolutely.  The API presented by `django-vanilla-views` is pretty simple so it shouldn't take you long to get up and running with it.  The generic class based views are the bread and butter of our web sites, and the small investment in time you'll make learning `django-vanilla-views` should pay of quickly as you'll be using simpler, more obvious views throughout.

### Is it stable?

The `django-vanilla-views` package has issued a 1.0 release and now has a [formal deprecation policy][deprecation-policy].  You should be free to use it knowing that package upgrades will be fully documented and will not break API compatibility between releases.  We also have 100% code coverage and fully intend to quickly deal with any issues reported.

---

## Design

### Isn't a mixin-less style less DRY?

Actually not really.  The base views and the model views do share some common implementation, but there's only a very small amount of duplication.

It's also worth noting that Django's existing class based views also include duplication despite being implemented using a mixin style.  For example, both `SingleObjectMixin` and `MultipleObjectMixin` implement a functionally identical `get_queryset()` method.

### What about seperation of concerns?

The base classes used by vanilla views include a small core set of functionality.  In the author's opinion there's no real practical issue introduced here, and the design trade-off should favor simplicity of implementation.

It's also worth noting that Django's existing class based views also include unused methods in base classes despite being implemented using a mixin style.  For example, `CreateView` inherits from `SingleObjectMixin` and includes `get_object()` which is never used.

[deprecation-policy]: release-notes.md