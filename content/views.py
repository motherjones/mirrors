from django.shortcuts import render


def get_content(request, slug):
    raise NotImplementedError


def get_content_data(request, slug):
    raise NotImplementedError


def get_content_revision(request, slug, revision):
    raise NotImplementedError


def get_content_revision_data(request, slug, revision):
    raise NotImplementedError
