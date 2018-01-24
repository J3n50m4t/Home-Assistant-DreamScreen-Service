# Home-Assistant-DreamScreen-Service
Based on ideas from https://github.com/avwuff/DreamScreenControl and [https://github.com/genesisfactor/DreamScreenCommander](https://github.com/genesisfactor/DreamScreenCommander), and [DreamScreen WiFi UDP Protocol](http://dreamscreen.boards.net/thread/293/dreamscreen-wifi-udp-protocol) .  This is a custom component for Home-Assistant which will add the ability to control a Wifi enabled DreamScreen (HD & 4k).  Currently the support is new/experimental.

# Installation/Usage

# Copy & Paste
Simply place the `dreamscreen` folder in your `custom_components` folder in your Home Assistant config location and you should be able to use it in the examples below.  It only exposes services but in the future it would be nice to show the current status of the DreamScreen too.

## Git Clone
You can clone this repo into your `custom_components` folder in your Home Assistant config location with the name `dreamscreen`.  The `__init__.py` at the root of the repo is a symbolic link into the `dreamscreen` folder.
```bash
git clone git@github.com:GregoryDosh/Home-Assistant-DreamScreen-Service.git dreamscreen
```

## Git Submodule
Adding it as a submodule will allow you to pull updates in the future using `git submodule update`.
```bash
git submodule add -b master git@github.com:GregoryDosh/Home-Assistant-DreamScreen-Service.git dreamscreen
```


## Example Configuration
This exposes the input sources as individual bulbs for the emulated_hue bridge so that you might control the HDMI inputs via Harmony or some other apps.

**ip_address** Required IP address to communicate with your DreamScreen.  Right now there is only support for 1 at a time.

**group** Optional group.  If you're not sure, don't use this parameter.

```yaml
dreamscreen:
  ip_address: 172.10.10.200

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
          source: 0
  dreamscreen_input_source_2:
    alias: "DreamScreen - Source 2"
    sequence:
      - service: dreamscreen.set_hdmi_source
        data:
          source: 1
  dreamscreen_input_source_3:
    alias: "DreamScreen - Source 3"
    sequence:
      - service: dreamscreen.set_hdmi_source
        data:
          source: 2

```

## Services
### dreamscreen.set_mode
**mode**

| Value | Mode |
| - | - |
| 0 | Off |
| 1 | Video |
| 2 | Music |
| 3 | Ambient|

```json
{
    "mode": 1
}
```
### dreamscreen.set_hdmi_source
**source**

| Value | HDMI Source |
| - | - |
| 0 | HDMI Source 1 |
| 1 | HDMI Source 2 |
| 2 | HDMI Source 3 |

```json
{
    "source": 0
}
```
### dreamscreen.set_brightness
**brightness**: Integer values between 0 and 100
```json
{
    "brightness": 75
}
```
### dreamscreen.set_ambiance_mode
**mode**

| Value | Ambiance Mode |
| - | - |
| 0 | RGB Color |
| 1 | Scenes (Required for setting scene below) |

```json
{
    "mode": 1
}
```
### dreamscreen.set_ambiance_color
At least one of the 3 keys are required.

**red**: Integer values between 0 and 255

**green**: Integer values between 0 and 255

**blue**: Integer values between 0 and 255

```json
{
    "red": 64,
    "green": 224,
    "blue": 208
}
```
### dreamscreen.set_ambiance_scene
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
    "scene": 4
}
```