#include <Python.h>
#include <signal.h>

#if PY_MAJOR_VERSION >= 3
#define PyInt_AsLong(x) (PyLong_AsLong((x)))
#endif

static sigset_t newmask, oldmask, pendmask;


static PyObject*
save_mask(PyObject *self, PyObject *arg)
{
    int idx, size;
    PyObject *list, *item;

    if (!PyArg_ParseTuple(arg, "O", &list)) {
        return NULL;
    }

    sigemptyset(&newmask);
    size = PySequence_Length(list);
    for (idx = 0; idx < size; ++idx) {
        item = PySequence_GetItem(list, idx);
        sigaddset(&newmask, PyInt_AsLong(item));
    }

    if (sigprocmask(SIG_BLOCK, &newmask, &oldmask) != 0) {
        Py_Exit(1);
    }

    Py_RETURN_NONE;
}

static PyObject*
pending_and_restore(PyObject *self, PyObject *arg)
{
    if (sigpending(&pendmask) != 0) {
        Py_Exit(1);
    }
    if (sigprocmask(SIG_SETMASK, &oldmask, NULL) != 0) {
        Py_Exit(1);
    }

    Py_RETURN_NONE;
}


static PyMethodDef methods[] = {
    {"save_mask", save_mask, METH_VARARGS, ""},
    {"pending_and_restore", pending_and_restore, METH_VARARGS, ""},
    {NULL, NULL, 0, NULL},
};

#if PY_MAJOR_VERSION >= 3
static struct PyModuleDef sigpendingmodule = {
    PyModuleDef_HEAD_INIT,
    "_sigpending",
    NULL,
    -1,
    methods
};

PyMODINIT_FUNC
PyInit__sigpending(void)
{
    return PyModule_Create(&sigpendingmodule);
}
#else
PyMODINIT_FUNC
init_sigpending()
{
    Py_InitModule("_sigpending", methods);
}
#endif
