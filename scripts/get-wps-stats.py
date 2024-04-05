#!/usr/bin/env python

import pymongo
import re
import datetime
import json
import argparse
from xml.etree import ElementTree


class WPSStatsGetter:

    def __init__(self):
        self._users = None
        dbclient = pymongo.MongoClient('127.0.0.1', 27027)
        self._db = dbclient['phoenix_db']
        self._ids = {}
        

    def get_jobs(self, key, regex):
        query = { key: { "$regex": regex, "$options" :'i' } }
        jobs = list(self._db.jobs.find(query))
        return [self.get_job_with_user(job) for job in jobs]


    def get_users(self):  #regex=".*"):
        if self._users:
            return self._users
    #    query = { "field": { "$regex": regex, "$options" :'i' } } 
        self._users = list(self._db.users.find())
        return self._users


    def get_job_with_user(self, job):
        job = job.copy()
        users = self.get_users()
        username = next(user["name"] for user in users
                        if user["identifier"] == job["userid"])
        job["username"] = username
        return job 


    def get_status(self, job):
        response = job["response"].decode('utf-8')
        m = re.search('<wps:(Process(?:Succeeded|Failed))>', response)
        if m:
            return m.group(1)
        else:
            raise Exception("Cannot get job status")


    def get_error_message(self, job):
        try:
            msg = job["status_message"]
        except IndexError:
            return None
        if not msg.startswith('Error: <?xml'):
            return None
        root = ElementTree.fromstring(msg[7:])
        for path, el in self.walk_xml(root):
            if self.path_to_str(path) == 'ExceptionReport.Exception.ExceptionText':
                el_parent = path[-2]
                msg1 = ', '.join(f'{var}={val}' for var, val in el_parent.items())
                msg2 = el.text
                return f'{msg1}, Exception text: {msg2}'
        return None
    
        
    def get_inputs(self, job):
        response = job["response"]
        if response is None:
            return None
        root = ElementTree.fromstring(response)
        inputs = {}        
        for path, el in self.walk_xml(root):
            if self.path_to_str(path) == 'ExecuteResponse.DataInputs.Input.Data.LiteralData':
                el_datainp = path[-3]
                try:
                    el_ident, = [ch for ch in el_datainp.getchildren()
                                    if self.get_short_tag(ch) == 'Identifier']
                except ValueError:
                    continue
                inputs[el_ident.text] = el.text

        return inputs


    def dump_job(self, job):
        for key in 'response', 'status_message':
            val = job.get(key)
            if val is not None:
                print(f'=== {key} ===')
                root = ElementTree.fromstring(val)
                self.dump_etree(root)
            
        
    def dump_etree(self, root):
        print("=====================")
        for path, el in self.walk_xml(root):            
            print(f'{self.path_to_str(path, with_ids=True)} text={el.text}, items={el.items()}')
        print("=====================")
            
            
    def path_to_str(self, path, with_ids=False):
        if with_ids:            
            return '.'.join(f'{self.get_short_tag(el)}[{self.get_short_id(el)}]'
                            for el in path)
        else:
            return '.'.join(f'{self.get_short_tag(el)}'
                            for el in path)

        
    def get_short_tag(self, el):
        return f'{el.tag[el.tag.index("}") + 1 :]}'

    
    def get_short_id(self, obj):
        oid = id(obj)
        if oid not in self._ids:
            self._ids[oid] = 1 + len(self._ids)
        return self._ids[oid]
            
    
    def walk_xml(self, el, path=None):
        if path is None:
            path = (el,)
        yield (path, el)
        for i, child in enumerate(el.getchildren()):
            yield from self.walk_xml(child, path + (child,))
        

    def get_job_times(self, job):
        times = {}
        for key in 'created', 'finished':
            val = job.get(key)
            if isinstance(val, datetime.datetime):
                times[key] = val.strftime("%Y-%m-%d %H:%M:%S")
        return times
    
            
    def get_job_info(self, job):
        job = job.copy()
        keys = ["username", "status", "process_id", "inputs", "times"]
        inputs = self.get_inputs(job)
        if inputs:
            job["inputs"] = inputs
        else:
            job["inputs"] = "Cannot parse inputs"
            keys.append('error')
            job["error"] = self.get_error_message(job) or "Cannot parse error message"
        job["times"] = self.get_job_times(job) or "Cannot parse times"
        return {key: job[key] for key in keys}
    
    def show_job_info(self, job_info, writer=None):
        msg = ', '.join(f'{k} = {v}' for k, v in job_info.items())
        if writer is not None:
            writer(msg + '\n')
        else:
            print(msg)

    def write_json(self, all_jobs_info, filename):
        data = {'num_jobs': len(all_jobs_info), 'jobs':all_jobs_info}
        with open(filename, 'w') as fout:
            json.dump(data, fout, indent=4)

    def get_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-o', '--output-prefix', default='wps_stats')
        return parser.parse_args()
        
    def main(self):
        args = self.get_args()
        txtfile = f'{args.output_prefix}.txt'
        jsonfile = f'{args.output_prefix}.json'

        jobs = self.get_jobs("process_id", "NAME")
        # users = self.get_users()
        all_jobs_info = []

        with open(txtfile, 'w') as fout:
            fout.write(f"Number of jobs: {len(jobs)}\n")
            for job in jobs:
                #print(self.get_status(job))
                job_info = self.get_job_info(job)
                all_jobs_info.append(job_info)
                self.show_job_info(job_info, writer=fout.write)
        
        self.write_json(all_jobs_info, jsonfile)
        print(f'wrote {txtfile} and {jsonfile}')

if __name__ == "__main__":
    wsg = WPSStatsGetter()
    wsg.main()

