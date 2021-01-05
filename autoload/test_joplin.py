#!/usr/bin/env python
# -*- coding: utf-8 -*-
from joplin import *


def get_folders(j):
    folders = []
    page = 1
    has_more = True
    while has_more:
        cur, has_more = j.get_all(FolderNode, page)
        page += 1
        folders += cur
    return folders


def get_notes(j):
    notes = []
    page = 1
    has_more = True
    while has_more:
        cur, has_more = j.get_all(NoteNode, page)
        page += 1
        notes += cur
    return notes


def get_tags(j):
    tags = []
    page = 1
    has_more = True
    while has_more:
        cur, has_more = j.get_all(TagNode, page)
        page += 1
        tags += cur
    return tags


def create_folder(j, new_folder_title):
    new_folder = FolderNode(title=new_folder_title)
    new_folder = j.post(new_folder)
    assert new_folder.id != ''
    assert new_folder.parent_id == ''
    assert new_folder.title == new_folder_title
    folders = get_folders(j)
    matched = list(filter(lambda folder: folder.id == new_folder.id, folders))
    assert len(matched) != 0
    assert matched[0].title == new_folder_title
    return new_folder


def update_folder(j, folder):
    new_title = folder.title + ' modified'
    id = folder.id
    folder.title = new_title
    j.put(folder)
    folders = get_folders(j)
    matched = list(filter(lambda f: f.id == folder.id, folders))
    assert len(matched) != 0
    assert matched[0].title == new_title
    assert folder.title == new_title
    return folder


def delete_folder(j, id):
    j.delete(FolderNode, id)
    folders = get_folders(j)
    matched = list(filter(lambda f: f.id == id, folders))
    assert len(matched) == 0
    get = j.get(FolderNode, id)
    assert get is None


def create_note(j, folder_id):
    title = 'hello ' + str(time.time())
    body = 'world'
    note = NoteNode(title=title, body=body, parent_id=folder_id)
    note = j.post(note)
    assert note.id != ''
    assert note.parent_id == folder_id
    assert note.title == title
    assert note.body == body
    get = j.get(NoteNode, note.id)
    assert get.id == note.id
    assert get.parent_id == note.parent_id
    assert get.title == note.title
    assert get.body == note.body
    return note


def udpate_note(j, note):
    new_body = note.body + ' modified'
    note.body = new_body
    note = j.put(note)
    assert new_body == note.body
    get = j.get(NoteNode, note.id)
    assert get.id == note.id
    assert get.parent_id == note.parent_id
    assert get.title == note.title
    assert get.body == note.body
    return note


def create_tag(j):
    tags = get_tags(j)
    title = 'tag_' + str(time.time())
    matched = list(filter(lambda tag: tag.title == title, tags))
    assert len(matched) == 0
    tag = TagNode(title=title)
    tag = j.post(tag)
    assert tag.id != ''
    assert tag.title == title
    get = j.get(TagNode, tag.id)
    assert get.id == tag.id
    assert get.title == tag.title
    return tag


def update_tag(j, tag):
    new_title = tag.title + ' modified'
    tag.title = new_title
    tag = j.put(tag)
    assert tag.title == new_title
    get = j.get(TagNode, tag.id)
    assert get.id == tag.id
    assert get.title == tag.title
    return tag


def note_tags(j, node, tag):
    tags, has_more = j.get_note_tags(node.id)
    assert has_more is False
    assert len(tags) == 1
    assert tags[0].id == tag.id
    assert tags[0].title == tag.title


def tag_notes(j, tag, node):
    nodes, has_more = j.get_tag_notes(tag.id)
    assert has_more is False
    assert len(nodes) == 1
    assert nodes[0].id == node.id
    assert nodes[0].title == node.title


def delete_tag_note(j, tag, node):
    j.delete_tag_note(tag.id, node.id)
    tags, has_more = j.get_note_tags(node.id)
    assert has_more is False
    assert len(tags) == 0
    notes, has_more = j.get_tag_notes(tag.id)
    assert has_more is False
    assert len(notes) == 0


def delete_tag(j, tag):
    j.delete(TagNode, tag.id)
    tag = j.get(TagNode, tag.id)
    assert tag is None


def delete_note(j, note):
    j.delete(NoteNode, note.id)
    note = j.get(NoteNode, note.id)
    assert note is None


def create_resource(j, filename):
    title = filename + str(time.time())
    resource = ResourceNode(title=title)
    resource = j.post_resource(filename, resource)
    assert resource.id != ''
    assert resource.mime != ''
    assert resource.size > 0
    assert resource.title == title
    return resource


def update_resouce(j, resource):
    new_title = resource.title + ' modified'
    resource.title = new_title
    resource = j.put_resource(resource)
    assert resource.id != ''
    assert resource.title == new_title
    return resource


def get_resrouces(j):
    resources = []
    page = 1
    has_more = True
    while has_more:
        cur, has_more = j.get_all(ResourceNode, page)
        page += 1
        resources += cur
    return resources


def resource_file(j, id):
    data = j.get_resource_file(id)
    assert len(data) > 0


def folder_notes(j, id, note):
    notes, has_more = j.get_folder_notes(id)
    assert has_more is False
    assert len(notes) == 1
    assert notes[0].id == note.id


def test_joplin():
    # get token from environment
    token = os.environ['JOPLIN_TOKEN']
    assert token != ''
    j = Joplin(token)
    # get folders
    folders = get_folders(j)

    folder_titles = list([folder.title for folder in folders])
    new_folder_title = 'test title ' + str(time.time())
    while new_folder_title in folder_titles:
        new_folder_title = 'test title ' + str(time.time())

    # create folder
    folder = create_folder(j, new_folder_title)

    # update folder
    folder = update_folder(j, folder)

    # get folder
    get = j.get(FolderNode, folder.id)
    assert get is not None
    assert get.id == folder.id

    # create note
    note = create_note(j, folder.id)

    folder_notes(j, folder.id, note)

    # create tag
    tag = create_tag(j)
    tag = update_tag(j, tag)

    # post tag notes
    j.post_tag_note(tag.id, note.id)

    note_tags(j, note, tag)
    tag_notes(j, tag, note)
    delete_tag_note(j, tag, note)

    delete_tag(j, tag)
    delete_note(j, note)

    delete_folder(j, folder.id)

    resource = create_resource(j, "joplin.py")
    resource = update_resouce(j, resource)

    get = j.get(ResourceNode, resource.id)
    assert get.id == resource.id
    assert get.title == resource.title

    resources = get_resrouces(j)
    matched = list(filter(lambda r: r.id == resource.id, resources))
    assert len(matched) == 1
    assert matched[0].id == resource.id

    resource_file(j, resource.id)

    j.delete(ResourceNode, resource.id)
    get = j.get(ResourceNode, resource.id)
    assert get is None
