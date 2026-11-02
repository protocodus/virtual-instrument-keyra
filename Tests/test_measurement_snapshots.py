"""Public stored-number regeneration contracts; no source recordings/caches."""
from pathlib import Path
import copy
import gzip
import hashlib
import json
import os
import pickle
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE/'Tools'))
import update_modal_measurements as u
import regenerate_modal_measurements as r
import fit_realtime_modal as fit

class Snapshots(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.parent=HERE/'Tests/Fixtures/measurements/belmont-accepted.json.gz';self.archive=u.read_archive(self.parent)

    def save(self,value):
        path=self.root/'snapshot.json.gz';path.write_bytes(gzip.compress(u.json_bytes(u.encode(value)),mtime=0));return path

    def child_recipe(self):
        values=copy.deepcopy(self.archive['measurements'])
        values['anchors'][0]['partials'][0]['lanes'][0]['level_db'][0]+=.125
        content=fit.header(fit.MODELS['belmont'],**values)
        manifest=self.root/'update.json'
        analysis=self.root/'analysis.py';analysis.write_text('# synthetic operator identity, never executed\n')
        manifest.write_bytes(u.json_bytes({'schema':u.MANIFEST,
            'analysis':{'path':analysis.name,'sha256':u.digest(analysis)},
            'fitter':{'path':str(Path(fit.__file__).resolve()),'sha256':u.digest(fit.__file__)}}))
        receipt={'model':'belmont','accepted_archive_path':str(self.parent),'accepted_archive_sha256':u.digest(self.parent),
                 'output_sha256':hashlib.sha256(content.encode()).hexdigest(),'manifest_path':str(manifest),
                 'input_pins':{str(p):u.digest(p) for p in [self.parent,manifest,analysis,Path(fit.__file__),
                              Path(u.__file__).with_name('import_modal_measurements.py').absolute()]}}
        return content,receipt

    def child(self):
        content,receipt=self.child_recipe()
        path=self.root/'child.json.gz';path.write_bytes(u.snapshot(content,receipt))
        return path,content,receipt

    def test_original_snapshot_exact(self):
        content,receipt=r.regenerate(self.parent,'belmont',fit.header,fit.MODELS['belmont'])
        self.assertEqual(receipt['header_sha256'],self.archive['provenance']['header_sha256'])

    def test_updated_numbers_and_parent_provenance_exact(self):
        path,expected,update=self.child();a=u.read_archive(path)
        self.assertEqual(a['provenance']['parent_archive_sha256'],u.digest(self.parent))
        self.assertEqual(a['provenance']['parent_header_sha256'],self.archive['provenance']['header_sha256'])
        self.assertEqual(a['provenance']['update_receipt_sha256'],hashlib.sha256(u.json_bytes(update)).hexdigest())
        self.assertNotIn('metadata_sha256',a['provenance'])
        content,_=r.regenerate(path,'belmont',fit.header,fit.MODELS['belmont']);self.assertEqual(content,expected)
        self.assertEqual(u.read_archive(self.parent),self.archive)

    def test_no_cache_or_audio_calls(self):
        path,expected,_=self.child()
        with patch.object(pickle,'load',side_effect=AssertionError('cache accessed')),patch.object(u.source_provenance,'verify',side_effect=AssertionError('audio accessed')):
            content,receipt=r.regenerate(path,'belmont',fit.header,fit.MODELS['belmont'])
        self.assertEqual(content,expected);self.assertEqual(receipt['source_audio_reads'],0);self.assertEqual(receipt['raw_cache_reads'],0)

    def test_model_rejected(self):
        with self.assertRaisesRegex(u.InvalidInput,'model mismatch'):r.regenerate(self.parent,'newyork',fit.header,fit.MODELS['newyork'])

    def test_snapshot_cannot_change_during_stored_number_regeneration(self):
        path=self.root/'changing.json.gz';shutil.copyfile(self.parent,path)
        def changed(model,**values):
            content=fit.header(model,**values);path.write_bytes(b'changed during formatting');return content
        with self.assertRaisesRegex(u.InvalidInput,'snapshot changed during regeneration'):
            r.regenerate(path,'belmont',changed,fit.MODELS['belmont'])

    def test_wrong_header_digest_rejected(self):
        a=copy.deepcopy(self.archive);a['provenance']['header_sha256']='0'*64
        with self.assertRaisesRegex(u.InvalidInput,'SHA differs'):r.regenerate(self.save(a),'belmont',fit.header,fit.MODELS['belmont'])

    def test_child_missing_parent_digest_rejected(self):
        path,_,_=self.child();a=u.read_archive(path);del a['provenance']['parent_header_sha256']
        with self.assertRaisesRegex(u.InvalidInput,'provenance'):r.regenerate(self.save(a),'belmont',fit.header,fit.MODELS['belmont'])

    def test_stale_metadata_label_rejected(self):
        path,_,_=self.child();a=u.read_archive(path);a['provenance']['metadata_sha256']='0'*64
        with self.assertRaisesRegex(u.InvalidInput,'historical metadata'):r.regenerate(self.save(a),'belmont',fit.header,fit.MODELS['belmont'])

    def test_no_implicit_source_recalibration(self):
        result=subprocess.run([sys.executable,str(HERE/'Tools/fit_realtime_modal.py'),'--model','belmont'],capture_output=True,text=True)
        self.assertEqual(result.returncode,2);self.assertIn('--recalibrate',result.stderr)

    def test_measurements_cli_and_check(self):
        path,expected,_=self.child();out=self.root/'out.h';metadata=self.root/'out.json'
        command=self.command(path,out)+['--metadata',str(metadata)]
        subprocess.run(command,check=True,capture_output=True);self.assertEqual(out.read_text(),expected)
        subprocess.run(command+['--check'],check=True,capture_output=True)
        # JSON whitespace is not provenance; complete field values/types are.
        value=u.read_json(metadata);metadata.write_text(json.dumps(value,separators=(',',':')))
        subprocess.run(command+['--check'],check=True,capture_output=True)

    def test_measurements_publish_exact_bytes_without_platform_newline_translation(self):
        path,expected,_=self.child()
        header=self.root/'portable.h';metadata=self.root/'portable.json'
        _,receipt=r.regenerate(path,'belmont',fit.header,fit.MODELS['belmont'])
        argv=['fit_realtime_modal','--model','belmont','--measurements',str(path),
              '--header',str(header),'--metadata',str(metadata)]
        # Path.write_text's default newline translation changes LF to CRLF on
        # Windows. The archive hashes UTF-8/LF bytes, so publication must avoid
        # that platform-dependent path even on our Linux/macOS test runners.
        with (patch.object(sys,'argv',argv),
              patch.object(Path,'write_text',side_effect=AssertionError('platform text writer used'))):
            fit.main()
        self.assertEqual(header.read_bytes(),expected.encode('utf-8'))
        self.assertEqual(metadata.read_bytes(),
                         (json.dumps(receipt,indent=2,allow_nan=False)+'\n').encode('utf-8'))

    def command(self,archive,header):
        return [sys.executable,str(HERE/'Tools/fit_realtime_modal.py'),'--model','belmont',
                '--measurements',str(archive),'--header',str(header)]

    def test_measurements_check_rejects_incomplete_changed_or_extra_metadata(self):
        content,receipt=r.regenerate(self.parent,'belmont',fit.header,fit.MODELS['belmont'])
        header=self.root/'out.h';header.write_text(content);metadata=self.root/'out.json'
        variants=[{},dict(receipt,header_sha256='0'*64),dict(receipt,undeclared_volatile='ignored?'),
                  dict(receipt,raw_cache_reads=False)]
        for value in variants:
            with self.subTest(value=value):
                metadata.write_bytes(u.json_bytes(value))
                result=subprocess.run(self.command(self.parent,header)+['--metadata',str(metadata),'--check'],capture_output=True,text=True)
                self.assertNotEqual(result.returncode,0);self.assertIn('Metadata differs',result.stderr)
                self.assertEqual(header.read_text(),content)

    def alias(self,path,target,kind):
        if kind=='same':return target
        if kind=='symlink':path.symlink_to(target)
        elif kind=='hardlink':os.link(target,path)
        return path

    def test_measurement_outputs_cannot_alias_archive(self):
        archive=self.root/'input.gz';shutil.copyfile(self.parent,archive);before=archive.read_bytes()
        for kind in ['same','symlink','hardlink']:
            for output in ['header','metadata']:
                with self.subTest(kind=kind,output=output):
                    alias=self.alias(self.root/(kind+output),archive,kind)
                    header=alias if output=='header' else self.root/('new-'+kind+'.h')
                    command=self.command(archive,header)
                    if output=='metadata':command+=['--metadata',str(alias)]
                    result=subprocess.run(command,capture_output=True,text=True)
                    self.assertNotEqual(result.returncode,0);self.assertIn('output aliases input',result.stderr)
                    self.assertEqual(archive.read_bytes(),before)
                    if output=='metadata':self.assertFalse(header.exists())

    def test_measurement_outputs_cannot_alias_each_other_even_when_missing(self):
        for kind in ['same','symlink']:
            with self.subTest(kind=kind):
                header=self.root/(kind+'.h');metadata=self.alias(self.root/(kind+'.json'),header,kind)
                result=subprocess.run(self.command(self.parent,header)+['--metadata',str(metadata)],capture_output=True,text=True)
                self.assertNotEqual(result.returncode,0);self.assertIn('outputs alias each other',result.stderr)
                self.assertFalse(header.exists())

    def test_snapshot_rejects_manifest_changed_after_generation(self):
        content,receipt=self.child_recipe();manifest=Path(receipt['manifest_path'])
        value=u.read_json(manifest);value['analysis']['sha256']='2'*64;manifest.write_bytes(u.json_bytes(value))
        with self.assertRaisesRegex(u.InvalidInput,'input changed'):u.snapshot(content,receipt)

    def test_snapshot_rejects_changed_operator_or_other_input(self):
        for changed in ['analysis.py','other-input']:
            with self.subTest(changed=changed):
                content,receipt=self.child_recipe();path=self.root/changed
                if changed=='other-input':
                    path.write_bytes(b'original source pin');receipt['input_pins'][str(path)]=u.digest(path)
                path.write_bytes(b'changed')
                with self.assertRaisesRegex(u.InvalidInput,'input changed'):u.snapshot(content,receipt)

    def test_snapshot_requires_named_operators_in_receipt_pins(self):
        content,receipt=self.child_recipe();del receipt['input_pins'][str(self.root/'analysis.py')]
        with self.assertRaisesRegex(u.InvalidInput,'missing/conflicting input pin'):u.snapshot(content,receipt)

    def test_snapshot_requires_operator_hash_consistent_with_receipt(self):
        content,receipt=self.child_recipe();manifest=Path(receipt['manifest_path']);value=u.read_json(manifest)
        value['analysis']['sha256']='2'*64;manifest.write_bytes(u.json_bytes(value))
        receipt['input_pins'][str(manifest)]=u.digest(manifest)
        with self.assertRaisesRegex(u.InvalidInput,'operator identity differs'):u.snapshot(content,receipt)

    def test_snapshot_checks_pins_again_after_import(self):
        content,receipt=self.child_recipe();actual_module=u.module
        def changed_module(name,path):
            importer=actual_module(name,path);actual_load=importer.load
            def changed(header):
                result=actual_load(header);(self.root/'analysis.py').write_text('# changed during import\n');return result
            importer.load=changed
            return importer
        with patch.object(u,'module',side_effect=changed_module):
            with self.assertRaisesRegex(u.InvalidInput,'input changed'):u.snapshot(content,receipt)

    def test_snapshot_ignores_shadow_importers_and_preserves_exact_numbers(self):
        content,receipt=self.child_recipe()
        shadow=self.root/'historical';shadow.mkdir()
        (shadow/'import_modal_measurements.py').write_bytes(
            b"raise AssertionError('sys.path shadow importer executed')\n")
        impostor=types.ModuleType('import_modal_measurements')
        def wrong_load(path):
            raise AssertionError('cached shadow importer executed')
        impostor.load=wrong_load
        # Cover both a historical operator's sys.path entry and prior cached
        # modules. Even the internal explicit-loader name must be replaced.
        for cached in [False,True]:
            with self.subTest(cached=cached):
                modules=dict(sys.modules)
                modules.pop('import_modal_measurements',None)
                if cached:
                    modules['import_modal_measurements']=impostor
                modules['_keyra_snapshot_importer']=impostor
                with (patch.object(sys,'path',[str(shadow)]+sys.path),
                      patch.dict(sys.modules,modules,clear=True),
                      patch.object(Path,'write_text',side_effect=AssertionError('platform text writer used'))):
                    packed=u.snapshot(content,receipt)
                snapshot=self.root/('shadow-'+str(cached)+'.gz');snapshot.write_bytes(packed)
                actual,_=r.regenerate(snapshot,'belmont',fit.header,fit.MODELS['belmont'])
                self.assertEqual(actual.encode('utf-8'),content.encode('utf-8'))

    def test_snapshot_requires_sibling_importer_pin_before_loading(self):
        content,receipt=self.child_recipe()
        importer=Path(u.__file__).with_name('import_modal_measurements.py').absolute()
        del receipt['input_pins'][str(importer)]
        with patch.object(u,'module',side_effect=AssertionError('unpinned importer loaded')):
            with self.assertRaisesRegex(u.InvalidInput,'missing/conflicting input pin'):
                u.snapshot(content,receipt)

    def test_snapshot_checks_content_receipt_identity(self):
        content,receipt=self.child_recipe()
        with self.assertRaisesRegex(u.InvalidInput,'content differs'):u.snapshot(content+'\n',receipt)

if __name__=='__main__':unittest.main(verbosity=2)
