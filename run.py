#!/usr/bin/env python

# Copyright 2018 Objectif Libre
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import glob
import os

import jinja2


class Runner(object):
    def __init__(self, src_file, dest_file, secrets_dir, verbose):
        self.src_file = src_file
        self.dest_file = dest_file
        self.secrets_dir = secrets_dir
        self.verbose = verbose

    def v_print(self, message):
        if self.verbose:
            print(message)

    def run(self):
        self.v_print('Source file: %s' % self.src_file)
        self.v_print('Dest file: %s' % self.dest_file)
        self.v_print('Secrets dir: %s' % self.secrets_dir)

        j_env = {}

        # parse the secret files
        secret_files = glob.glob(os.path.join(self.secrets_dir, '*'))
        if not secret_files:
            self.v_print('No secret files found')
        for secret_file in secret_files:
            key = os.path.basename(secret_file)
            with open(secret_file) as fd:
                value = fd.read().strip()
            j_env[key] = value
            self.v_print('Read secret `%s`' % key)

        # parse the environment variables
        for k, v in os.environ.items():
            if k.startswith('JINJA_VAR_'):
                j_env[k[10:]] = v

        with open(self.src_file) as fd:
            template_data = fd.read()
        template = jinja2.Template(template_data)
        with open(self.dest_file, 'w') as fd:
            fd.write(template.render(**j_env))
        self.v_print('Template rendered. Done')


if __name__ == "__main__":
    runner = Runner(
        os.environ.get('JINJA_SRC_FILE', '/config_src/template.j2'),
        os.environ.get('JINJA_DEST_FILE', '/config/settings.py'),
        os.environ.get('JINJA_SECRETS_DIR', '/secrets'),
        os.environ.get('VERBOSE', False),
    )
    runner.run()
