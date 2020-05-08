[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

Bayernluefter control for home assistant.

Example configuration.yaml

```yaml
sensor:
  - platform: bayernluefter
    name: Living Room WRG
    resource: 192.168.178.5

switch:
  - platform: bayernluefter
    name: Living Room WRG Power
    resource: 192.168.178.5
```
