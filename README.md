metar-clock
===========

Clock-like display of METAR data.

This project is intended to run on a Raspberry Pi with a Noritake CU-U type VFD connected to an asynchronous serial port. The serial port is logic level, so a level converter must be used between the RPi (3.3VDC) and the VFD (5VDC).

It's quick and dirty, but expecially for those looking for quick ways to hook up stuff like the VFD to an RPi, it might be helpful.
