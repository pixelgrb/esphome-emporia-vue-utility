# Frequently Asked Questions


### 1. Why is your product so good?

Why do so many FAQ's include this?

---

### 2. Where can I get help?

The [Community thread](https://community.home-assistant.io/t/emporia-vue-utility-connect/).

If you are brave: [read the ESPHome docs](https://esphome.io/components/)

---

### 3. I'm new, I just want something that works.  Why are there multiple YAML files and why are they different?

They’re just starting points with different features enabled or disabled. Pick one, add your Wi-Fi/password, and it should work.

Later, if you want to customize, see the [section on YAML configuration](yaml.md).  


---

### 4. I'm getting intermittent drop outs.  What do I check?

- First: **swap the USB power supply**.  We have seen a number of the Emporia USB power supplies fail, which started out like this.
- You may need to move the device closer to your power meter.
- You may need to contact your utililty and ask them to reprovision the device.

---

### 5. What is the API encryption key in the YAML file?

Looks like this in the YAML:
```
api:
  encryption:
    key: "M3d8zXcnwM4Uo2fRybLjFUNVs+mnlC1XbEfnlvUNI2c="
```

- Just a security measure.  It’s a shared secret between your device and Home Assistant.
- Ensures all ESPHome API traffic (state updates, commands, etc.) is encrypted and authenticated.
- Without it, someone on your LAN could spoof commands to the device.
- To generate one manually:

```
python3 -c "import base64, os; print(base64.b64encode(os.urandom(32)).decode())"
```

---

### 6. What is the OTA password in the YAML file?

Looks like this in the YAML:
```
ota:
  password: "blah"
```
- Just a security measure.  It’s a shared secret between your device and Home Assistant.
- Used only when flashing new firmware over Wi-Fi (OTA updates).
- Prevents anyone on your LAN from pushing firmware to the device without authorization.
- ESPHome generates one the first time if you don’t set it yourself.

---

### 7. Do I need MQTT?

Not at all.  This is in the example YAML files in case you want to access the data via MQTT topics.  By default, the ESPHome firmware discovers and talks via it's native API (not MQTT discovery).

---

### 8. What happens to the Vue device + entity records in HA if I rebuild the firmware?

As long as you build the firmware with:
- the same esphome.name (in YAML)
- the same sensor names (in YAML)
- and running on the same physical device

.. HA will reuse same entities.  You can reflash and switch between the ESPHome CLI and ESPHome Device Builder, and you will not lose sensor entities or data.  See next question for more details.

---

### 9. How do the device and entities work in HA for the Vue?

**The Device ID**
- comes from the firmware when it is discovered over the API (when you turn it on).
- It is based on this in the YAML file:  
  ```
  esphome:
    name: vue-utility
  ```
- HA makes a “device” record around that, so all the sensor entities are grouped.

**Entity IDs (e.g. sensor.vue_utility_watts)**
- Generated from each sensor defined in YAML
- They’re based on the device name + the component name.
- Example:  
  ```
  esphome:
    name: vue-utility

  sensor:
    - platform: emporia_vue_utility
      name: "Watts"
  ```
  gives sensor.vue_utility_watts.

**Unique IDs**

Under the hood, every device and entity in HA is allocated a unique ID.  Unique IDs for devices and entities in HA work differently, but for the Vue both are tied to the Vue's hardware MAC address:

**1. Device**
HA - the unique ID is generated and tied to the MAC address of the device.
- If you rename the device (e.g. 'vue-utility' to 'uncle_bob'), HA keeps the same underlying device, it will just be renamed.
- Let's say your Vue breaks and you buy another one, it will come with a different MAC address and a different device will be created in HA for it.

**2. Sensor entities**
Likewise, HA stores a unique ID for each sensor which is directly based on the MAC address of the device + sensor name.  e.g.
```
  {
    "entity_id": "sensor.vue_utility_watts",
    "unique_id": "20:60:AB:E5:12:24-sensor-watts"
  }
```

---
