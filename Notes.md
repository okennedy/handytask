# Notes

### Setting up LibHandy
As of writing, PureOS desktop packages only LibHandy v0, while the current version is 1.  That means you will, in all likelihood, need to build and compile it yourself.  The repository, with instructions is [here](https://source.puri.sm/Librem5/libhandy).  

It's worth noting that the LibHandy build installer (i.e., `ninja -C _build install`) sets up the libraries, but does not seem to configure all of the GTK metadata properly.  The LibHandy build script does provide a convenient script to run a command with relevant environment variables set (`libhandy/_build/run` if you follow the suggested build instructions).  As a convenience, I found it useful to set the same environment variables in my .profile.  e.g., (make sure to change the first two path variables appropriately if you use this code yourself:

```
LIBHANDY_BUILDDIR='/home/okennedy/Documents/Lib/libhandy/_build'
LIBHANDY_SRCDIR='/home/okennedy/Documents/Lib/libhandy'

export GLADE_CATALOG_SEARCH_PATH="${LIBHANDY_SRCDIR}/glade/:${GLADE_CATALOG_SEARCH_PATH}"
export GLADE_MODULE_SEARCH_PATH="${LIBHANDY_BUILDDIR}/glade:${GLADE_MODULE_SEARCH_PATH}"
export GI_TYPELIB_PATH="${LIBHANDY_BUILDDIR}/src:$GI_TYPELIB_PATH"
export LD_LIBRARY_PATH="${LIBHANDY_BUILDDIR}/src:${LIBHANDY_BUILDDIR}/glade:$LD_LIBRARY_PATH"
export PKG_CONFIG_PATH="${LIBHANDY_BUILDDIR}/src:$PKG_CONFIG_PATH"
```

### Python Docs
- [Python GTK Documentation](https://python-gtk-3-tutorial.readthedocs.io/)
- [PyGObject Docs](https://pygobject.readthedocs.io/en/latest/)
- [TaskLib Documentation](https://tasklib.readthedocs.io/)
- [LibHandy Tutorial](https://tuxphones.com/tutorial-developing-responsive-linux-smartphone-apps-libhandy-gtk-part-1/)
- [LibHandy Manual](https://developer.puri.sm/projects/libhandy/unstable/index.html)
