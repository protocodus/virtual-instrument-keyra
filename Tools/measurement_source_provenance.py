"""Exact provenance for the existing AIFF and cropped-WAV recipes.

No resampling, gain, channel conversion or tolerance is allowed. The original
corpus pin is independent of the authored analysis-WAV pin. Container metadata
and decoded interleaved float64 PCM must agree with the declared transform.
The historical fitter's flac/wav fallback (including New York's literal None)
is retained ONLY for checking its old cache key, never as source verification.
"""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import tempfile

DECODERS = {
    'newyork-aiff-lossless-v1': ('newyork', '4f74f06be33be46e793a2d413c217de02dbf42ac5af1874d8691f24e790693d3', 44100),
    'hamburg-preset-crop-v1': ('hamburg', '88ad0e73e037aee99b5e3231600a426a6670fd71c0d1dc309d91fcfeac355eb7', 48000),
}
KINDS = {'newyork': 'newyork-aiff-lossless-v1', 'hamburg': 'hamburg-preset-crop-v1'}

class ProvenanceError(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise ProvenanceError(message)

def executable(name):
    """Use CMake's exact decoder path, or discover its CLI name on PATH."""
    require(name in ('ffmpeg', 'ffprobe'), 'unsupported decoder executable')
    requested = os.environ.get('KEYRA_MODEL_' + name.upper()) or name
    path = shutil.which(requested)
    require(path is not None, name + ' required for exact transformed-source proof: ' + requested)
    return str(Path(path).resolve())

def prepare(item, source, model, base, pins, pinned):
    """Hash/role-independent metadata validation; does not decode audio."""
    p = source['provenance']
    kind = p.get('kind')
    require(KINDS.get(model) == kind, 'unsupported model/source recipe')
    # This is exactly train_anchors()' historical cache recipe. AIFF source
    # identity was absent there; current original+decoded proofs close that gap.
    cache_pin = item.get('flac_sha256', item.get('wav_sha256'))
    require(p.get('historical_cache_pin', 'missing') == cache_pin, 'historical cache pin differs')
    wav = pinned(source['wav'], base, pins)
    result = {'kind': kind, 'model': model, 'case': source['id'], 'analysis_wav': str(wav),
              'analysis_wav_sha256': source['wav']['sha256'], 'historical_cache_pin': cache_pin}
    require(set(p) == {'kind', 'historical_cache_pin', 'original', 'decoder', 'sample_rate',
                       'channels', 'source_bits', 'analysis_bits', 'frame_span'}, 'transform fields differ')
    _, decoder_sha, rate = DECODERS[kind]
    decoder = pinned(p['decoder'], base, pins)
    require(p['decoder']['sha256'] == decoder_sha, 'decoder implementation not supported by this recipe version')
    original = pinned(p['original'], base, pins)
    field = 'aif_sha256' if model == 'newyork' else 'wav_sha256'
    require(item.get(field) == p['original']['sha256'], 'original source differs from corpus')
    require(type(p['sample_rate']) is int and p['sample_rate'] == rate, 'declared sample rate differs from recipe')
    require(type(p['channels']) is int and p['channels'] == 2, 'declared channels differ from recipe')
    require(type(p['source_bits']) is int and type(p['analysis_bits']) is int, 'invalid bit depth')
    span = p['frame_span']
    require(isinstance(span, list) and len(span) == 2 and all(type(v) is int for v in span)
            and 0 <= span[0] < span[1], 'invalid frame span')
    if model == 'newyork':
        require(p['source_bits'] in (16, 24) and p['analysis_bits'] == p['source_bits'], 'AIFF depth conversion forbidden')
        require(span[0] == 0, 'AIFF trimming forbidden')
    else:
        require(p['source_bits'] == 24 and p['analysis_bits'] == 32, 'Hamburg requires original24/analysis32 bit PCM')
        require(type(item.get('start')) is int and item['start'] >= 0, 'invalid corpus preset start')
        require(span[0] == max(0, item['start'] - round(.02 * rate)), 'crop does not match corpus start minus20ms')
    result.update(original=str(original), original_sha256=p['original']['sha256'],
                  original_corpus_field=field, original_corpus_source=item['source'],
                  decoder=str(decoder), decoder_sha256=decoder_sha,
                  sample_rate=rate, channels=2, source_bits=p['source_bits'],
                  analysis_bits=p['analysis_bits'], frame_span=span)
    return result

def probe(path):
    command = [executable('ffprobe'), '-v', 'error', '-show_entries',
               'format=format_name:stream=codec_type,codec_name,sample_rate,channels,bits_per_sample,bits_per_raw_sample',
               '-of', 'json', str(path)]
    value = json.loads(subprocess.run(command, check=True, capture_output=True, text=True).stdout)
    audio = [s for s in value['streams'] if s.get('codec_type') == 'audio']
    require(len(audio) == 1, 'exactly one audio stream required')
    s = audio[0]
    return {'container': value['format']['format_name'], 'codec': s['codec_name'],
            'sample_rate': int(s['sample_rate']), 'channels': int(s['channels']),
            'bits': int(s.get('bits_per_raw_sample') or s.get('bits_per_sample') or 0)}

def pcm(path, channels, span=None):
    """Decode without transform; select exact whole frames in Python bytes."""
    command = [executable('ffmpeg'), '-v', 'error', '-nostdin', '-i', str(path), '-map', '0:a:0',
               '-c:a', 'pcm_f64le', '-f', 'f64le', 'pipe:1']
    frame_bytes = 8 * channels
    full, selected = hashlib.sha256(), hashlib.sha256()
    count = kept = 0
    with tempfile.TemporaryFile() as errors:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=errors)
        try:
            while True:
                data = process.stdout.read(65536 * frame_bytes)
                if not data:
                    break
                require(len(data) % frame_bytes == 0, 'decoder returned fractional frame')
                frames = len(data) // frame_bytes
                full.update(data)
                lo = 0 if span is None else max(0, span[0] - count)
                hi = frames if span is None else min(frames, span[1] - count)
                if hi > lo:
                    selected.update(data[lo*frame_bytes:hi*frame_bytes])
                    kept += hi - lo
                count += frames
            code = process.wait()
            errors.seek(0)
            require(code == 0, 'PCM decoder failed: ' + errors.read().decode(errors='replace'))
        finally:
            process.stdout.close()
            if process.poll() is None:
                process.terminate()
                process.wait()
    return {'frames': count, 'full_pcm_sha256': full.hexdigest(),
            'selected_frames': kept, 'selected_pcm_sha256': selected.hexdigest(),
            'representation': 'interleaved stereo normalized float64 little-endian, no dither/gain/resampling'}

def verify(record):
    """Exact streaming proof, after ALL manifest source roles/hashes pass."""
    a, b = probe(record['original']), probe(record['analysis_wav'])
    for label, value, bits in [('original', a, record['source_bits']), ('analysis', b, record['analysis_bits'])]:
        require(value['sample_rate'] == record['sample_rate'], label + ' sample rate mismatch')
        require(value['channels'] == record['channels'], label + ' channel mismatch')
        require(value['bits'] == bits, label + ' bit depth mismatch')
    a_container = 'aiff' if record['kind'] == 'newyork-aiff-lossless-v1' else 'wav'
    a_codec = 'pcm_s' + str(record['source_bits']) + ('be' if a_container == 'aiff' else 'le')
    b_codec = 'pcm_s' + str(record['analysis_bits']) + 'le'
    require(a['container'] == a_container and a['codec'] == a_codec, 'original container/PCM encoding mismatch')
    require(b['container'] == 'wav' and b['codec'] == b_codec, 'analysis container/PCM encoding mismatch')
    original = pcm(record['original'], record['channels'], record['frame_span'])
    analysis = pcm(record['analysis_wav'], record['channels'])
    begin, end = record['frame_span']
    require(end == original['frames'] and begin < end, 'declared span must end at original final frame')
    require(original['selected_frames'] == end - begin == analysis['frames'], 'analysis frame count differs from exact transform')
    require(original['selected_pcm_sha256'] == analysis['full_pcm_sha256'], 'decoded PCM differs from declared lossless transform')
    return dict(record, original_format=a, analysis_format=b, original_pcm=original,
                analysis_pcm=analysis, exact_pcm_identity=True, transformed=True)

def runtime():
    result = {}
    for name in ['ffmpeg', 'ffprobe']:
        path = executable(name)
        digest = hashlib.sha256()
        with Path(path).open('rb') as source:
            for block in iter(lambda: source.read(1024 * 1024), b''):
                digest.update(block)
        result[name] = {'path': path, 'sha256': digest.hexdigest(),
                        'version': subprocess.run([path, '-version'], check=True, capture_output=True, text=True).stdout.splitlines()[0]}
    return result
