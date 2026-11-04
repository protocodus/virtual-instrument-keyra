"""CLI output safety contracts: synthetic bytes only, no source audio or fit."""
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / 'Tools'))
import archive_modal_measurements as archive
import update_modal_measurements as update


class OutputSafety(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'protected.bin'
        self.source.write_bytes(b'protected source bytes')

    def alias(self, name, target, kind):
        path = self.root / name
        if kind == 'same':
            return target
        if kind == 'symlink':
            path.symlink_to(target)
        else:
            os.link(target, path)
        return path

    def test_resolved_directory_symlink_alias(self):
        link = self.root / 'directory'
        link.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(update.InvalidInput, 'output aliases input'):
            update.protect_outputs([link / self.source.name], [self.source])

    def test_existing_hardlinked_outputs_are_rejected(self):
        link = self.alias('hardlink', self.source, 'hardlink')
        with self.assertRaisesRegex(update.InvalidInput, 'outputs alias each other'):
            update.protect_outputs([self.source, link], [])

    def test_archive_rejects_every_source_alias_before_loading_operators(self):
        names = ['header', 'metadata', 'corpus', 'split', 'fitter', 'analysis', 'importer']
        inputs = {name: self.root / (name + '.input') for name in names}
        for name, path in inputs.items():
            path.write_bytes(name.encode())
        original = {name: path.read_bytes() for name, path in inputs.items()}
        for name, path in inputs.items():
            for kind in ['same', 'symlink', 'hardlink']:
                with self.subTest(input=name, kind=kind):
                    output = self.alias(name + '-' + kind, path, kind)
                    argv = ['archive', '--model', 'hamburg', '--output', str(output)]
                    for key, value in inputs.items():
                        argv += ['--' + key, str(value)]
                    with patch.object(sys, 'argv', argv), patch.object(update, 'operators', side_effect=AssertionError('operator loaded')):
                        with self.assertRaisesRegex(update.InvalidInput, 'output aliases input'):
                            archive.main()
                    self.assertEqual({key: value.read_bytes() for key, value in inputs.items()}, original)

    def test_update_rejects_every_output_input_alias_before_any_publish(self):
        for name in ['header', 'receipt', 'snapshot']:
            for kind in ['same', 'symlink', 'hardlink']:
                for check in [False, True]:
                    with self.subTest(output=name, kind=kind, check=check):
                        outputs = {key: self.root / (key + f'-{name}-{kind}-{check}')
                                   for key in ['header', 'receipt', 'snapshot']}
                        outputs[name] = self.alias(f'alias-{name}-{kind}-{check}', self.source, kind)
                        argv = ['update', '--manifest', str(self.source)]
                        for key, value in outputs.items():
                            argv += ['--' + key, str(value)]
                        if check:
                            argv.append('--check')
                        receipt = {'input_pins': {str(self.source): update.digest(self.source)}}
                        with (patch.object(sys, 'argv', argv), patch.object(update, 'generate', return_value=('header', receipt)),
                              patch.object(update, 'publish', side_effect=AssertionError('published before alias checks'))):
                            with self.assertRaisesRegex(update.InvalidInput, 'output aliases input'):
                                update.main()
                        self.assertEqual(self.source.read_bytes(), b'protected source bytes')
                        self.assertTrue(all(not path.exists() for key, path in outputs.items() if key != name))

    def test_update_rejects_each_output_pair_before_any_publish(self):
        for first, second in [('header', 'receipt'), ('header', 'snapshot'), ('receipt', 'snapshot')]:
            for kind in ['same', 'symlink']:
                with self.subTest(first=first, second=second, kind=kind):
                    outputs = {key: self.root / f'{key}-{first}-{second}-{kind}'
                               for key in ['header', 'receipt', 'snapshot']}
                    outputs[second] = self.alias(f'pair-{first}-{second}-{kind}', outputs[first], kind)
                    argv = ['update', '--manifest', str(self.source)]
                    for key, value in outputs.items():
                        argv += ['--' + key, str(value)]
                    receipt = {'input_pins': {str(self.source): update.digest(self.source)}}
                    with (patch.object(sys, 'argv', argv), patch.object(update, 'generate', return_value=('header', receipt)),
                          patch.object(update, 'publish', side_effect=AssertionError('published before alias checks'))):
                        with self.assertRaisesRegex(update.InvalidInput, 'outputs alias each other'):
                            update.main()
                    self.assertTrue(all(not path.exists() for path in outputs.values()))

    def test_update_snapshot_failure_cannot_publish_header_or_receipt(self):
        header, receipt_path, snapshot = [self.root / name for name in ['new.h', 'receipt.json', 'snapshot.gz']]
        argv = ['update', '--manifest', str(self.source), '--header', str(header), '--receipt', str(receipt_path), '--snapshot', str(snapshot)]
        receipt = {'input_pins': {str(self.source): update.digest(self.source)}}
        with (patch.object(sys, 'argv', argv), patch.object(update, 'generate', return_value=('header', receipt)),
              patch.object(update, 'snapshot', side_effect=update.InvalidInput('input changed')),
              patch.object(update, 'publish', side_effect=AssertionError('published before snapshot validation'))):
            with self.assertRaisesRegex(update.InvalidInput, 'input changed'):
                update.main()
        self.assertFalse(any(path.exists() for path in [header, receipt_path, snapshot]))


if __name__ == '__main__':
    unittest.main(verbosity=2)
