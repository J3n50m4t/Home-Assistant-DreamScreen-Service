# Home-Assistant-DreamScreen-Service
Based on ideas from https://github.com/avwuff/DreamScreenControl and [https://github.com/genesisfactor/DreamScreenCommander](https://github.com/genesisfactor/DreamScreenCommander).  This is a custom component for Home-Assistant which will add the ability to control a Wifi enabled DreamScreen (HD & 4k).  Currently the support is new/experimental.

# Installation/Usage
Simply place the `custom_components` folder in your Home Assistant config folder and you should be able to use it in the examples below.  It only exposes services but in the future it would be nice to show the current status of the DreamScreen too.

## Example Configuration
```yaml
dreamscreen:
  ip_address: 172.10.10.200
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
| 0 | Color/Slider? |
| 1 | Scenes (Required for setting scene below) |

```json
{
    "mode": 1
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