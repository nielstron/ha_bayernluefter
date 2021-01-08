[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

# Bayernlüfter Custom Component

A custom component for controlling the [Bayernlüfter](https://www.bayernluft.de/de/intro.htm) (Bayernluefter) via [home-assistant](home-assistant.io/).
The Bayernlüfter needs to have a WiFi-Module and additional humidity sensors installed (original [WiFi-Module](https://www.bayernluft.de/de/detailanzeige.cgi?suchen=TRUE&search_field=artikel&search_for=BV-WLN-2) and [Sensors](https://www.bayernluft.de/de/detailanzeige.cgi?suchen=TRUE&search_field=artikel&search_for=BV-FS-1) and [DIY option](https://github.com/nielstron/diy_bayernluft)).

The component enables controlling the fan, monitoring humditity and toggling Power and Timer mode.

Example configuration.yaml

```yaml
bayernluefter:
    name: Living Room WRG
    resource: http://192.168.178.5
    scan_interval: 30 # Optional scan interval in seconds
```

## Installation

Copy into your custom_components directory or install via [HACS](https://hacs.xyz/)
