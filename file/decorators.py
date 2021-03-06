import functools
import re
from datetime import datetime
# django imports
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User

# local imports
from .models import File
from folder.models import Folder


# check_is_owner
# check_is_folder
# check_request_attr
REGEX_NAME = r"^[\w\-. ]+$"


def get_id(request):
    if(request.method == "GET" or request.method == "DELETE"):
        id = request.GET["id"]
    else:
        id = request.data["id"]
    return id


def check_id_file(func):

    @functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
        id = get_id(request)
        file = File.custom_objects.get_or_none(id=id)
        if(file == None):
            return Response(data={"message": "Invalid id or id is not of a file"}, status=status.HTTP_400_BAD_REQUEST)

        result = func(self, request, args, **kwargs)
        return result
    return wrapper


def check_is_owner_file(func):

    @functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
        id = get_id(request)

        file = File.custom_objects.get(id=id)
        if(file.owner != request.user):
            return Response(data={"message": "user is not owner of the file"}, status=status.HTTP_400_BAD_REQUEST)

        result = func(self, request, args, **kwargs)
        return result
    return wrapper


def check_has_access_file(func):

    @functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
        id = get_id(request)

        file = File.custom_objects.get(id=id)
        allowed = False

        if(file.owner == request.user or file.privacy == False):
            allowed = True

        if (request.user in file.shared_among.all()):
            allowed = True

        if(not allowed):
            return Response(data={"message": "user is not allowed to see the file"}, status=status.HTTP_400_BAD_REQUEST)
        result = func(self, request, args, **kwargs)
        return result
    return wrapper


def check_valid_name_request_file(func):
    @functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
        for req_file in request.FILES.getlist('file'):
            name = req_file.name
            if re.match(REGEX_NAME, name) is None:
                return Response(data={"message": f"Invalid Name of file - {name}"}, status=status.HTTP_400_BAD_REQUEST)
        result = func(self, request, *args, **kwargs)
        return result
    return wrapper


def check_valid_name_request_body(func):
    @functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
        name = request.data["NAME"]
        if re.match(REGEX_NAME, name) is None:
            return Response(data={"message": "Invalid Name of file"}, status=status.HTTP_400_BAD_REQUEST)
        result = func(self, request, *args, **kwargs)
        return result
    return wrapper


def check_already_present(to_check):
    def decorator_func(func):
        @functools.wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # there might be cases in patch when we are not changing names
            if(request.FILES or "name" in request.data):

                # for post when new is created by parent id
                if("PARENT" in request.data):
                    parent_id = request.data["PARENT"]
                    parent_folder = Folder.custom_objects.get(id=parent_id)

                # for patch when rename is done by folder id
                else:
                    id = get_id(request)
                    folder = File.custom_objects.get(id=id)
                    parent_folder = folder.parent

                if(to_check == "req_data_name"):
                    name = request.data["name"]
                    children = parent_folder.children_file.all().filter(name=name)
                    if(children):
                        return Response(data={"message": f"File with given name = {name} already exists"}, status=status.HTTP_400_BAD_REQUEST)

                elif to_check == "req_file_name":
                    for req_file in request.FILES.getlist('file'):
                        name = req_file.name
                        children = parent_folder.children_file.all().filter(name=name)
                        if(children):
                            return Response(data={"message": f"File with given name = {name} already exists"}, status=status.HTTP_400_BAD_REQUEST)

            result = func(self, request, *args, **kwargs)
            return result
        return wrapper
    return decorator_func


def check_file_not_trashed(func):
    @ functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
        id = get_id(request)
        file = File.custom_objects.get(id=id)

        if file.trash:
            return Response(data={"message": "File is in Trash"}, status=status.HTTP_400_BAD_REQUEST)
        result = func(self, request, *args, **kwargs)
        return result
    return wrapper


def update_last_modified_file(func):
    @ functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
        id = get_id(request)
        file = File.custom_objects.get(id=id)
        file.last_modified = datetime.now()
        file.save()
        result = func(self, request, *args, **kwargs)
        return result
    return wrapper
