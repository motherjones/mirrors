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
     'slug': '<slug>',
     'content_type': '<http content type>',
     'schema_name': '<name of schema>',
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


Creating
""""""""

Creating new :py:class:`Component` objects is done through a ``PUT`` request
against ``/component/<slug-id>``, where slug-id is the (you guessed it!) desired
slug. The minimum expected data should look like this:

.. code:: json

 {
     'content_type': '<http content type>',
     'schema_name': '<name of component schema>',
     'metadata': { '<metadata field 1>': '<value>',
                   '<metadata field 1>': '<value>' }
 }

A successful operation will return a *201* response and the resource
representation of the :py:class:`Component` currently exists in the database,
as it would be appear if the user issued a ``GET /component/<slug>`` query.

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
``DELETE`` query to ``/component/<slug>``.

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
     'weight': 0
 }

The value for the field ``component`` should be the slug of the component you
wish to associate with the name. ``weight`` is optional and will default to 0.

If you issue multiple ``PUT`` requests using the name attribute name, but
different values for the weight, you will end up with an attribute that will
return an order list of :py:class:`Component` objects.

Successful requests will result in a *201* response along with the new resource
in correct JSON form.

.. note:: Attribute names have the same constraints as slugs.

Updating
""""""""

You can't update an attribute. Delete it, and then re-create it with the new
data.

Deleting
""""""""

To delete **all** of the contents of an attribute, make a ``DELETE`` request to
``/component/<slug-id>/attribute/<attribute-name>``. If you want to delete a
specific ordered element in an attribute, make a ``DELETE`` request to
``/component/<slug-id>/attribute/<attribute-name>/<index>``, where index is the
location of the element in that list.

Attempting to delete a nonexistent attribute or a nonexistent attribute element
will result in a *404* response.

A successful delete will return a *204* responsen.


Data
^^^^

Reading
"""""""

To get at the data of a :py:class:`Component`, issue a ``GET`` query to
``/component/<slug>/data``. The data will be returned with a *200* response
code, and the content type header set appropriately (eg ``'image/png'`` if the data
represented by the :py:class:`Component` is a png file).

If no data exists yet, a *404* response will be returned.

Creating/Updating
"""""""""""""""""

Both creating and updating the data for a :py:class:`Component` is done by the
same method. Issuing a ``PUT`` query to ``/component/<slug>/data`` where the
request body is the data itself.

URLs
====

.. code::

 /content                             GET, PUT, PATCH, DELETE do nothing
                                      POST creates new Content item

 /content/:slug-id                    GET Content object data as JSON
                                      PUT Create new Content object with name :slug-id as the slug
                                      PATCH, POST, and DELETE work as normal

 /content/:slug-id/data               GET retrieves the current version of the actual data in the Content object
                                      PUT, POST update the current data, adding a new revision

 /content/:slug-id/rev                GET retrieves revision information and returns it as JSON

 /content/:slug-id/rev/:rev-id        GET retrieves the data in the Content object from that particular revision

 /content/:slug-id/attribute          GET retrieve a list of all attribute names for that Content object

 /content/:slug-id/attribute/:attr-id PUT Create a new attribute with the name :attr-id
                                      GET equivalent to GETting the actual content referenced by the attribute
                                      PUT, PATCH, and DELETE work as normal

 /content/:slug-id/member             POST Create a new member

 /content/:slug-id/member/:index      PUT create or replace a member
                                      GET get member info
                                      DELETE, PATCH work as normal (use PATCH to move elements)
