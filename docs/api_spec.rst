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
     'attribute_1': '<component>',
     ...
 }

Attributes and their use are described in :ref:`attributes-section`.

A standard *404* response is returned if no :py:class:`Component` exists
with that slug.


Creating
""""""""

Creating new :py:class:`Component` objects is done through a ``POST`` query
against ``/component/``, where slug-id is the (you guessed it!) desired
slug for the ``Component``. The minimum expected data should look like this:

.. code:: json

 {
     'slug': '<component slug>',
     'content_type': '<http content type>',
     'schema_name': '<name of component schema>',
     'metadata': { <metadata object> }
 }

A successful operation will return a *201* response and the resource
representation of the :py:class:`Component` currently exists in the database,
as it would be appear if the user issued a ``GET /component/<slug>`` query.


Updating
""""""""

Changes to a :py:class:`Component` resource are made by submitting a ``PATCH``
query to ``/component/<slug-id>``. Multiple fields can be changed at once.
Attributes can not be altered at this end point, though. The expected data
takes the form

.. code:: json
 {
     '<field name>': <new value>,
     ...
 }

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

Reading
"""""""

Creating
""""""""

Updating
""""""""

De

Data
^^^^

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
