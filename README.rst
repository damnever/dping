A simple ping program write in Python.
==================================

.. image:: https://github.com/Damnever/dping/blob/master/view.png
    :target: https://raw.githubusercontent.com/Damnever/pigar/master/view.png

Tested it on Ubuntu 15.04(3.19.0-34-generic).

Get started
----------

Install it from GitHub with ``pip``, you must use **root permission**: ::

    sudo pip install git+https://github.com/Damnever/dping.git@master

Run it, **root permission** is also required, no optional arguments: ::

    sudo dping example-site.com

That's it. You can learn more from the source code.

About the C extension
-------------------

The reason to write the C extension is I want to block ``SIGINT`` when a ping request-response cycle is not finished. And, the Python signal module is weak, it can not support for pending a signal.

You can consider the situation like this: it sends a ICMP packet to destination, and it increases transmitted counter value, it waiting for receiving a ICMP response packet, then it increases received counter value. If it sends a packet then you enter ``Ctrl+C``, then the program will be interrupted, it will loss the ICMP response packet and received counter value, so the loss rate is not exactly incorrect.

Why don't I just throw the last counter value away? Because I do not wanna do this, I want to learn more and ...

The C extension is usefull. For example:

.. code:: python

    import time
    import signal

    from dping.sigpending import sigpending


    def main():
        try:
            with sigpending(signal.SIGINT):
                print('Doing sth.')
                for i in range(1, 6):
                    time.sleep(1)
                    print('{0} sec passed!'.format(i))
                print('Done.')
        except KeyboardInterrupt:
            print('\nInterruped')

    if __name__ == '__main__':
        main()

Ouput(``^C`` is ``Ctrl+C``): ::

    Doing sth.
    1 sec passed!
    ^C2 sec passed!
    3 sec passed!
    4 sec passed!
    5 sec passed!
    Done.

    Interruped

LICENSE
------

`The BSD 3-Clause License <https://github.com/Damnever/dping/blob/master/LICENSE>`_
