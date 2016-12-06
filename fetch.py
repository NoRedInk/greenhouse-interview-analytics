# -*- coding: utf-8 -*-
import time
import json

import requests

import db


session = requests.Session()


# TODO: account for rate limiting
def iter_list(*path_components, **kwargs):
    params = {'page': 1}
    params.update(kwargs)
    url = requests.compat.urljoin('https://harvest.greenhouse.io/v1/', '/'.join(map(str, path_components)))
    last_page = False
    while not last_page:
        time.sleep(0.2)
        print('GET', url, params)
        response = session.get(
            url,
            params=params)
        print('--->', len(response.json()), 'items')
        for item in response.json():
            yield item
        if 'next' in response.links:
            url = response.links['next']['url']
            params = {}  # clear out initial params
        else:
            last_page = True


def list_jobs(department):
    for job in iter_list('jobs'):
        if job_belongs_to_department(department, job):
            yield job


def job_belongs_to_department(department, job):
    return any(d['name'] == department for d in job['departments'] if d is not None)


def list_applications(table, job, only_new=True, only_active=True):
    params = dict(job_id=job['id'])
    if only_new:
        latest = table.find_one(job_id=job['id'], order_by=['-application_updated_at'])
        if latest:
            params['last_activity_after'] = latest['application_updated_at']
    for application in iter_list('applications', **params):
        if (not only_active) or application['status'] == 'active':
            yield application


def list_scorecards(application):
    return iter_list('applications', application['id'], 'scorecards')


def store_interview(table, job, application, scorecard):
    '''
    An interview is identified by `scorecard_id`.
    '''
    keys = dict(scorecard_id=scorecard['id'])
    interview = table.find_one(**keys)
    if interview:
        interview = update_interview(interview, job, application, scorecard)
        table.update(interview, ['id'])
    else:
        interview = update_interview(keys, job, application, scorecard)
        table.insert(interview)


def update_interview(interview, job, application, scorecard):
    '''
    Update the following columns:
      candidate_id
      scorecard_recommendation
      scorecard_ratings
      scorecard_questions
      interviewed_at
      interviewer_id
      interviewer_name
      interview_type
      job_id
      job_title
      application_id
      application_status
      application_updated_at
    '''
    new_interview = dict(interview)
    new_interview['candidate_id'] = application['candidate_id']
    new_interview['scorecard_recommendation'] = scorecard['overall_recommendation']
    new_interview['scorecard_ratings'] = json.dumps(scorecard['ratings'])
    new_interview['scorecard_questions'] = json.dumps(scorecard['questions'])
    new_interview['interviewed_at'] = scorecard['interviewed_at']
    new_interview['interviewer_id'] = scorecard['submitted_by']['id']
    new_interview['interviewer_name'] = scorecard['submitted_by']['name']
    new_interview['interview_type'] = scorecard['interview']
    new_interview['job_id'] = job['id']
    new_interview['job_title'] = job['name']
    new_interview['application_id'] = application['id']
    new_interview['application_status'] = application['status']
    new_interview['application_updated_at'] = application['last_activity_at']
    return new_interview


def main(args):
    table = db.interviews_table()
    for job in list_jobs(args.department):
        for application in list_applications(table, job, only_new=args.incremental, only_active=False):
            for scorecard in list_scorecards(application):
                store_interview(table, job, application, scorecard)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--department')
    parser.add_argument('--token')
    parser.add_argument('--all', dest='incremental', action='store_false', default=True)

    args = parser.parse_args()
    session.auth = (args.token, None)

    main(args)
