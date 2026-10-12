import copy
import io
import json
from pathlib import Path
import shutil
import unittest
from unittest.mock import patch

from weft import batches, qualification as q, screening
from weft.discovery import Store
from weft.__main__ import main
import test_batches
import test_reading

XML = test_reading.XML.replace(b'</sec>', b'''<fig id="f1"><label>Figure 1</label><caption><p>One pooled library per condition.</p></caption><graphic xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="fig1.jpg"/></fig>
<supplementary-material id="s1" xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="supp.pdf"><label>Supplement 1</label><caption><p>Methods and sample table.</p></caption></supplementary-material></sec>''')


class QualificationTests(unittest.TestCase):
    setUp = test_batches.BatchTests.setUp
    create = test_batches.BatchTests.create
    run_batch = test_batches.BatchTests.run_batch
    response = test_batches.BatchTests.response
    screen = test_batches.BatchTests.screen

    def prepared(self):
        bid=self.create();self.run_batch(bid);issued,_=self.screen(bid)
        cid=issued['packet']['candidate_id']
        read=screening.read_packet(self.store,bid,cid,fetch=lambda _:XML)
        assessment=test_reading.ReadingTests.assessment(self,{**read,'directory':read['resolved_directory']})
        screening.submit_reading(self.store,bid,assessment)
        packet=q.issue(self.store,bid,cid)
        record=copy.deepcopy(packet['response_template'])
        record.update(actor='fixture',prior_exposure='Synthetic development test')
        return bid,cid,packet,record

    def citation(self,packet):
        s=packet['packet']['segments'][0]
        return {'locator':s['locator'],'segment_sha256':s['sha256']}

    def descriptive(self,packet,record):
        record=copy.deepcopy(record);refs=[self.citation(packet)]
        for c in record['coverage']:
            c.update(status='not_required',inspection_note='Synthetic scoped description uses a source table; image interpretation excluded')
        record['data'].update(comparison='Condition A versus B',measured_endpoint='Observed transcript abundance',
                              biological_unit='Pooled library',independent_units='pooled_only',controls='documented',
                              access='documented',citations=refs,recommendation='review_required',
                              datasets=[{'accession':'GSE_FIXTURE','file_identifiers':['counts.tsv'],
                                         'unit_mapping':'pooled_only','cohort':'fixture-pool',
                                         'source_relationship':'shared_source','citations':refs}])
        return record

    def test_inventory_template_hold_and_idempotent_packet(self):
        bid,cid,packet,record=self.prepared()
        self.assertEqual([r['kind'] for r in packet['packet']['resources']],['figure','supplement'])
        self.assertEqual(packet['packet']['resources'][0]['hrefs'],['fig1.jpg'])
        self.assertEqual(packet,q.issue(self.store,bid,cid))
        result=q.submit(self.store,bid,record)
        self.assertEqual(len(result['coverage_holds']),2)
        self.assertIsNone(result['independent_study_count'])
        self.assertFalse(result['scientific_execution_allowed'])

    def test_complete_explicit_coverage_required(self):
        bid,cid,packet,record=self.prepared()
        for coverage in [[],record['coverage']*2,[{**record['coverage'][0],'resource_id':'invented'}]]:
            with self.subTest(coverage=coverage),self.assertRaises(ValueError):q.submit(self.store,bid,{**record,'coverage':coverage})

    def test_caption_and_missing_artifact_never_become_pixels(self):
        bid,cid,packet,record=self.prepared();c=record['coverage'][0]
        c['status']='caption_only'
        self.assertEqual(q.submit(self.store,bid,record)['reviewed_resources'],0)
        c['status']='inspected'
        with self.assertRaisesRegex(ValueError,'retained artifact'):q.submit(self.store,bid,record)
        file=Path(self.temp.name)/'caption.txt';file.write_text('caption')
        attached=q.attach(self.store,bid,cid,c['resource_id'],file,'synthetic fixture caption')
        c['artifact_id']=attached['artifact_id']
        with self.assertRaisesRegex(ValueError,'pixels or PDF'):q.submit(self.store,bid,record)

    def test_attachment_binding_hash_and_format(self):
        bid,cid,packet,record=self.prepared();c=record['coverage'][0]
        file=Path(self.temp.name)/'figure.png';file.write_bytes(b'\x89PNG\r\n\x1a\nsynthetic bytes, not rendered')
        result=q.attach(self.store,bid,cid,c['resource_id'],file,'synthetic PNG signature fixture')
        self.assertEqual(q.attach(self.store,bid,cid,c['resource_id'],file,'synthetic PNG signature fixture')['status'],'already_recorded')
        c.update(status='inspected',artifact_id=result['artifact_id'],inspection_note='Synthetic attestation; format signature alone is not image validation')
        self.assertEqual(q.submit(self.store,bid,record)['reviewed_resources'],1)
        record['coverage'][1].update(status='inspected',artifact_id=result['artifact_id'])
        with self.assertRaisesRegex(ValueError,'bound'):q.submit(self.store,bid,record)
        blob=next(self.store.root.glob('evidence-*/source.bin'));blob.write_bytes(b'changed')
        self.assertFalse(q.summary(self.store,bid,cid)['current'])

    def test_attachment_bounds_unknown_resource_and_active_content(self):
        bid,cid,packet,record=self.prepared();file=Path(self.temp.name)/'f.txt';file.write_text('fixture')
        with self.assertRaisesRegex(ValueError,'Unknown source'):q.attach(self.store,bid,cid,'bad',file,'fixture')
        with patch.object(q,'MAX_ARTIFACT',2),self.assertRaises(ValueError):q.attach(self.store,bid,cid,record['coverage'][0]['resource_id'],file,'fixture')
        file=file.with_suffix('.html');file.write_text('<script>untrusted</script>')
        with self.assertRaises(ValueError):q.attach(self.store,bid,cid,record['coverage'][0]['resource_id'],file,'fixture')

    def test_pooled_description_does_not_pass_population_or_perturbation(self):
        bid,cid,packet,record=self.prepared();record=self.descriptive(packet,record)
        result=q.submit(self.store,bid,record)
        self.assertEqual(result['data_proposal'],'review_required')
        self.assertEqual(result['rq_proposal'],'hold')
        self.assertEqual(result['analysis_readiness'],'not_assessed')
        record['data']['inference']='replicated_population'
        with self.assertRaisesRegex(ValueError,'Unresolved'):q.submit(self.store,bid,record)
        record['data'].update(inference='descriptive',purpose='perturbation_effect',controls='absent')
        with self.assertRaisesRegex(ValueError,'Unresolved'):q.submit(self.store,bid,record)

    def test_missing_mapping_access_and_shared_source_never_counts_as_replication(self):
        bid,cid,packet,record=self.prepared();record=self.descriptive(packet,record)
        for key,value in [('access','restricted'),('biological_unit',None)]:
            changed=copy.deepcopy(record);changed['data'][key]=value
            with self.assertRaises(ValueError):q.submit(self.store,bid,changed)
        changed=copy.deepcopy(record);changed['data']['datasets'][0]['unit_mapping']='unknown'
        with self.assertRaises(ValueError):q.submit(self.store,bid,changed)
        record['data']['datasets']*=2
        with self.assertRaisesRegex(ValueError,'Duplicate accession'):q.submit(self.store,bid,record)

    def test_endpoint_mismatch_cannot_be_presented_as_review_ready(self):
        bid,cid,packet,record=self.prepared();record=self.descriptive(packet,record)
        compat=record['rq_compatibility'];compat.update(relation='adjacent',recommendation='review_required')
        for d in compat['dimensions'].values():d.update(status='match',citations=[self.citation(packet)])
        compat['dimensions']['endpoint']['status']='mismatch'
        with self.assertRaisesRegex(ValueError,'Unresolved'):q.submit(self.store,bid,record)
        compat['recommendation']='hold'
        result=q.submit(self.store,bid,record)
        self.assertIn('endpoint:mismatch',result['rq_holds'])
        self.assertEqual(result['data_proposal'],'review_required')

    def test_citation_identity_and_authority_fail_closed(self):
        bid,cid,packet,record=self.prepared()
        for changes in [{'scientific_execution_allowed':True},{'claim_validated':True},
                        {'packet_sha256':'bad'},{'run_code':'not allowed'},{'actor_identity_verified':True}]:
            with self.subTest(changes=changes),self.assertRaises(ValueError):q.submit(self.store,bid,{**record,**changes})
        record=self.descriptive(packet,record)
        record['data']['citations'][0]['locator']='/invented'
        with self.assertRaisesRegex(ValueError,'citation'):q.submit(self.store,bid,record)

    def test_amendments_preserve_history_and_late_replay_is_not_current(self):
        bid,cid,packet,record=self.prepared();first=q.submit(self.store,bid,record)
        self.assertEqual(q.submit(self.store,bid,record)['status'],'already_recorded')
        updated=copy.deepcopy(record);updated['limitations'].append('Additional disclosed limit')
        with self.assertRaisesRegex(ValueError,'latest'):q.submit(self.store,bid,updated)
        updated.update(previous_record_sha256=first['record_sha256'],amendment_reason='Versioned correction')
        second=q.submit(self.store,bid,updated)
        replay=q.submit(self.store,bid,record)
        self.assertFalse(replay['current'])
        self.assertEqual(q.summary(self.store,bid,cid)['record_sha256'],second['record_sha256'])
        self.assertEqual(self.store.db.execute('SELECT COUNT(*) FROM evidence_reviews').fetchone()[0],2)

    def test_stale_metadata_and_external_disposition_hold_saved_proposal(self):
        bid,cid,packet,record=self.prepared();q.submit(self.store,bid,record)
        with self.store.db:self.store.db.execute("UPDATE candidates SET status='held' WHERE id=?",(cid,))
        self.assertFalse(q.summary(self.store,bid,cid)['current'])
        with self.assertRaises(ValueError):q.submit(self.store,bid,record)

    def test_source_tamper_blocks_review_and_digest_marks_hold(self):
        bid,cid,packet,record=self.prepared();q.submit(self.store,bid,record)
        next(self.store.root.glob('reading-*/source.xml')).write_bytes(b'changed')
        status=batches.status_report(self.store,bid)['items'][0]['evidence_qualification']
        self.assertEqual(status['status'],'hold');self.assertFalse(status['current'])
        with self.assertRaises(ValueError):q.issue(self.store,bid,cid)

    def test_relocated_store_replays_without_fetch_or_duplicate_events(self):
        bid,cid,packet,record=self.prepared()
        file=Path(self.temp.name)/'supplement.csv';file.write_text('sample,unit\nfixture,pooled\n')
        c=record['coverage'][1]
        artifact=q.attach(self.store,bid,cid,c['resource_id'],file,'Synthetic sample table')
        c.update(status='inspected',artifact_id=artifact['artifact_id'],inspection_note='Synthetic table inspected')
        result=q.submit(self.store,bid,record)
        destination=Path(self.temp.name)/'new-host';shutil.copytree(self.store.root,destination)
        before=self.store.db.execute('SELECT COUNT(*) FROM batch_events').fetchone()[0]
        with Store(destination) as other,patch('urllib.request.urlopen',side_effect=AssertionError('No network')):
            self.assertEqual(q.issue(other,bid,cid),packet)
            self.assertEqual(q.submit(other,bid,record)['status'],'already_recorded')
            self.assertEqual(q.summary(other,bid,cid)['record_sha256'],result['record_sha256'])
            self.assertEqual(other.db.execute('SELECT COUNT(*) FROM batch_events').fetchone()[0],before)

    def test_stale_age_preserves_saved_record(self):
        bid,cid,packet,record=self.prepared();q.submit(self.store,bid,record)
        with self.store.db:self.store.db.execute("UPDATE runs SET finished='2020-01-01T00:00:00+00:00'")
        self.assertFalse(q.summary(self.store,bid,cid)['current'])
        with self.assertRaisesRegex(ValueError,'older'):q.submit(self.store,bid,record)
        self.assertEqual(self.store.db.execute('SELECT COUNT(*) FROM evidence_reviews').fetchone()[0],1)

    def test_linked_attachment_target_rejected(self):
        bid,cid,packet,record=self.prepared();file=Path(self.temp.name)/'supplement.csv';file.write_text('fixture')
        c=record['coverage'][1];q.attach(self.store,bid,cid,c['resource_id'],file,'Synthetic fixture')
        blob=next(self.store.root.glob('evidence-*/source.bin'));saved=blob.with_name('preserved.bin');blob.rename(saved)
        try:blob.symlink_to(saved)
        except OSError:
            saved.rename(blob)
            self.skipTest('Symlink creation unavailable on this host')
        with self.assertRaisesRegex(ValueError,'Linked'):
            q.attach(self.store,bid,cid,c['resource_id'],file,'Synthetic fixture')

    def test_cli_packet_and_status(self):
        bid,cid,packet,record=self.prepared()
        with patch('sys.stdout',new_callable=io.StringIO) as out:
            self.assertEqual(main(['batch-evidence','--store',str(self.store.root),'--batch',bid,'--candidate',cid]),0)
        self.assertEqual(json.loads(out.getvalue())['packet_sha256'],packet['packet_sha256'])
        q.submit(self.store,bid,record)
        with patch('sys.stdout',new_callable=io.StringIO) as out:
            self.assertEqual(main(['batch-evidence-status','--store',str(self.store.root),'--batch',bid,'--candidate',cid]),0)
        self.assertFalse(json.loads(out.getvalue())['scientific_execution_allowed'])
