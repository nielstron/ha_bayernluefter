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

## The result:

![Configured groups containing Bayernluft informations](bayernluftresult.png)
![Custombayernluft card](bayernluftcustomcard.png)

The second card which is taken from: https://github.com/arjenvrh/audi_connect_ha requires the following mods: 

https://github.com/thomasloven/lovelace-card-mod

https://github.com/custom-cards/circle-sensor-card

and the following configuration:

```yaml
type: picture-elements
image: /local/img/bayernluefter.png
style: |
  ha-card {
    border-radius: 10px;
    border: solid 1px rgba(100,100,100,0.3);
    box-shadow: 3px 3px rgba(0,0,0,0.4);
    background-color: white;
    overflow: hidden;
  } 
elements:
  - type: image
    image: /local/img/bayernluefter.png
    style:
      left: 50%
      top: 90%
      width: 100%
      height: 60px
  - type: icon
    icon: 'mdi:water-percent'
    entity: sensor.bayernluefter_abs_humidity_in
    tap_action: more_info
    style:
      color: black
      left: 30%
      top: 5%
  - type: state-label
    entity: sensor.bayernluefter_abs_humidity_in
    style:
      color: black
      left: 30%
      top: 10%
  - type: icon
    icon: 'mdi:water-percent'
    entity: sensor.bayernluefter_abs_humidity_out
    tap_action: more_info
    style:
      color: black
      left: 30%
      top: 90%
  - type: state-label
    entity: sensor.bayernluefter_abs_humidity_out
    style:
      color: black
      left: 30%
      top: 95%
  - type: icon
    icon: 'mdi:thermometer'
    entity: sensor.bayernluefter_temp_out
    tap_action: more_info
    style:
      color: black
      left: 8%
      top: 5%
  - type: state-label
    entity: sensor.bayernluefter_temp_out
    style:
      color: black
      left: 8%
      top: 10%
  - type: icon
    icon: 'mdi:thermometer'
    entity: sensor.bayernluefter_temp_in
    tap_action: more_info
    style:
      color: black
      left: 10%
      top: 90%
  - type: state-label
    entity: sensor.bayernluefter_temp_in
    style:
      color: black
      left: 10%
      top: 95%
  - type: icon
    icon: 'mdi:thermometer'
    entity: sensor.bayernluefter_temp_fresh
    tap_action: more_info
    style:
      color: black
      left: 90%
      top: 15%
  - type: state-label
    entity: sensor.bayernluefter_temp_fresh
    style:
      color: black
      left: 90%
      top: 20%
  - type: 'custom:circle-sensor-card'
    entity: sensor.bayernluefter_efficiency
    max: 100
    min: 0
    stroke_width: 15
    gradient: true
    fill: '#FF'
    name: eff.
    units: ' '
    font_style:
      font-size: 1.0em
      font-color: black
      text-shadow: 1px 1px black
    style:
      top: 2%
      left: 60%
      width: 4em
      height: 4em
      transform: none
```

