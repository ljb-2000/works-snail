include:
  - packages

module_ujobs.py:
  file.managed:
    - source: salt://_modules/ujobs.py
    - name: /srv/salt/_modules/ujobs.py
    - makedirs: True
  cmd.run:
    - name: salt '*' saltutil.sync_all
    - watch:
      - file: /srv/salt/_modules/ujobs.py

top_sls:
  file.managed:
    - source: salt://top.sls
    - name: /srv/salt/top.sls
    - makedirs: True

sync_dirs:
  file.recurse:
    - source: salt://sync_files
    - name: /srv/salt/sync_files

packages_sls:
  file.managed:
    - source: salt://packages.sls
    - name: /srv/salt/packages.sls
    - makedirs: True

run_install_pkgs:
  cmd.run:
    - name: salt '*' state.sls packages
    - watch:
      - file: packages_sls
