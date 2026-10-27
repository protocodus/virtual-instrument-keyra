from pathlib import Path
import argparse, datetime, hashlib, json, os, subprocess

ROOT = Path('/workspace/virtual-instrument-keyra')
RACK = Path('/workspace/reason-rack-extensions')
OUT = ROOT/'out/full-free-unison-fusion/integration'
CMAKE = '/home/agent/.local/bin/cmake'

def record(path):
    path = Path(path)
    return {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('kind', choices=['native', 'asan', 'reason'])
    kind = parser.parse_args().kind
    folder = OUT/kind
    folder.mkdir(parents=True, exist_ok=False)
    files = [ROOT/p for p in ['CMakeLists.txt', 'src/full_instrument/PreparedModel.h',
        'src/full_instrument/FreeUnisonFusion.h', 'src/full_instrument/FullInstrument.cpp',
        'src/full_instrument/generate_prepared_model.py', 'src/full_instrument/free_unison_transform.py',
        'src/full_instrument/SelectedModel.h', 'src/full_instrument/MechanismBodyCache.h',
        'include/keyra/FullInstrument.h', 'tests/full_instrument_tests.cpp', 'tests/full_profile_tests.cpp',
        'tools/render_full.cpp']]
    if kind == 'reason':
        files += [RACK/p for p in ['Prototypes/Keyra/CMakeLists.txt',
            'Prototypes/Keyra/Keyra.cpp', 'Prototypes/Keyra/Keyra.h',
            'Prototypes/Keyra/tests/FullWrapperHost.cpp', 'Prototypes/Keyra/tests/full_build_policy.py']]
    freeze = [record(path) for path in files]
    (folder/'freeze.json').write_text(json.dumps(freeze, indent=2)+'\n')
    def verify():
        for item in freeze:
            assert record(item['path']) == item, item['path']
    commands = []
    def run(command, name, env=None):
        verify()
        print(kind+' '+name, flush=True)
        call = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
        log = folder/(name+'.log')
        log.write_text(call.stdout)
        commands.append({'command': command, 'log': record(log), 'exit_code': call.returncode})
        verify()
        if call.returncode:
            raise RuntimeError(str(log)+' exit '+str(call.returncode))
    try:
        common = ['-DCMAKE_BUILD_TYPE=Release', '-DBUILD_TESTING=ON', '-DCMAKE_EXPORT_COMPILE_COMMANDS=ON']
        build = folder/'build'
        if kind == 'reason':
            run([CMAKE, '-S', str(RACK/'Prototypes/Keyra'), '-B', str(build), *common,
                 '-DKEYRA_BUILD_EXPERIMENTAL_FULL_MODEL=ON', '-DKEYRA_INSTRUMENT_DIR='+str(ROOT)], 'configure')
            targets = ['keyra_rack_host', 'keyra_rack_full_host', 'keyra_rack_full_scalar_host']
            regex = '^keyra_reason_'
        else:
            run([CMAKE, '-S', str(ROOT), '-B', str(build), *common,
                 '-DKEYRA_BUILD_REFERENCE=OFF', '-DKEYRA_BUILD_FULL_REFERENCE=OFF',
                 '-DKEYRA_BUILD_PHYSICAL=OFF', '-DKEYRA_BUILD_CLAP=OFF',
                 '-DKEYRA_SANITIZERS='+('ON' if kind == 'asan' else 'OFF')], 'configure')
            targets = ['keyra_full_instrument_tests', 'keyra_full_profile_tests']
            if kind == 'native':
                targets += ['keyra_full_sdk_compat_tests', 'keyra_full_render']
            regex = '^(full_instrument|full_model_profile'+('|full_sdk_portable' if kind == 'native' else '')+')$'
        run([CMAKE, '--build', str(build), '--target', *targets, '-j', '1'], 'build')
        env = os.environ.copy()
        if kind == 'asan':
            env['ASAN_OPTIONS'] = 'detect_leaks=1:strict_string_checks=1'
            env['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
        run(['ctest', '--test-dir', str(build), '--output-on-failure', '-R', regex], 'tests', env)
        passed = True
        error = None
    except Exception as exc:
        passed = False
        error = str(exc)
    result = {'kind': kind, 'passed': passed, 'error': error, 'commands': commands,
              'freeze': record(folder/'freeze.json'), 'tests_are_host_approximations': True,
              'Reason_SDK_or_Recon_run': False,
              'finished_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (folder/'result.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)
    if not passed:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
