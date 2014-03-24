Mirrors REST API spec
=====================

Components
----------

CRUD Operations
^^^^^^^^^^^^^^^

Reading
"""""""

All information associated with a :py:class:`Component` object except for the
actual binary data itself.

It will return a JSON object with this format:

.. code:: json

 {
   'slug': '<slug-id>',
   'url': '<canonical URL of component>',
   'data_uri': '<canonical URL of component data>',
   'content_type': '<http content type>',
   'schema_name': '<name of schema>',
   'content': '<canonical URL of component data>',
   'metadata': {
     'title': '<title>',
     'description': 'description'
   },
   'attribute_1': component_1,
   'attribute_2': component_2,
   'attribute_n': component_n
 }

Attributes and their use are described in :ref:`attributes-section`.

A standard *404* response is returned if no :py:class:`Component` exists
with that slug.

.. note ::
   There are some standard metadata attributes which will be yound in more or
   less all :py:class:`Component` objects. ``title`` and ``description`` are
   two of them.

   One attribute, ``force_template`` allows a Component to force the front end
   to display it using a specified template.


Creating
""""""""

Creating new :py:class:`Component` objects is done through a ``PUT`` request
against ``/component/<slug-id>``, where slug-id is the (you guessed it!)
desired slug. The minimum expected data should look like this:

.. code:: json

 {
   'content_type': '<http content type>',
   'schema_name': '<name of component schema>',
   'metadata': { '<metadata field 1>': '<value>',
                 '<metadata field 2>': '<value>' }
 }

A successful operation will return a *201* response and the resource
representation of the :py:class:`Component` currently exists in the database,
as it would be appear if the user issued a ``GET /component/<slug-id>`` query.

If the slug provided is already in use, a *409* response will be returned.


Updating
""""""""

Changes to a :py:class:`Component` resource are made by submitting a ``PATCH``
query to ``/component/<slug-id>``. Multiple fields can be changed at once.
Attributes can not be altered at this end point, though. The expected data
takes the form

.. code:: json

 {
   '<field name>': '<new value>'
 }

Multiple fileds and new values can be specified in this dictionary.

After a successful update, a *200* HTTP response is returned along with the
current state of the :py:class:`Component`.


Deleting
""""""""
Deleting a :py:class:`Component` resource is achieved by submitting a
``DELETE`` query to ``/component/<slug-id>``.

After a successful delete, a *204* response is returned.


.. _attributes-section:

Attributes
^^^^^^^^^^

Simple named attributes which refer to a single :py:class:`Component` object
come in the following form:

.. code:: json

 {
   'parent': '<parent slug>',
   'name': '<attribute name>',
   'value': component_object
 }

However if an attribute contains a list of :py:class:`Component` objects the
returned value will come in *this* form:

.. code:: json

 {
   'parent': '<parent slug>',
   'name': '<attribute name>',
   'value': [ component_object_1,
              component_object_2,
              component_object_n ]
 }

Reading
"""""""

Reading an attribute is as simple as making a ``GET`` request to
``/component/<slug-id>/attribute/<attribute-name>``. If there is no attribute
by that name, a *404* response is returned.

Creating
""""""""

An attribute is created by making a ``PUT`` request to
``/component/<slug-id>/attribute/<attribute-name>`` with a JSON object of the
following form:

.. code:: json

 {
   'component': '<component slug>',
   'weight': 9999
 }

The value for the field ``component`` should be the slug of the Component you
wish to associate with the name. ``weight`` is optional and will default to
9999 in order to have the effect of appending the Component to the list.

If you issue multiple ``PUT`` requests using the name attribute name, but
different values for the weight, you will end up with an attribute that will
return an order list of :py:class:`Component` objects.

Successful requests will result in a *201* response along with the new resource
in correct JSON form.

.. note:: Attribute names have the same constraints as slugs.

Updating
""""""""

When you make a ``PUT`` to an attribute including a component that already
exists such as in this example:

.. code:: json

 {
   'component': 'my-fancy-component',
   'weight': 9999
 }

followed by another ``PUT`` request...

.. code:: json

 {
   'component': 'my-fancy-component',
   'weight': 150
 }

The attribute will be updated in place. This will work whether the attribute
has a single component in it or if it has a list.

.. warning:: To entirely replace the contents of an attribute, you must delete
             it first, and then re-create it.

Deleting
""""""""

To delete **all** of the contents of an attribute, make a ``DELETE`` request to
``/component/<slug-id>/attribute/<attribute-name>``. If you want to delete a
specific ordered element in an attribute, make a ``DELETE`` request to
``/component/<slug-id>/attribute/<attribute-name>/<index>``, where index is the
location of the element in that list.

Attempting to delete a nonexistent attribute or a nonexistent attribute element
will result in a *404* response.

A successful delete will return a *204* response.


Data
^^^^

Reading
"""""""

To get at the data of a :py:class:`Component`, issue a ``GET`` query to
``/component/<slug-id>/data``. The data will be returned with a *200* response
code, and the content type header set appropriately (eg ``'image/png'`` if the
data represented by the :py:class:`Component` is a png file).

If no data exists yet, a *404* response will be returned.

Creating/Updating
"""""""""""""""""

Both creating and updating the data for a :py:class:`Component` is done by the
same method. Issuing a ``PUT`` query to ``/component/<slug-id>/data`` where the
request body is the data itself.


Locking
^^^^^^^

To prevent simultaneous editing of the same component, creating conflicting
changes, it is possible to lock them to prevent changes being made by anybody
other than the user who locked it initially.

The locks themselves can be of any period of time, but they default to 30
minutes long.

Checking lock status
""""""""""""""""""""

To see whether or not a component is currently locked, make a ``GET`` request
to ``/component/<slug-id>/lock``, which will result in a JSON object like the
following if the component is locked:

.. code:: json

 {
   'locked': true,
   'locked_by': '<username of locker>',
   'locked_at': '<timestamp of creation of lock>',
   'lock_ends_at': '<timestamp of creation of lock>',
 }

The response will also come along with a *200* status code.

If the component is unlocked, the response will be a *404*.


Making a lock
"""""""""""""

To create a lock make a ``PUT`` to ``/component/<slug-id>/lock`` with JSON data in
the following format:

.. code:: json

  {
    'locked': true,
    'lock_duration': duration_in_minutes
  }


.. note:: ``lock_duration`` is optional and the duration will default to 30
          minutes when not specified.

.. note:: The currently logged in user account will be recorded as having made
          the lock in the database.

If the lock is successful, you will receive a response with a *201* status code
along with data that matches what you would get if you issued a ``GET``
statement to ``/component/<slug-id>/lock``.

If there is already a lock in place then you will get a response with a *409*
response.

Breaking a lock
"""""""""""""""

Sometimes you need to break the lock. Make a ``DELETE`` request to
``/component/<slug-id>/lock`` and the current lock will be removed. You will
receive a *204* response if the lock is successfully broken. If there is no
lock, you will get a *404* response.


Scheduler
---------

Reservations
^^^^^^^^^^^^

Creating a Reservation
""""""""""""""""""""""

A component can be scheduled for publishing by issuing a ``POST`` request to
``/scheduler/`` with the slug and the time that it should be published at in
the format of an ISO timestamp.

.. code:: json
 
 {
   'slug': '<slug name>',
   'datetime': '<timestamp>'
 }

If the slug or timestamp is invalid, a *400* response will be returned.

A successful scheduling will result in a :py:class:`Reservation` object being
returned with a *200* code.

.. code:: json

 {
   'slug': '<slug name>',
   'datetime': '<timestamp>',
   'reservation': '<uuid>'
 }

Changing a Reservation
""""""""""""""""""""""

A ``PATCH`` request made to ``/scheduler/<reservation id>`` can be used to
update the time when a component will be published, but only that. The response
will look like this:

.. code:: json

 {
   'slug': '<slug name>',
   'datetime': '<timestamp>',
   'reservation': '<uuid>'
 }

and come with a *200* response code.

Deleting a Reservation
""""""""""""""""""""""

Issue a ``DELETE`` request to ``/scheduler/<reservation id>``. Status code
*204* will be returned.

Getting the Schedule
^^^^^^^^^^^^^^^^^^^^

Whenever the schedule is queried, the result is a list of
:py:class:`Reservation` objects in JSON format.

For a Day
"""""""""

Issue a ``GET`` request to ``/scheduler/?date=<day>``.

For a Range
"""""""""""

Issue a ``GET`` request to ``/scheduler/?start=<day>&end=<day>``, where the day is the
date you wish to check.

