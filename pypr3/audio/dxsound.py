# qaqFei/Phispler

# type: ignore

from __future__ import annotations


import wave
import subprocess
import math
import warnings
from typing import Literal
from io import BytesIO


import win32comext.directsound.directsound as ds
import win32event as w32e
import numpy as np
from pywintypes import WAVEFORMATEX


CACHE_BUFFER_MAXSIZE = 32
PRE_CACHE_SIZE = CACHE_BUFFER_MAXSIZE
RING_BUFFER = True

dxs = ds.DirectSoundCreate(None, None)
dxs.SetCooperativeLevel(None, ds.DSSCL_NORMAL)


def _decode_audio_with_ffmpeg(data: bytes) -> tuple[np.ndarray, int, int]:
    cmd = [
        "ffmpeg",
        "-i", "pipe:0",
        "-f", "wav",
        "-acodec", "pcm_s16le",
        "pipe:1",
    ]

    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    stdout, stderr = proc.communicate(data)

    if proc.returncode != 0:
        raise RuntimeError(
            f"ffmpeg failed (code {proc.returncode}): {stderr.decode('utf-8', errors='ignore')}"
        )

    with wave.open(BytesIO(stdout), "rb") as wf:
        channels = wf.getnchannels()
        samplerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    samples = samples.reshape(-1, channels)

    return samples, samplerate, channels


def _loadDirectSound(data: bytes):
    sdesc = ds.DSBUFFERDESC()

    audio_data, samplerate, nchannels = _decode_audio_with_ffmpeg(data)

    audio_data = np.clip(audio_data, -1, 1)
    audio_data = (audio_data * 32767).astype(np.int16)

    bufdata = audio_data.tobytes()

    wfx = WAVEFORMATEX()
    wfx.wFormatTag = 1
    wfx.nChannels = nchannels
    wfx.nSamplesPerSec = samplerate
    wfx.nAvgBytesPerSec = samplerate * nchannels * 2
    wfx.nBlockAlign = nchannels * 2
    wfx.wBitsPerSample = 16

    sdesc.lpwfxFormat = wfx

    if len(bufdata) > ds.DSBSIZE_MAX:
        warnings.warn(
            f"Sound buffer size is too large ({len(bufdata)} > {ds.DSBSIZE_MAX}), truncated.",
            RuntimeWarning
        )
        bufdata = bufdata[:ds.DSBSIZE_MAX]

    sdesc.dwBufferBytes = len(bufdata)

    return bufdata, sdesc


class DirectSound:
    def __init__(self, data: bytes | str, enable_cache: bool = True):
        if isinstance(data, str):
            data = open(data, "rb").read()

        (
            self._bufdata,
            self._sdesc
        ) = _loadDirectSound(data)

        self._sdesc.dwFlags = ds.DSBCAPS_CTRLVOLUME | ds.DSBCAPS_CTRLPOSITIONNOTIFY | ds.DSBCAPS_GLOBALFOCUS | ds.DSBCAPS_GETCURRENTPOSITION2

        self._enable_cache = enable_cache
        self._volume = 0  # -10000 ~ 0
        self._buffers = []

        if self._enable_cache:
            self._buffers.extend(self._create() for _ in range(PRE_CACHE_SIZE))

    def _create(self):
        event = w32e.CreateEvent(None, 0, 0, None)
        buffer = dxs.CreateSoundBuffer(self._sdesc, None)
        buffer.QueryInterface(
            ds.IID_IDirectSoundNotify).SetNotificationPositions((-1, event))
        buffer.Update(0, self._bufdata)
        buffer.SetVolume(self._volume)
        return event, buffer

    def create(self, playMethod: Literal[0, 1]):
        if self._enable_cache:
            if len(self._buffers) > CACHE_BUFFER_MAXSIZE:
                for i in reversed(self._buffers):
                    e, buf = i
                    if buf.GetStatus() == 0:
                        try:
                            self._buffers.remove(i)
                        except ValueError:
                            continue
                        break

            if self._buffers:
                for e, buf in self._buffers:
                    if buf.GetStatus() == 0:
                        buf.SetVolume(self._volume)
                        buf.SetCurrentPosition(0)
                        buf.Play(playMethod)
                        return e, buf

                if RING_BUFFER:
                    e, buf = self._buffers[0]
                    buf.Stop()
                    buf.SetVolume(self._volume)
                    buf.SetCurrentPosition(0)
                    buf.Play(playMethod)
                    return e, buf

        event, buffer = self._create()
        buffer.Play(playMethod)
        if self._enable_cache:
            self._buffers.append((event, buffer))
        return event, buffer

    def transform_volume(self, v: float):
        if v <= 1e-5:
            return ds.DSBVOLUME_MIN
        if v >= 1.0:
            return ds.DSBVOLUME_MAX
        return int(2000 * math.log10(v))

    def set_volume(self, v: float):
        self._volume = self.transform_volume(v)

    def play(self, wait: bool = False, playMethod: Literal[0, 1] = 0):
        event, buffer = self.create(playMethod)

        if wait:
            w32e.WaitForSingleObject(event, -1)

        return event, buffer
