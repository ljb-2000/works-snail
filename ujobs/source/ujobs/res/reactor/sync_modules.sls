sync_modules:
    local.saltutil.sync_modules:
        - tgt: {{ data['data']['id'] }}

install_packages:
    local.state.sls:
        - tgt: {{ data['data']['id']}}
        - arg: 
          -  packages