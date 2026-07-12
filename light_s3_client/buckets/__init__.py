"""
Bucket-related operations for the light-s3-client.
This module contains functions for managing S3 buckets.
"""

import xmltodict
from ..exceptions import UnknownBucketError, BucketNotFound, AccessDeniedToBucket
from ..version import __version__
import logging

log = logging.getLogger("light-s3-client")


def create_bucket(self, Bucket: str) -> bool:
    """
    Create an S3 bucket.

    Args:
        Bucket (str): The name of the bucket to create

    Returns:
        bool: True if bucket was created successfully, False if access was denied
    """
    s3_url = f"{self._get_server_url()}/{Bucket}"
    headers = {
        "User-Agent": f"light-s3-client/{__version__}"
    }

    # For regions other than us-east-1, send a CreateBucketConfiguration body
    payload = None
    if self.region != "us-east-1":
        body = {
            "CreateBucketConfiguration": {
                "LocationConstraint": self.region
            }
        }
        payload = xmltodict.unparse(body).encode("utf-8")

    auth_headers = self.create_aws_signature("PUT", s3_url, headers, payload=payload)
    headers.update(auth_headers)

    try:
        response = self.do_request(url=s3_url, headers=headers, method="PUT", data=payload)
        if response.status_code == 200:
            log.info(f"Created bucket {Bucket}")
            return True
    except AccessDeniedToBucket:
        log.info(f"Access denied creating bucket {Bucket}")
        return False

    return False


def delete_bucket(self, Bucket: str) -> bool:
    """
    Delete an S3 bucket.

    Args:
        Bucket (str): The name of the bucket to delete

    Returns:
        bool: True if bucket was deleted successfully, False if bucket not found
    """
    s3_url = f"{self._get_server_url()}/{Bucket}"
    headers = {
        "User-Agent": f"light-s3-client/{__version__}"
    }
    auth_headers = self.create_aws_signature("DELETE", s3_url, headers)
    headers.update(auth_headers)

    try:
        response = self.do_request(url=s3_url, headers=headers, method="DELETE")
        if response.status_code == 204:
            log.info(f"Deleted bucket {Bucket}")
            return True
    except BucketNotFound:
        log.info(f"Bucket {Bucket} not found")
        return False
    # Bucket-not-empty errors propagate as UnknownBucketError

    return False


def head_bucket(self, Bucket: str) -> bool:
    """
    Check if an S3 bucket exists.

    Args:
        Bucket (str): The name of the bucket to check

    Returns:
        bool: True if bucket exists, False if not found
    """
    s3_url = f"{self._get_server_url()}/{Bucket}"
    headers = {
        "User-Agent": f"light-s3-client/{__version__}"
    }
    auth_headers = self.create_aws_signature("HEAD", s3_url, headers)
    headers.update(auth_headers)

    try:
        response = self.do_request(url=s3_url, headers=headers, method="HEAD")
        if response.status_code == 200:
            log.info(f"Bucket {Bucket} exists")
            return True
    except BucketNotFound:
        log.info(f"Bucket {Bucket} not found")

    return False


def list_objects(self, Bucket: str, Prefix: str) -> list:
    """
    List all keys in an S3 bucket with a given prefix.
    
    Args:
        Bucket (str): The name of the bucket to list objects from
        Prefix (str): The prefix to use for filtering keys
        
    Returns:
        list: List of object keys matching the prefix
    """
    s3_url = f"{self._get_server_url()}/{Bucket}/?list-type=2&prefix={Prefix}"
    headers = {
        "User-Agent": f"light-s3-client/{__version__}"
    }
    auth_headers = self.create_aws_signature("GET", s3_url, headers)
    headers.update(auth_headers)
    # Make the request
    response = self.do_request(url=s3_url, headers=headers)
    log.info(f"Retrieved keys for bucket {Bucket} with prefix {Prefix}")
    data = get_bucket_keys(response.text, Prefix)
    return data


def get_object(self, Bucket: str, Key: str) -> bool:
    """
    Check if an S3 object exists.
    
    Args:
        Bucket (str): The name of the bucket to check
        Key (str): The key to check for existence
        
    Returns:
        bool: True if object exists, False otherwise
    """
    s3_url = f"{self._get_server_url()}/{Bucket}/{Key}"
    headers = {
        "User-Agent": f"light-s3-client/{__version__}"
    }
    auth_headers = self.create_aws_signature("GET", s3_url, headers)
    headers.update(auth_headers)
    # Make the request
    exists = False
    try:
        response = self.do_request(url=s3_url, headers=headers, stream=True)
        if response.status_code == 200:
            log.info(f"key {Key} from bucket {Bucket} exists")
            exists = True
    except BucketNotFound:
        log.info(f"{Key} not found in {Bucket}")
    return exists


def head_object(self, Bucket: str, Key: str) -> dict:
    """
    Check if an S3 object exists and return its metadata.
    
    Args:
        Bucket (str): The S3 Bucket name
        Key (str): The S3 key to check
        
    Returns:
        dict: Dictionary containing object metadata, or empty dict if object doesn't exist
    """
    s3_url = f"{self._get_server_url()}/{Bucket}/{Key}"
    headers = {
        "User-Agent": f"light-s3-client/{__version__}"
    }
    auth_headers = self.create_aws_signature("HEAD", s3_url, headers)
    headers.update(auth_headers)
    # Make the request
    response = self.do_request(url=s3_url, headers=headers, method="HEAD")
    if response.status_code == 200:
        # Return metadata from response headers
        metadata = {
            "Content-Type": response.headers.get("Content-Type"),
            "Content-Length": response.headers.get("Content-Length"),
            "ETag": response.headers.get("ETag"),
            "Last-Modified": response.headers.get("Last-Modified"),
            "Server": response.headers.get("Server"),
            "x-amz-request-id": response.headers.get("x-amz-request-id"),
            "x-amz-id-2": response.headers.get("x-amz-id-2")
        }
        # Remove None values
        metadata = {k: v for k, v in metadata.items() if v is not None}
        log.info(f"Object {Key} from bucket {Bucket} exists with metadata")
        return metadata
    else:
        log.info(f"Object {Key} not found in {Bucket}")
        return {}


def get_bucket_keys(xml_text: str, prefix: str) -> list:
    """
    get_bucket_keys parses the XML response from S3 list objects request.
    :param xml_text: XML response text from S3
    :param prefix: The prefix used for filtering keys
    :return: List of object keys
    """
    import xmltodict
    xml_data = xmltodict.parse(xml_text)
    results = xml_data.get("ListBucketResult")
    if prefix is None:
        prefix = ""
    if results is not None:
        contents = results.get("Contents")
    else:
        contents = None
    data = []
    if contents is not None:
        # Ensure contents is always a list
        if isinstance(contents, dict):
            contents = [contents]
        for content in contents:
            key = content.get("Key")
            if key is not None and key.rstrip("/") != prefix.rstrip("/"):
                data.append(key)
    return data