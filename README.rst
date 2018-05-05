.. image:: https://travis-ci.org/ObjectifLibre/jinja-init.svg?branch=master
   :target: https://travis-ci.org/ObjectifLibre/jinja-init

#####################
jinja-init dockerfile
#####################

``jinja-init`` is a Docker image that can be used to run an init container in
Kubernetes. It uses the Jinja templating system to generate configuration
files using config maps, secrets and environment variables.

To learn more about Jinja2 templates have a look at the `project documentation
<http://jinja.pocoo.org/docs/2.10/>`__.

Example usage
=============

You can either build the image:

.. code-block:: console

   $ docker build -t jinja-init:latest .

Or get it from the Docker hub:

.. code-block:: console

   $ docker pull objectiflibre/jinja-init


To use the container in Kubernetes:

#. Create a configMap object to store the Jinja template:

   .. code-block:: console

      $ cat > template.php.j2 << EOF
      <?php
      \$db_pass = '{{ db_pass }}';
      \$db_host = '{{ db_host }}';
      \$db_user = '{{ db_user }}';
      ?>
      EOF
      $ kubectl create configmap config-template --from-file=template.php.j2

#. Create some secrets (optional). In this example only the ``db_pass``
   variable is stored as a secret, the other variables will be defined as a
   container environment variables:

   .. code-block:: console

      $ PASSWORD=$(echo -n 's3cr3t' | base64)
      $ cat > secrets.yml << EOF
      apiVersion: v1
      kind: Secret
      metadata:
        name: secrets
      data:
        db_pass: $PASSWORD
      EOF
      $ kubectl apply -f secrets.yml

#. Define your deployment. The generated configuration file needs to be stored
   on a volume (can be an ``emptyDir``) to share it between the init container
   and the application container.

   ``db_host`` and ``db_user`` are defined as environment variables, with the
   ``JINJA_VAR_`` prefix. This is optional, all the template variables could be
   stored in the secret.

   In this exemple the application container runs a single command to display
   the content of the generated file.

   .. code-block:: console

      $ cat > deployment.yml << EOF
      apiVersion: apps/v1
      kind: Deployment
      metadata:
        name: test
        labels:
          app: test
      spec:
        replicas: 1
        selector:
          matchLabels:
            app: test
        template:
          metadata:
            labels:
              app: test
          spec:
            initContainers:
            - name: config
              image: objectiflibre/jinja-init
              env:
              # source and destination files
              - name: JINJA_SRC_FILE
                value: /config_src/template.php.j2
              - name: JINJA_DEST_FILE
                value: /config/config.php
              - name: JINJA_VAR_db_host
                value: /secrets
              # let's be verbose
              - name: VERBOSE
                value: "1"
              # extra variables used in the template
              - name: JINJA_VAR_db_host
                value: "127.0.0.1"
              - name: JINJA_VAR_db_user
                value: app_user
              volumeMounts:
              # configMap mount point
              - name: config-template
                mountPath: /config_src
              # target directory mount point; the final config file will be created here
              - name: config
                mountPath: /config
              # /secrets is the default mount point used by jinja-init
              - name: secrets
                mountPath: /secrets
            containers:
            - name: busybox
              image: busybox
              command: ["cat", "/config/config.php"]
              volumeMounts:
              - name: config
                mountPath: /config
            volumes:
            - name: config-template
              configMap:
                name: config-template
            - name: config
              emptyDir:
            - name: secrets
              secret:
                secretName: secrets
      EOF
      $ kubectl apply -f deployment.yml
      $ kubectl logs deployment/test
      <?php
      $db_pass = 'password';
      $db_host = '127.0.0.1';
      $db_user = 'app_user';
      ?>

Variables
=========

The container supports the following variables:

``JINJA_SRC_FILE``
    Path of the source template.

    Default: ``/config_src/template.j2``

``JINJA_DEST_FILE``
    Path of the destination file (file generated from the template).

    Default: ``/config/settings.py``

``JINJA_SECRETS_DIR``
    Directory containing the secrets. The name of each file in this folder
    become the name of a jinja variable, and the content of the file is the
    value.

    Default: ``/secrets``

``VERBOSE``
    If defined the script will output extra information about what it is doing.

``JINJA_VAR_*``
    Extra jinja variables. The ``JINJA_VAR_`` prefix is removed from the
    variable name. The variable name in case sensitive.

Contributing
============

We welcome new ideas and contributions. You can use issues and pull requests to
help us improve this tool.
