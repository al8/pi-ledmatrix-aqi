# pi-ledmatrix-aqi
Show Air Quality Index (AQI) information on a raspberry pi driven led matrix.

Shows time, current AQI, 10m average, 6 hour average, e.g.:

     03:13
    AQI 161
    10m avg
      167
      6Hav 115

# Usage

## dependencies

rpi-rgb-led-matrix, python-aqi, purpleair

clone and compile: https://github.com/hzeller/rpi-rgb-led-matrix

From there, we'll need to copy:
  rpi-rgb-led-matrix/examples-api-use/text-example
  rpi-rgb-led-matrix/fonts/4x6.bdf

python3 -m pip install python-aqi

## run

./getaqi.py <sensor_id>