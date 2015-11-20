# -*- coding: utf-8 -*-

# Simple ping program, do not support optional arguments.

from __future__ import print_function, division, absolute_import

import os
import time
import ctypes
import struct
import socket
import select
import signal

from .sigpending import sigpending


def _to_ascii(value):
    if isinstance(value, int):
        return value
    return ord(value)


class Ping(object):

    _ICMP_ECHO_REQUEST = 8
    _verbose_fmt = '{0} bytes from {1}: icmp_seq={2} ttl={3} time={4:.0f}ms'
    # "BBHBHd"
    _stp = struct.Struct('B')  # type(8bit)
    _scd = struct.Struct('B')  # code(8bit)
    _scs = struct.Struct('H')  # check sum(16bit)
    _sis = struct.Struct('B')  # icmp seq(8bit)
    _spid = struct.Struct('H')  # pid(cat /proc/sys/kernel/pid_max: 16bit)
    _sts = struct.Struct('d')  # time stamp(...64bit)
    _buffer_size = (_stp.size + _scd.size + _scs.size + _sis.size +
                    _spid.size + _sts.size)
    _sttl = struct.Struct('B')  # ttl(8bit)

    def __init__(self, addr):
        self._socket = socket.socket(socket.AF_INET,
                                     socket.SOCK_RAW,
                                     socket.IPPROTO_ICMP)
        self._pid = os.getpid()
        self._addr = addr
        self._max_icmp_seq = 255
        self._icmp_seq = self._received = 0
        self._start = self._end = 0

        self._buffer = ctypes.create_string_buffer(self._buffer_size)
        self._stp.pack_into(self._buffer, 0, self._ICMP_ECHO_REQUEST)
        self._scd.pack_into(self._buffer, self._stp.size, 0)
        self._spid.pack_into(self._buffer,
                             self._stp.size + self._scd.size +
                             self._scs.size + self._sis.size,
                             self._pid)

    def start(self, timeout=3):
        # ICMP packet + IP header
        size = self._buffer_size + 20
        addr = socket.gethostbyname(self._addr)
        print('PING {0} ({1}) {2} bytes of data.'.format(self._addr, addr, size))

        while self._icmp_seq < self._max_icmp_seq:
            try:
                with sigpending(signal.SIGINT):
                    self.ping_pong(addr, timeout)
            except KeyboardInterrupt:
                break
        self.report()

    def ping_pong(self, addr, timeout):
        origin_time = time.time()
        self._icmp_seq += 1
        self._socket.sendto(self.icmp(origin_time), (addr, 0))
        if self._start == 0:
            self._start = origin_time

        r, w, e = select.select([self._socket], [], [], timeout)
        if not r:
            self._end = time.time()
            return -1

        self._end = time.time()
        data, (host, _) = self._socket.recvfrom(512)
        ttl, type_, icmp_seq, pid, time_stamp = self._unpack_data(data)
        if pid != self._pid:  # or type_ != 0 ?
            return -1
        self._received += 1
        print(self._verbose_fmt.format(
            len(data), addr, icmp_seq, ttl, (self._end - time_stamp) * 1000))
        return 0

    def icmp(self, time_stamp):
        icmp_seq = self._icmp_seq
        data = self._make_icmp(0, icmp_seq, time_stamp)
        check_sum = self.check_sum(data)
        return self._make_icmp(check_sum, icmp_seq, time_stamp)

    def _make_icmp(self, check_sum, icmp_seq, time_stamp):
        self._scs.pack_into(self._buffer, self._stp.size + self._scd.size,
                            check_sum)
        self._sis.pack_into(self._buffer,
                            self._stp.size + self._scd.size + self._scs.size,
                            icmp_seq)
        self._sts.pack_into(self._buffer, self._buffer_size - self._sts.size,
                            time_stamp)
        return self._buffer.raw

    def _unpack_data(self, data, ip_len=20, ttl_offset=8):
        buffer = ctypes.create_string_buffer(data)
        ttl = self._sttl.unpack_from(buffer, ttl_offset)
        # IP Header: 20 bytes
        type_ = self._stp.unpack_from(buffer, ip_len)
        icmp_seq = self._sis.unpack_from(
            buffer, ip_len + self._stp.size + self._scd.size + self._scs.size)
        pid = self._spid.unpack_from(
            buffer, ip_len + self._stp.size + self._scd.size +
            self._scs.size + self._sis.size)
        time_stamp = self._sts.unpack_from(
            buffer, ip_len + self._buffer_size - self._sts.size)
        return ttl[0], type_[0], icmp_seq[0], pid[0], time_stamp[0]

    def check_sum(self, value):
        checksum = 0
        length = len(value)

        for idx in range(0, length, 2):
            if idx + 1 == length:
                checksum += _to_ascii(value[idx])
                break
            checksum += (_to_ascii(value[idx + 1]) << 8) + _to_ascii(value[idx])

        checksum = (checksum >> 16) + (checksum & 0xffff)
        checksum += (checksum >> 16)

        return ((~checksum) & 0xffff)

    def report(self):
        print('\n--- {0} ping statistics ---'.format(self._addr))
        loss_rate = (self._icmp_seq - self._received) / self._icmp_seq * 100
        fmt = ('{0} packets transmitted, {1} received, {2:.2f}% packet loss, '
               'time {3:.0f}ms')
        print(fmt.format(self._icmp_seq, self._received, loss_rate,
                         (self._end - self._start) * 1000))
