{% if grains['kernel'] == 'Linux' %}
python-pip:
  pkg.installed

gcc:
  pkg.installed

python-devel:
  pkg.installed

/usr/lib/python2.6/site-packages/salt/modules/mount.py:
   file.managed:
     - source: salt://sync_files/mount.py
     - name: /usr/lib/python2.6/site-packages/salt/modules/mount.py

salt-minion:
    service.running:
        - enable: True
        - reload: True
        - watch:
            - file: /usr/lib/python2.6/site-packages/salt/modules/mount.py
{% endif %}

psutil:
  cmd.run:
{% if grains['kernel'] == 'Windows' %}
    - name: "easy_install psutil"
    - cwd: 'C:\salt\bin\scripts'
    - bin_env: 'C:\salt\bin\scripts\pip.exe'
{% else %}
    - name: "pip install psutil"
    - require:
       - pkg: python-pip
{% endif %}
