# Meter Response Payload

There are at least two known response payloads sent by the MGM111 chip. MGM Firmware version 2 sends a 152 byte payload while version 7 sends a 45 byte payload. Check the section below relevant to your version.

## Payload for Version 2

The meter reading response contains 152 bytes of payload, most of which seem to always be zeros.  The fields in the payload have
a mix of sizes and just to make things more confusing, the use of LSB / MSB byte ordering is inconsistent.  
The below table details the payload format that's been reversed engineered so far.
Blank cells have never been seen to be anything other than zero.  Note the table is zero-indexed (starts at byte zero, not byte 1)

<table  style="width:20%">
  <tr>   <td></td>
            <th align="center"><img width="50" height="1">0<img width="50" height="1"></th>
            <th align="center"><img width="50" height="1">1<img width="50" height="1"></th>
            <th align="center"><img width="50" height="1">2<img width="50" height="1"></th>
            <th align="center"><img width="50" height="1">3<img width="50" height="1"></th>
  </tr>
  <tr>   <th>0</th> <td colspan=4></td></tr>
  <tr>   <th>4</th> <td colspan=4 align="center">EnergyVal</td></tr>
  <tr>   <th>...</th> <td colspan=4></td></tr>
  <tr>   <th>44</th> <td colspan=3></td><td align="center">MeterDiv</td></tr>
  <tr>   <th>48</th> <td colspan=2></td><td colspan=2 align="center">EnergyCostUnit</td></tr>
  <tr>   <th>52</th> <td colspan=2 align="center">Unknown 1</td><td colspan=2></td></tr>
  <tr>   <th>56</th> <td></td><td colspan=3 align="center">PowerVal</td></tr>
  <tr>   <th>...</th> <td colspan=4></td></tr>
  <tr>   <th>148</th> <td colspan=4 align="center">MeterTS</td></tr>
</table>

### Known Fields

#### EnergyVal

Bytes 4 to 8, 32 bit int, unknown if signed, MSB

Energy Meter totalizer in watts, in other words, cumulative watt-hours consumed.  Unknown when this value resets to zero, 
might reset monthly or on start of new billing cycle.

Sometimes, an invalid number greater than `0x00400000` is returned, it is not understood when or why this happens.

#### MeterDiv

At least byte 47, maybe as large as bytes 44 to 47

Some meters report values not in watts and watt hours but in a multiple of those values.  `EnergyVal` and `PowerVal` should 
be divided by `MeterDiv` to determine the real value.  Usually this is 1, but have also seen a value of 3.

#### EnergyCostUnit

Bytes 50 and 51 MSB(?)

Usually `0x03E8`, which is 1000.  Theorized to be how many `EvergyVal` units per "cost unit" (a value we don't appear to have).
Since people are typically charged per kWh, this value is typically 1000.

This value is not currently used in the code

#### PowerVal

Bytes 57 to 59 (24 bit signed int, MSB)

The power being consumed at the moment in Watts.  If you have a grid-tie solar / wind / battery system, then this value can go negative.
Negative values are returned in 1's complement notation (if left most bit is 1, then flip all the bits then multiply by -1)

"Data Missing" / "Unknown" is denoted as max negative, `0x800000`

#### MeterTS

Bytes 148 to 151 (32 bit unsigned int, LSB)

Number of milliseconds since an unknown event.  Could be time since `EnergyVal` was reset, or could just be a free-running timer.
Will roll over every 49 days.

Only reported as a debugging value, not used in calculations.

#### Unknown 1

Bytes 52 and 53

The meaning of the values in these fields is completely unknown.  They appear to be static for each meter.  Some of the observed values from users include:
```
fbfb
2c2b
3133
```
Random uneducated guess is that this is a bit field with flags about the meter configuration.

## Payload for Version 7

The meter reading response contains 45 bytes of payload, most of which seem to always be zeros. The table below details the payload format that's been reversed engineered so far.
Blank cells have never been seen to be anything other than zero. Some cells have hex codes that I have never seen change, but might differ for you. Note the table is zero-indexed (starts at byte zero, not byte 1).

<table  style="width:80%">
  <tr>   <td></td>
            <th align="center"><img width="50" height="1">0<img width="50" height="1"></th>
            <th align="center"><img width="50" height="1">1<img width="50" height="1"></th>
            <th align="center"><img width="50" height="1">2<img width="50" height="1"></th>
            <th align="center"><img width="50" height="1">3<img width="50" height="1"></th>
  </tr>
  <tr>   <th>0</th> <td colspan=1 align="center">0x18</td><td colspan=1 align="center">Incrementor</td><td colspan=1 align="center">0x01</td><td colspan=1></tr>
  <tr>   <th>4</th> <td colspan=2></td><td colspan=1 align="center">0x25</td><td colspan=1 align="center">ImportWh~</td></tr>
  <tr>   <th>8</th> <td colspan=1 align="center">~ImportWh</td><td colspan=1 align="center">0x16</td><td colspan=1 align="center">0x09</td><td colspan=1></td></tr>
  <tr>   <th>12</th> <td colspan=1></td><td colspan=1 align="center">0x01</td><td colspan=2></td></tr>
  <tr>   <th>16</th> <td colspan=1></td><td colspan=2 align="center">ExportWh</td><td colspan=1 align="center">0x97</td></tr>
  <tr>   <th>20</th> <td colspan=3></td><td colspan=1 align="center">0x01</td></tr>
  <tr>   <th>24</th> <td colspan=1 align="center">0x03</td><td colspan=1></td><td colspan=1 align="center">0x22</td><td colspan=1 align="center">0x01</td></tr>
  <tr>   <th>28</th> <td colspan=2></td><td colspan=1 align="center">0x02</td><td colspan=1 align="center">0x03</td></tr>
  <tr>   <th>32</th> <td colspan=1></td><td colspan=1 align="center">0x22</td><td colspan=1 align="center">0xE8</td><td colspan=1 align="center">0x03</td></tr>
  <tr>   <th>36</th> <td colspan=1></td><td colspan=1></td><td colspan=1 align="center">0x04</td><td colspan=1></td></tr>
  <tr>   <th>40</th> <td colspan=1></td><td colspan=3 align="center">PowerVal</td></tr>
</table>

### Known Fields

#### ImportWh

Bytes 7 to 8, (16 bit int, probably unsigned, LSB)

Cumulative watt-hours consumed from the grid. Unknown when the value resets, but probably never resets since ESP32 never sends a clock sync to the MGM111 so it likely just rolls over.

#### ExportWh

Bytes 17 to 18, (16 bit int, probably unsigned, LSB)

Cumulative watt-hours sent to the grid. Unknown when the value resets, but probably never resets since ESP32 never sends a clock sync to the MGM111 so it likely just rolls over.

#### PowerVal

Bytes 41 and 43 (24 bit signed int, LSB)

The power being sent or consumed at this moment. This is in watts for me but I know in the V2 payload that there is a `MeterDiv`, which means `PowerVal` might be a multiplication of the real wattage. If V7 also has this behavior then `MeterDiv` must have a value of 1 in my readings. So, `MeterDiv` might be byte 2, 13, 23, or 27.

#### Incrementor

Byte 1 (8 bit unsigned int)

This just increments by 1 on each reading and rolls over.