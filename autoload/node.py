#!/usr/bin/env python
# -*- coding: utf-8 -*-


def factory_node(**kwargs):
    if 'type_' not in kwargs:
        return None
    type_ = kwargs['type_']
    if type_ == 1:
        return NoteNode(**kwargs)
    elif type_ == 2:
        return FolderNode(**kwargs)
    elif type_ == 4:
        return ResourceNode(**kwargs)
    elif type_ == 5:
        return TagNode(**kwargs)
    else:
        return None


class Node(object):
    """base node"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', '')
        self.title = kwargs.get('title', '')
        self.created_time = kwargs.get('created_time', 0)
        self.updated_time = kwargs.get('updated_time', 0)
        self.user_created_time = kwargs.get('user_created_time', 0)
        self.user_updated_time = kwargs.get('user_updated_time', 0)
        self.is_shared = kwargs.get('is_shared', 0)
        self.encryption_cipher_text = kwargs.get('encryption_cipher_text', '')
        self.encryption_applied = kwargs.get('encryption_applied', 0)
        self.type_ = kwargs.get('type_', 0)

    def fields(self):
        return [v for v in vars(self).keys() if not v.endswith('_')]

    def __str__(self):
        return str(self.dict())

    def __repr__(self):
        return str(self.dict())

    def dict(self):
        return dict({k: v for k, v in vars(self).items()})

    def new(self, **kwargs):
        o = self.__class__(**kwargs)
        self = o
        return self


class NoteNode(Node):
    """Node for note"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parent_id = kwargs.get('parent_id', '')
        self.body = kwargs.get('body', '')
        self.is_conflict = kwargs.get('is_conflict', 0)
        self.latitude = kwargs.get('latitude', 0)
        self.longitude = kwargs.get('longitude', 0)
        self.altitude = kwargs.get('altitude', 0)
        self.author = kwargs.get('author', '')
        self.source_url = kwargs.get('source_url', '')
        self.is_todo = kwargs.get('is_todo', 0)
        self.todo_due = kwargs.get('todo_due', 0)
        self.todo_completed = kwargs.get('todo_completed', 0)
        self.source = kwargs.get('source', '')
        self.source_application = kwargs.get('source_application', '')
        self.application_data = kwargs.get('application_data', '')
        self.order = kwargs.get('order', 0)
        self.markup_language = kwargs.get('markup_language', 0)

    @classmethod
    def path(cls):
        return 'notes'


class FolderNode(Node):
    """Node for Folder"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parent_id = kwargs.get('parent_id', '')
        self.open_ = kwargs.get('open_', False)

    @classmethod
    def path(cls):
        return 'folders'


class ResourceNode(Node):
    """Node for resource"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mime = kwargs.get('mime', '')
        self.filename = kwargs.get('filename', '')
        self.file_extension = kwargs.get('file_extension', '')
        self.size = kwargs.get('size', -1)

    @classmethod
    def path(cls):
        return 'resources'


class TagNode(Node):
    """Node for tag"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parent_id = kwargs.get('parent_id', '')

    @classmethod
    def path(cls):
        return 'tags'
