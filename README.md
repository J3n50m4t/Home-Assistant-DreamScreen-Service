# Home-Assistant-DreamScreen-Service
This is a custom component for Home-Assistant which will add the ability to control a Wifi enabled DreamScreen (HD & 4k).  Currently the support is new/experimental.

# Installation/Usage

## Hacs custom repo

If you use [Hacs](https://hacs.xyz) go to Settings and paste 
`https://github.com/GregoryDosh/Home-Assistant-DreamScreen-Service` and choose `integration`.
You now can switch to the Integrations Tab and install DreamScreen-Service. 

Continue with [configuration](#configuration)

## Git Clone
You can clone this repo into your `custom_components` folder in your Home Assistant config location with the name `dreamscreen`.
```bash
git clone https://github.com/GregoryDosh/Home-Assistant-DreamScreen-Service.git dreamscreen
```

## Git Submodule
You can also add it as a submodule which will allow you to pull updates in the future using `git submodule foreach git pull`.
```bash
git submodule add -b master https://github.com/GregoryDosh/Home-Assistant-DreamScreen-Service.git dreamscreen
```

## Configuration

Simply adding the `dreamscreen` component will enable device autodiscovery.
**THIS DOES NOT WORK See #18. Add your hostname/ip** 

```yaml
dreamscreen:
```

Depending on your network some times a search may terminate before the discovery
has completed. You can specify the timeout to use before the component will give
up waiting for a response.

```yaml
dreamscreen:
  timeout: 5
```
If you want you can configure the devices by hostname or IP address, this will disable
auto discovery.

```yaml
dreamscreen:
  devices:
    - dream_screen:
        address: 192.168.0.140
```

Finally: you can specify the timeout for the component to wait for a response when
requesting the current state from the device.

```yaml
dreamscreen:
  devices:
    - dream_screen:
        address: 192.168.0.140
        timeout: 5
```

## Example Configuration
This exposes the input sources as individual bulbs for the emulated_hue bridge so that you might control the HDMI inputs via Harmony or some other apps.

```yaml
dreamscreen:

homeassistant:
  customize:
    script.dreamscreen_input_source_1:
      emulated_hue_hidden: false
      hidden: true
    script.dreamscreen_input_source_2:
      emulated_hue_hidden: false
      hidden: true
    script.dreamscreen_input_source_3:
      emulated_hue_hidden: false
      hidden: true

script:
  dreamscreen_input_source_1:
    alias: "DreamScreen - Source 1"
    sequence:
      - service: dreamscreen.set_hdmi_source
        data:
          entity_id: dreamscreen.living_room
          source: 0
  dreamscreen_input_source_2:
    alias: "DreamScreen - Source 2"
    sequence:
      - service: dreamscreen.set_hdmi_source
        data:
          entity_id: dreamscreen.living_room
          source: 1
  dreamscreen_input_source_3:
    alias: "DreamScreen - Source 3"
    sequence:
      - service: dreamscreen.set_hdmi_source
        data:
          entity_id: dreamscreen.living_room
          source: 2

```

## Services
### dreamscreen.set_mode
**entity_id**: Name of DreamScreen device to send command to.

**mode**

| Value | Mode |
| - | - |
| 0 | Off |
| 1 | Video |
| 2 | Music |
| 3 | Ambient|

```json
{
    "entity_id": "dreamscreen.living_room",
    "mode": 1
}
```

### dreamscreen.set_hdmi_source
**entity_id**: Name of DreamScreen device to send command to.

**source**

| Value | HDMI Source |
| - | - |
| 0 | HDMI Source 1 |
| 1 | HDMI Source 2 |
| 2 | HDMI Source 3 |

```json
{
    "entity_id": "dreamscreen.living_room",
    "source": 0
}
```

### dreamscreen.set_brightness
**entity_id**: Name of DreamScreen device to send command to.

**brightness**: Integer values between 0 and 100
```json
{
    "entity_id": "dreamscreen.living_room",
    "brightness": 75
}
```

### dreamscreen.set_ambiance_color
**entity_id**: Name of DreamScreen device to send command to.

**color**: Hex valued color
```json
{
    "entity_id": "dreamscreen.living_room",
    "color": "#40e0d0",
}
```

### dreamscreen.set_ambiance_scene
**entity_id**: Name of DreamScreen device to send command to.

**scene**

| Value | Ambiance Scene |
| - | - |
| 0 | Random Colors |
| 1 | Fireside |
| 2 | Twinkle |
| 3 | Ocean|
| 4 | Pride|
| 5 | July 4th|
| 6 | Holiday|
| 7 | Pop|
| 8 | Enchanted Forrest|

```json
{
    "entity_id": "dreamscreen.living_room",
    "scene": 4
}
```
## LoveLace

An example how to integrate your dreamscreen into your homeassistant lovelace can be found in the wiki.

[Lovelace Example](https://github.com/GregoryDosh/Home-Assistant-DreamScreen-Service/wiki/LoveLace-Example)
