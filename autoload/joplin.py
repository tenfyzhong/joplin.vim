#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import inspect
import time
import os
import json


class Node(object):
    """base node"""
    def __init__(self, **kwargs):
        """TODO: to be defined. """
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
        """TODO: to be defined. """
        super().__init__(**kwargs)
        self.parent_id = kwargs.get('parent_id', '')
        self.open_ = kwargs.get('open_', False)

    @classmethod
    def path(cls):
        return 'folders'


class ResourceNode(Node):
    """Node for resource"""
    def __init__(self, **kwargs):
        """TODO: to be defined. """
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
        """TODO: to be defined. """
        super().__init__(**kwargs)
        self.parent_id = kwargs.get('parent_id', '')

    @classmethod
    def path(cls):
        return 'tags'


class Joplin(object):
    """Joplin operation"""
    def __init__(self, token, host='127.0.0.1', port=41184):
        self.token = token
        self.host = host
        self.port = port
        self.base_url = 'http://%s:%d' % (host, port)

    def ping(self):
        """Testing if the service is available
        :returns: bool

        """
        url = self.base_url + 'ping'
        r = requests.get(url)
        return r.status_code == 200 and r.text == 'JoplinClipperServer'

    def get_all(self, cls, page=1, order_by='updated_time', order_dir='DESC'):
        """Gets cls' objects

        :cls: the object type
        :page: the page to get
        :returns: ojbects and has_more if success else None

        """
        url = '%s/%s?token=%s&order_by=%s&order_dir=%s&page=%d' % (
            self.base_url, cls.path(), self.token, order_by, order_dir, page)
        print('url', url)
        r = requests.get(url)
        if r.status_code != 200:
            print(r.status_code, r.text)
            return None
        json = r.json()
        items = json['items']
        has_more = json['has_more']
        objects = list([cls(**item) for item in items])
        return objects, has_more

    def get(self, cls, id):
        """Get cls' object

        :cls: the object type
        :id: the id to get
        :returns: object if success else None

        """
        fields = ','.join(cls().fields())
        url = '%s/%s/%s?token=%s&fields=%s' % (self.base_url, cls.path(), id,
                                               self.token, fields)
        r = requests.get(url)
        if r.status_code != 200:
            print(r.status_code, r.text)
            return None
        json = r.json()
        return cls(**json)

    def post(self, o):
        """Create a new object

        :o: the object to create
        :returns: the created object

        """
        url = '%s/%s?token=%s' % (self.base_url, o.path(), self.token)
        r = requests.post(url, json=o.dict())
        if r.status_code != 200:
            print(r.status_code, r.text)
            return None
        return o.new(**r.json())

    def put(self, o):
        """Sets the properties of the object

        :o: the object to update
        :returns: new object
        """
        url = '%s/%s/%s?token=%s' % (self.base_url, o.path(), o.id, self.token)
        r = requests.put(url, json=o.dict())
        if r.status_code != 200:
            print(r.status_code, r.text)
            return None
        return o.new(**r.json())

    def delete(self, cls, id):
        """delete object with id

        :cls: the object type
        :arg1: the id to delete
        :returns:

        """
        url = '%s/%s/%s?token=%s' % (self.base_url, cls.path(), id, self.token)
        r = requests.delete(url)
        if r.status_code != 200:
            print(r.status_code, r.text)

    def get_note_tags(self, id, page=1):
        """Gets all the tags attached to this note

        :id: note's id
        :returns: TagNodes, has_more

        """
        url = '%s/notes/%s/tags?token=%s&page=%d' % (self.base_url, id,
                                                     self.token, page)
        r = requests.get(url)
        if r.status_code != 200:
            return None
        json = r.json()
        tags = list([TagNode(**item) for item in json['items']])
        return tags, json['has_more']

    def get_note_resources(self, id, page=1):
        """Gets all the resources attached to this note

        :id: note's id
        :returns: ResourceNodes

        """
        fields = ','.join(ResourceNode().fields())
        url = '%s/notes/%s/resources?token=%s&fields=%s&page=%d' % (
            self.base_url, id, self.token, fields, page)
        r = requests.get(url)
        if r.status_code != 200:
            return None
        json = r.json()
        resources = list([ResourceNode(**item) for item in json['items']])
        return resources, json['has_more']

    def get_folder_notes(self, id, page=1):
        """Gets all the notes inside this folder

        :id: folder's id
        :returns: NoteNodes

        """
        url = '%s/folders/%s/notes?token=%s&page=%d' % (self.base_url, id,
                                                        self.token, page)
        r = requests.get(url)
        if r.status_code != 200:
            print(r.status_code, r.text)
            return None
        json = r.json()
        items = json['items']
        has_more = json['has_more']
        notes = list([NoteNode(**item) for item in items])
        return notes, has_more

    def get_resource_file(self, id):
        """Gets the actual file associated with this resource

        :id: resource's id
        :returns: TODO

        """
        url = '%s/resources/%s/file?token=%s' % (self.base_url, id, self.token)
        r = requests.get(url)
        if r.status_code != 200:
            print(r.status_code, r.text)
            return None
        return r.text

    def get_resource_notes(self,
                           id,
                           page=1,
                           order_by='updated_time',
                           order_dir='DESC'):
        """Gets the notes associated with the resource with id

        :id: resource's id
        :returns: notes' id

        """
        url = '%s/resources/%s/notes?token=%s&order_by=%s&order_dir=%s&page=%d' % (
            self.base_url, id, self.token, order_by, order_dir, page)
        r = requests.get(url)
        if r.status_code != 200:
            print(r.status_code, r.text)
            return None
        json = r.json()
        items = json['items']
        has_more = json['has_more']
        notes = list([NoteNode(**item) for item in items])
        return notes, has_more

    def post_resource(self, filename, resource):
        """Creates a new resource

        :resource: the resource to create
        :returns: TODO

        """
        url = '%s/resources?token=%s' % (self.base_url, self.token)
        payload = {
            'props': json.dumps(resource.dict()),
        }
        r = requests.post(url,
                          files={'data': open(filename, 'rb')},
                          data=payload)
        if r.status_code != 200:
            print(r.status_code, r.text)
            return None
        j = r.json()
        return ResourceNode(**j)

    def put_resource(self, resource):
        """Sets the properties of the resource with id

        :resource: the resource to update
        :returns: TODO

        """
        url = '%s/resources/%s?token=%s' % (self.base_url, resource.id,
                                            self.token)
        r = requests.put(url, json=resource.dict())
        if not r.ok:
            print(r.status_code, r.text)
            return None
        return ResourceNode(**r.json())

    def get_tag_notes(self,
                      id,
                      page=1,
                      order_by='updated_time',
                      order_dir='DESC'):
        """Gets all the notes with this tag

        :id: tag's id
        :returns: None

        """
        url = '%s/tags/%s/notes?token=%s&order_by=%s&order_dir=%s&page=%d' % (
            self.base_url, id, self.token, order_by, order_dir, page)
        r = requests.get(url)
        if r.status_code != 200:
            print(r.status_code, r.text)
            return None
        json = r.json()
        items = json['items']
        has_more = json['has_more']
        notes = list([NoteNode(**item) for item in items])
        return notes, has_more

    def post_tag_note(self, id, note_id):
        """Post a note to this endpoint to add the tag to the note.

        :id: tag id
        :note_id: note id
        :returns: None

        """
        url = '%s/tags/%s/notes?token=%s' % (self.base_url, id, self.token)
        payload = {'id': note_id}
        r = requests.post(url, json=payload)
        if r.status_code != 200:
            print(r.status_code, r.text)

    def delete_tag_note(self, id, note_id):
        """Remove the tag from the note

        :id: tag id
        :note_id: note_id
        :returns: None

        """
        url = '%s/tags/%s/notes/%s?token=%s' % (self.base_url, id, note_id,
                                                self.token)
        r = requests.delete(url)
        if r.status_code != 200:
            print(r.status_code, r.text)
