# ESPHome Emporia Vue Utility Connect Unofficial Firmware

This is an unauthorized and unoffical firmware for the Emporia View Utility Connect device that reports energy usage to Home Assistant and completely divorces the device from Emporia's servers.

## Disclaimer

There is no guarantee of quality.   When you install the software on your device, it will no longer report data to Emporia.  You should backup the original Emporia firmware before installing this.

## Backup the original firmware

Determine which COM device your USB to serial adapter is and use it in the below command(s). Typically a single digit number. (e.g. `COM3`)

Backup:

`.\esptool --port COM# --chip esp32 -b 115200 read_flash 0x0 0x400000 .\vueUtilityConnect_stock.bin`

Restore:

`.\esptool --port COM# --chip esp32 -b 115200 write_flash --flash_freq 80m 0x0 .\vueUtilityConnect_stock.bin`

## Installation

Connect a your USB to serial adapter to the port marked "P3" as follows:

| Pin | Description | USB-Serial port |
| --- |  ---------  | --------------- |
|  1  |        IO0  |             RTS |
|  2  |         EN  |             DTR |
|  3  |        GND  |             GND |
|  4  |         TX  |              RX |
|  5  |         RX  |              TX |
|  6  |        +5v  |             +5v |

Note that pin 6 (the pin just above the text "EmporiaEnergy") is 5 volts, not 3.3v.  Use caution not to apply 5V to the wrong pin or
the magic smoke may come out.  You may want to not connect pin 6 at all and instead plug the device into a usb port to provide power,
a portable USB battery pack works well for this.

Instead of connecting IO0 and EN, you can simply short IO0 to ground while connecting power to get the device into bootloader mode.

Use either YAML file in the `example_yaml` directory and modify it to your liking.

Execute `esphome run vue-utility.yaml` or `esphome run vue-utility-solar.yaml` to build and install.

## YAML configuration

This sensor component provides **6** output values and takes **3** configuration options.

A full configuration can look like this:
```yaml
# Boilerplate UART configuration.
uart:
  id: emporia_uart
  rx_pin: GPIO21
  tx_pin: GPIO22
  baud_rate: 115200

# The actual sensor configuration.
sensor:
  - platform: emporia_vue_utility
    uart_id: emporia_uart
    debug: true
    update_interval: 15s
    power:
      name: "${name} Watts"
    power_export:
      name: "${name} Watts Returned"
    power_import:
      name: "${name} Watts Consumed"
    energy:
      name: "${name} Wh Net"
    energy_export:
      name: "${name} Wh Returned"
    energy_import:
      name: "${name} Wh Consumed"
```

Note: You likely do not need all of these fields.

### Outputs

The output values are all *optional* and categorized into instantaneous power (aka. watts) and total energy usage (aka. watt-hours) in "import", "export", and "net" variations. Their relationship is: `net = import - export`

#### Watts
- **power** = Net watt usage at that moment in time. Is negative if you have excess solar generation.
- **power_import** = Watt usage from the grid at that moment in time. Is `0` if your solar generation currently exceeds your usage.
- **power_export** = Watts sent to the grid at that moment in time. Is `0` if you are using more than your solar is generating.

#### Watt-hours
This is a total energy usage count for the lifetime of your utility meter. The only situations where the count will decrease is if the 32bit value experiences an integer overflow, or if your utility meter is replaced with a new one. For either situation, it is expected that the count(s) will reset to `0`.

- **energy** = Total net watt-hour usage.
- **energy_import** = Total watt-hours taken from the grid.
- **energy_export** = Total watt-hours sent to the grid. Is perpetually `0` if you don't have solar generation.

### Configurations

#### UART

We need to talk to the MGM chip that talks to the utility meter. This chip is connected to the ESP via `GPIO21` and `GPIO22` and the configuration is:
```yaml
uart:
  id: emporia_uart
  rx_pin: GPIO21
  tx_pin: GPIO22
  baud_rate: 115200
```

Then, within the `sensor:` configuration, you can add `uart_id: emporia_uart`. I believe it is optional if there is only one `uart:` defined.

Example with `uart_id` added:
```yaml
sensor:
  - platform: emporia_vue_utility
    uart_id: emporia_uart
    ...
```

#### Poll rate

The `update_interval` lets you define the rate at which we ask the utility meter for a new reading. This defaults to `30` seconds, which is also the default in the Emporia stock firmware.

Note that the utility meter has its own update rate, and if you poll more frequently it will just give you the same value as before. Some users report being able to receive new values every 5 seconds while I only see a new value every 15 seconds. You are welcome to trial-and-error and see how frequently you can get updated values and settle on a value that makes sense to you.

Example with `update_interval` added:
```yaml
sensor:
  - platform: emporia_vue_utility
    update_interval: 15s
    ...
```

#### Debug logs

Add `debug: true` if you need to see additional details about issues you're experiencing.

When enabled, each reading will cause the log to output something like this:
```
[00:05:17][D][emporia_vue_utility:360]: Meter Cost Unit: 1000
[00:05:17][D][emporia_vue_utility:361]: Meter Divisor: 1
[00:05:17][D][emporia_vue_utility:362]: Meter Energy Import Flags: 00596680
[00:05:17][D][emporia_vue_utility:363]: Meter Energy Export Flags: 0078f478
[00:05:17][D][emporia_vue_utility:364]: Meter Power Flags: 00038d2a
[00:05:17][D][emporia_vue_utility:365]: Meter Import Energy: 5858.944kWh
[00:05:17][D][emporia_vue_utility:366]: Meter Export Energy: 7926.904kWh
[00:05:17][D][emporia_vue_utility:367]: Meter Net Energy: -2067.960kWh
[00:05:17][D][emporia_vue_utility:368]: Meter Power:  909W
[00:05:17][D][emporia_vue_utility:377]: Meter Response Bytes   0 to   3: 18 91 01 00
[00:05:17][D][emporia_vue_utility:377]: Meter Response Bytes   4 to   7: 00 00 25 80
[00:05:17][D][emporia_vue_utility:377]: Meter Response Bytes   8 to  11: 66 59 00 00
[00:05:17][D][emporia_vue_utility:377]: Meter Response Bytes  12 to  15: 00 01 00 00
[00:05:17][D][emporia_vue_utility:377]: Meter Response Bytes  16 to  19: 25 78 f4 78
[00:05:17][D][emporia_vue_utility:377]: Meter Response Bytes  20 to  23: 00 00 00 01
[00:05:17][D][emporia_vue_utility:377]: Meter Response Bytes  24 to  27: 03 00 22 01
[00:05:17][D][emporia_vue_utility:377]: Meter Response Bytes  28 to  31: 00 00 02 03
[00:05:17][D][emporia_vue_utility:377]: Meter Response Bytes  32 to  35: 00 22 e8 03
[00:05:17][D][emporia_vue_utility:377]: Meter Response Bytes  36 to  39: 00 00 04 00
[00:05:17][D][emporia_vue_utility:377]: Meter Response Bytes  40 to  43: 2a 8d 03 00
```

Example with `debug` added:
```yaml
sensor:
  - platform: emporia_vue_utility
    debug: true
    ...
```

## Meaning of LEDs

There are three LEDs on the device, which have "power", "wifi" and "link" icons stenciled on the case.
* **Power** = An ESPHome status led.  Slowly flashing means warning, quickly flashing means error, solid on means OK.  See [status_led](https://esphome.io/components/status_led.html) docs.
* **Wifi** = Normally solid on, will briefly flash each time a meter rejoin is attempted which indicates poor signal from the meter.
* **Link** = Flashes off briefly about once every 5 seconds.  More specifically, the LED turns off when a reading from the meter is requested and turns back on when a response is received.  If no response is received then the LED will remain off.  If this LED is never turning on then no readings are being returned by the meter.

## More Details

Check out the `docs` directory for technical details!
