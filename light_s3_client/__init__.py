"""
light-s3-client - A lightweight Python library for interacting with Amazon S3.

This module provides a simplified interface to S3 operations without requiring the full Boto3 SDK.
"""

import json
import requests
from requests import Response
import base64
import hmac
from hashlib import sha256
from datetime import datetime, timezone
import io
import xmltodict
import os
import logging
from typing import Union, Optional, TYPE_CHECKING
from .version import __version__
from .exceptions import UnknownBucketError, BucketNotFound, AccessDeniedToBucket

__author__ = 'socket.dev'
__all__ = [
    "Client",
]


log = logging.getLogger("light-s3-client")
log.addHandler(logging.NullHandler())


def do_request(
        url: str,
        headers: dict,
        data: Union[bytes, io.TextIOWrapper, io.BufferedReader, dict, None] = None,
        stream: bool = True,
        method: str = "GET",
        bucket: Optional[str] = None,
        key: Optional[str] = None,
        prefix: Optional[str] = None
) -> Union[Response, None]:
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            data=data,
            stream=stream
        )
    except requests.exceptions.ConnectionError as error:
        msg = {
            'error': f"Connection error performing {method} on {url}",
            'data': str(error)
        }
        error_msg = json.dumps(msg)
        response = Response()
        response.status_code = 500
        response._content = bytes(error_msg, 'utf-8')
        log.error(f"Connection error: {error}")
        return response
    except requests.exceptions.Timeout as error:
        msg = {
            'error': f"Timeout error performing {method} on {url}",
            'data': str(error)
        }
        error_msg = json.dumps(msg)
        response = Response()
        response.status_code = 500
        response._content = bytes(error_msg, 'utf-8')
        log.error(f"Timeout error: {error}")
        return response
    except requests.exceptions.RequestException as error:
        msg = {
            'error': f"Request error performing {method} on {url}",
            'data': str(error)
        }
        error_msg = json.dumps(msg)
        response = Response()
        response.status_code = 500
        response._content = bytes(error_msg, 'utf-8')
        log.error(f"Request error: {error}")
        return response
    except Exception as error:
        msg = {
            'error': f"Unexpected error performing {method} on {url}",
            'data': str(error)
        }
        error_msg = json.dumps(msg)
        response = Response()
        response.status_code = 500
        response._content = bytes(error_msg, 'utf-8')
        log.error(f"Unexpected error: {error}")
        return response
    msg_items = [f"url: {url}", f"method: {method}"]
    if bucket is not None:
        msg_items.append(f"bucket: {bucket}")
    if prefix is not None:
        msg_items.append(f"prefix: {prefix}")
    if key is not None:
        msg_items.append(f"key: {key}")
    msg = ", ".join(msg_items)
    if response.status_code == 200 or response.status_code == 204:
        return response
    elif response.status_code == 403:
        raise AccessDeniedToBucket(msg)
    elif response.status_code == 404:
        raise BucketNotFound(msg)
    else:
        # Parse the S3 error response for more detailed error information
        try:
            error_data = xmltodict.parse(response.text)
            error_code = error_data.get("Error", {}).get("Code", "Unknown")
            error_message = error_data.get("Error", {}).get("Message", response.text)
            detailed_msg = f"{error_code}: {error_message}"
            raise UnknownBucketError(detailed_msg)
        except Exception:
            raise UnknownBucketError(response.text)


class Client:
    """
    A lightweight S3 client for interacting with Amazon S3 or S3-compatible services.
    
    This client provides a simplified interface to S3 operations without requiring the full Boto3 SDK.
    It implements AWS Signature Version 4 authentication directly using the requests library.
    
    Args:
        access_key (str): The AWS Access Key for API Access
        secret_key (str): The AWS Secret Key for API Access
        region (str): The S3 region being used
        server (str, optional): An override of the HTTPS URL to use. Defaults to None.
        encryption (str, optional): The encryption algorithm to use for uploads. Defaults to "AES256".
        
    Attributes:
        region (str): The S3 region being used
        server (str): The S3 server URL
        base_url (str): The base S3 URL
        access_key (str): The AWS Access Key
        secret_key (str): The AWS Secret Key
        date_format (str): The date format used for requests
        encryption (str): The encryption algorithm to use for uploads
    """
    server: str
    bucket_name: str
    access_key: str
    secret_key: str
    date_format: str
    region: str
    base_url: str
    signature_version: str

    def __init__(self,
                 access_key: str,
                 secret_key: str,
                 region: str,
                 server: Optional[str] = None,
                 encryption="AES256",
                 signature_version: str = "v4") -> None:
        self.region = region
        self.base_url = "s3.amazonaws.com"
        if server is None:
            self.server = f"https://s3-{self.region}.{self.base_url}"
        else:
            self.server = server
        self.access_key = access_key
        self.secret_key = secret_key
        self.date_format = "%a, %d %b %Y %H:%M:%S +0000"
        self.encryption = encryption
        self.signature_version = signature_version

    if TYPE_CHECKING:
        @staticmethod
        def do_request(
            url: str,
            headers: dict,
            data: Union[bytes, io.TextIOWrapper, io.BufferedReader, dict, None] = None,
            stream: bool = True,
            method: str = "GET",
            bucket: Optional[str] = None,
            key: Optional[str] = None,
            prefix: Optional[str] = None
        ) -> Union[Response, None]: ...
        def create_bucket(self, Bucket: str) -> bool: ...
        def delete_bucket(self, Bucket: str) -> bool: ...
        def head_bucket(self, Bucket: str) -> bool: ...
        def list_objects(self, Bucket: str, Prefix: str) -> list: ...
        def get_object(self, Bucket: str, Key: str) -> bool: ...
        def head_object(self, Bucket: str, Key: str) -> dict: ...
        @staticmethod
        def get_bucket_keys(xml_text: str, prefix: str) -> list: ...
        def download_file(self, Bucket: str, Key: str, Filename: str) -> str: ...
        def upload_fileobj(self, Fileobj: io.BytesIO, Bucket: str, Key: str) -> Optional[Response]: ...
        def delete_file(self, Bucket: str, Key: str) -> bool: ...
        @staticmethod
        def create_download_folders(key: str) -> None: ...
        def put_object_tagging(self, Bucket: str, Key: str, Tags: dict) -> bool: ...
        def get_object_tagging(self, Bucket: str, Key: str) -> dict: ...
        def upload_file_multipart(self, Fileobj: Union[io.BytesIO, bytes, bytearray], Bucket: str, Key: str, part_size: int = 5242880, max_parts: int = 10000) -> Optional[Response]: ...
        def _abort_multipart_upload(self, Bucket: str, Key: str, upload_id: str) -> None: ...
        def create_aws_signature(self, method: str, url: str, headers: dict, payload=None) -> dict: ...
        def _get_current_date(self) -> str: ...
        def _get_server_url(self) -> str: ...
        def build_vars(self, file_name: str, bucket_name: str) -> tuple[str, str]: ...


# Set up method bindings after class definition
import light_s3_client.buckets as buckets_module
import light_s3_client.files as files_module
import light_s3_client.objects as objects_module
import light_s3_client.auth as auth_module
import light_s3_client.multipart as multipart_module

# Bind methods to the Client class
setattr(Client, 'do_request', staticmethod(do_request))

setattr(Client, 'create_bucket', buckets_module.create_bucket)
setattr(Client, 'delete_bucket', buckets_module.delete_bucket)
setattr(Client, 'head_bucket', buckets_module.head_bucket)
setattr(Client, 'list_objects', buckets_module.list_objects)
setattr(Client, 'get_object', buckets_module.get_object)
setattr(Client, 'head_object', buckets_module.head_object)
setattr(Client, 'get_bucket_keys', staticmethod(buckets_module.get_bucket_keys))

setattr(Client, 'download_file', files_module.download_file)
setattr(Client, 'upload_fileobj', files_module.upload_fileobj)
setattr(Client, 'delete_file', files_module.delete_file)
setattr(Client, 'create_download_folders', staticmethod(files_module.create_download_folders))

setattr(Client, 'put_object_tagging', objects_module.put_object_tagging)
setattr(Client, 'get_object_tagging', objects_module.get_object_tagging)

setattr(Client, 'upload_file_multipart', multipart_module.upload_file_multipart)
setattr(Client, '_abort_multipart_upload', multipart_module._abort_multipart_upload)

setattr(Client, 'create_aws_signature', auth_module.create_aws_signature)
setattr(Client, '_get_current_date', auth_module._get_current_date)
setattr(Client, '_get_server_url', auth_module._get_server_url)
setattr(Client, 'build_vars', auth_module.build_vars)
