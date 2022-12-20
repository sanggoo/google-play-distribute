#!/usr/bin/python
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Uploads an apk to the alpha track."""

import argparse

import sys
from apiclient.discovery import build
import httplib2
from oauth2client import client
from oauth2client.service_account import ServiceAccountCredentials

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=True)
argparser.add_argument("service_account_email", help="service_account_email")
argparser.add_argument("key_file", help="key file")
argparser.add_argument(
    "package_name", help="The package name. Example: com.android.sample"
)
argparser.add_argument(
    "bundle_file",
    nargs="?",
    default="test.aab",
    help="The path to the AAB file to upload.",
)


def main(argv):
    # Process flags and read their values.
    flags = argparser.parse_args()

    service_account_email = flags.service_account_email
    key = flags.key_file
    package_name = flags.package_name
    bundle_file = flags.bundle_file

    scope = "https://www.googleapis.com/auth/androidpublisher"

    credentials = ServiceAccountCredentials.from_p12_keyfile(
        service_account_email, key, scopes=[scope]
    )
    http = httplib2.Http()
    http = credentials.authorize(http)

    service = build("androidpublisher", "v3", http=http)

    try:
        edit_request = service.edits().insert(body={}, packageName=package_name)
        result = edit_request.execute()
        edit_id = result["id"]

        result = (
            service.edits()
            .bundles()
            .upload(
                editId=edit_id,
                packageName=package_name,
                media_mime_type="application/octet-stream",
                media_body=bundle_file,
            )
            .execute()
        )

        print("Version code %d has been uploaded" % result["versionCode"])

        commit_request = (
            service.edits().commit(editId=edit_id, packageName=package_name, changesNotSentForReview=True).execute()
        )

        print('Edit "%s" has been committed' % (commit_request["id"]))

    except client.AccessTokenRefreshError:
        print(
            "The credentials have been revoked or expired, please re-run the "
            "application to re-authorize"
        )


if __name__ == "__main__":
    main(sys.argv)
