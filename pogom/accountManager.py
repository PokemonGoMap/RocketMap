#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import time

from collections import OrderedDict, deque
from datetime import datetime, timedelta
from requests import Session
from threading import Lock, Thread
from timeit import default_timer

from .account import AccountBanned, check_login, setup_api
from .altitude import get_altitude
from .models import Account, Token
from .utils import distance
from .transform import jitter_location

log = logging.getLogger(__name__)


class AccountManager(object):
    def __init__(self, args, db_queue, wh_queue, high_level=30):

        self.args = args
        self.dbq = db_queue
        self.whq = wh_queue
        self.key_scheduler = None
        self.high_level = high_level
        self.instance_id = args.instance_id

        self.allocated = {
            'scanner': set(),
            'high-level': set()
        }

        self.active = {
            'scanner': OrderedDict(),
            'high-level': OrderedDict(),
        }

        self.accounts = {
            'scanner': OrderedDict(),
            'high-level': OrderedDict(),
            'failed': deque(),
            'captcha': deque()
        }

        self.accounts_locks = {
            'scanner': Lock(),
            'high-level': Lock()
        }

    def run_manager(self):
        # Release accounts previously used by this instance.
        self._release_instance()
        # Load required accounts to start working.
        self._account_keeper(notice=True)
        time.sleep(10)
        # Captcha solver current thread ID.
        self.thread_id = 0

        # Run account management cycle every 15 seconds.
        run_manager_interval = 15
        # Display warnings once every 5 minutes.
        notice_interval = 300
        notice_timer = default_timer()
        # Run account recycler once every 60 seconds.
        account_recycler_interval = 60
        account_recycler_timer = default_timer()
        # Run account monitor once every 10 minutes.
        account_monitor_interval = 600
        account_monitor_timer = default_timer()

        while True:
            now = default_timer()

            display_notice = False
            if now - notice_timer > notice_interval:
                display_notice = True
                notice_timer = default_timer()

            self._account_keeper(notice=display_notice)
            if self.args.captcha_solving:
                self._captcha_manager()

            if now - account_recycler_timer > account_recycler_interval:
                self._account_recycler()
                account_recycler_timer = default_timer()

            if now - account_monitor_timer > account_monitor_interval:
                self._account_monitor()
                account_monitor_timer = default_timer()

            time.sleep(run_manager_interval)

    def _account_keeper(self, notice=False):
        log.debug('Account keeper running. ' +
                  'Managing %d scanner and %d high-level accounts.',
                  len(self.allocated['scanner']),
                  len(self.allocated['high-level']))
        try:
            self._replenish_accounts(False, notice)
            self._replenish_accounts(True, notice)

            self._release_accounts(False)
            self._release_accounts(True)
        except KeyError as e:
            log.exception('Account manager lost track of an account: %s.', e)
        except Exception as e:
            log.exception('Account keeper critical fail: %s.', e)

    def _replenish_accounts(self, hlvl, notice):
        if hlvl:
            account_pool = 'high-level'
            target_count = self.args.hlvl_workers
        else:
            account_pool = 'scanner'
            target_count = self.args.workers

        available_count = (len(self.active[account_pool]) +
                           len(self.accounts[account_pool]))
        replenish_count = target_count - available_count

        if replenish_count <= 0:
            return

        accounts = self._fetch_accounts(replenish_count, hlvl)
        log.debug('Fetched %d %s accounts from database.',
                  len(accounts), account_pool)

        missing_count = replenish_count - len(accounts)
        if notice and missing_count:
            log.warning('Insufficient available accounts in database. ' +
                        'Unable to replenish %d %s accounts.',
                        missing_count, account_pool)

    # Check for excess accounts that can be released from this instance.
    def _release_accounts(self, hlvl):
        if hlvl:
            account_pool = 'high-level'
            holding_time = self.args.hlvl_workers_holding_time
            target_count = self.args.hlvl_workers
        else:
            account_pool = 'scanner'
            holding_time = self.args.workers_holding_time
            target_count = self.args.workers

        accounts_lock = self.accounts_locks[account_pool]
        allocated_pool = self.allocated[account_pool]
        active_pool = self.active[account_pool]
        spare_pool = self.accounts[account_pool]

        released_accounts = {}
        with accounts_lock:
            available_count = (len(active_pool) + len(spare_pool))
            excess_count = available_count - target_count

            if excess_count <= 0:
                return

            for username in spare_pool.keys():
                account = spare_pool[username]
                hold_time = (datetime.utcnow() -
                             account['last_modified']).total_seconds()
                if hold_time > holding_time:
                    # Release account from this instance.
                    account = spare_pool.pop(username)
                    account['allocated'] = False
                    allocated_pool.remove(username)
                    log.info('Released %s account %s from this instance. ' +
                             'Waited idle for %d seconds.',
                             account_pool, username, hold_time)

                    released_accounts[username] = Account.db_format(account)
                    excess_count -= 1
                else:
                    # Don't need to check further, account pool is sorted.
                    break
                if excess_count == 0:
                    break

        if released_accounts:
            # Update account information in database.
            self.dbq.put((Account, released_accounts))
            log.debug('Released %d excess %s accounts from this instance.',
                      len(released_accounts), account_pool)

    # Monitor failed accounts to check their status.
    def _account_recycler(self):
        now = datetime.utcnow()
        failed_count = len(self.accounts['failed'])
        log.debug('Account recycler running. Checking status of %d accounts.',
                  failed_count)

        # Define maximum ban level allowed to continue working.
        if not self.args.shadow_ban_scan:
            ban_level = AccountBanned.Clear
        else:
            ban_level = AccountBanned.Shadowban

        # Search through failed pool for recyclable accounts.
        while failed_count > 0:
            account, reason, notified = self.accounts['failed'].popleft()
            failed_count -= 1

            rest_interval = self.args.account_rest_interval

            if 'exception' in reason:
                rest_interval = rest_interval * 0.1
            elif 'login' in reason:
                rest_interval = self.args.login_timeout * 3600
            elif account['banned'] != AccountBanned.Clear:
                rest_interval = rest_interval * 10

            hold_time = (account['last_modified'] +
                         timedelta(seconds=rest_interval))

            if now < hold_time:
                if not notified:
                    time = (hold_time - now).total_seconds()
                    log.info('Account %s needs to stop (%s) for %.0f minutes.',
                             account['username'], reason, time/60)
                    notified = True

                self.accounts['failed'].append((account, reason, notified))
                continue

            if account['banned'] > ban_level:
                # Release banned accounts from this instance.
                account_pool = account['account_pool']
                log.info('Released banned %s account %s from this instance.',
                         account_pool, account['username'])
                account['allocated'] = False
                self.allocated[account_pool].remove(account['username'])
            else:
                if account['level'] >= self.high_level:
                    account_pool = 'high-level'
                else:
                    account_pool = 'scanner'

                # Return account to the appropriate account pool.
                log.info('Returning %s account %s to spare account pool.',
                         account_pool, account['username'])

                account['account_pool'] = account_pool
                spare_pool = self.accounts[account_pool]
                accounts_lock = self.accounts_locks[account_pool]

                with accounts_lock:
                    spare_pool[account['username']] = account

            # Update account information in database.
            self.dbq.put((Account, {0: Account.db_format(account)}))

    def _account_monitor(self):
        # Reset allocated accounts after one day.
        query = (Account
                 .update(allocated=False)
                 .where((Account.last_modified <
                         (datetime.utcnow() - timedelta(days=1))))
                 .execute())
        log.debug('Reseted %d old allocated accounts.', query)

        # Reset warning after one week.
        query = (Account
                 .update(allocated=False, failed=0, warning=False)
                 .where((Account.warning == 1) &
                        (Account.last_modified <
                         (datetime.utcnow() - timedelta(weeks=1))))
                 .execute())
        log.debug('Reseted warnings on %d accounts.', query)

        # Reset shadow banned accounts after two weeks.
        query = (Account
                 .update(allocated=False, failed=0, banned=AccountBanned.Clear)
                 .where((Account.banned == AccountBanned.Shadowban) &
                        (Account.last_modified <
                         (datetime.utcnow() - timedelta(weeks=2))))
                 .execute())
        log.debug('Reseted %d shadow banned accounts.', query)

        # Reset temporarily banned accounts after six weeks.
        query = (Account
                 .update(allocated=False, failed=0, banned=AccountBanned.Clear)
                 .where((Account.banned == AccountBanned.Temporary) &
                        (Account.last_modified <
                         (datetime.utcnow() - timedelta(weeks=6))))
                 .execute())
        log.debug('Reseted %d temporarily banned accounts.', query)

    # Release accounts previously used by this instance.
    def _release_instance(self):
        rows = 0
        try:
            with Account.database().execution_context():
                query = (Account
                         .update(allocated=False)
                         .where(Account.instance_id == self.instance_id))
                rows = query.execute()
        except Exception as e:
            log.exception('Error releasing accounts previously used: %s.', e)

        log.debug('Released %d accounts previously used by this instance.',
                  rows)

    # Allocate available accounts from database.
    def _allocate_accounts(self, count, reuse, hlvl):
        # Build query conditions to select valid and usable accounts.
        timeout = datetime.utcnow() - timedelta(hours=self.args.login_timeout)
        conditions = ((Account.allocated == 0) &
                      ((Account.failed == 0) |
                       (Account.last_modified < timeout)))
        if self.args.no_pokemon or self.args.shadow_ban_scan:
            conditions &= (Account.banned <= AccountBanned.Shadowban)
        else:
            conditions &= (Account.banned == AccountBanned.Clear)
        if reuse:
            conditions &= (Account.instance_id == self.instance_id)
        else:
            conditions &= (Account.instance_id.is_null() |
                           (Account.instance_id != self.instance_id))
        if hlvl:
            conditions &= (Account.level >= self.high_level)
        elif not self.args.scan_hlvl:
            # Allow high-level accounts to be allocated for scanning.
            conditions &= (Account.level < self.high_level)

        try:
            with Account.database().execution_context():
                query = (Account
                         .select()
                         .where(conditions)
                         .order_by(Account.level.desc(),
                                   Account.last_modified.desc())
                         .limit(min(250, count))
                         .dicts())
                accounts = {}
                for dba in query:
                    # Update account object.
                    dba['allocated'] = True
                    dba['instance_id'] = self.instance_id
                    dba['last_modified'] = datetime.utcnow()
                    accounts[dba['username']] = dba

                allocated = 0
                if accounts:
                    # Update selected accounts as allocated to this instance.
                    query = (Account
                             .update(allocated=True,
                                     instance_id=self.instance_id)
                             .where((Account.allocated == 0) &
                                    (Account.username << accounts.keys())))
                    allocated = query.execute()

                unallocated = len(accounts) - allocated
                if unallocated > 0:
                    log.error('Failed to allocate %d accounts.', unallocated)
                else:
                    # Return valid and allocated accounts.
                    return accounts

        except Exception as e:
            log.exception('Error allocating accounts from database: %s.', e)

        return {}

    # Allocate and load accounts from database.
    def _fetch_accounts(self, count, hlvl, spare=True):
        accounts = {}
        if count > 0:
            accounts = self._allocate_accounts(count, True, hlvl)
            count -= len(accounts)
        if count > 0:
            accounts.update(self._allocate_accounts(count, False, hlvl))

        if hlvl:
            account_pool = 'high-level'
        else:
            account_pool = 'scanner'

        accounts_lock = self.accounts_locks[account_pool]
        allocated_pool = self.allocated[account_pool]
        active_pool = self.active[account_pool]
        spare_pool = self.accounts[account_pool]

        # Store accounts in their respective account pool.
        with accounts_lock:
            for username, account in accounts.iteritems():
                # Satefy check, better be sure than sorry.
                if username in allocated_pool:
                    log.warning('Fetched %s account %s was already allocated.',
                                account_pool, username)
                    continue
                allocated_pool.add(username)
                account['account_pool'] = account_pool
                if spare:
                    spare_pool[username] = account
                else:
                    active_pool[username] = account

        return accounts

    # Get next account that is ready to start working.
    def get_account(self, location=None, hlvl=False):
        if hlvl:
            account_pool = 'high-level'
            speed_limit = self.args.hlvl_kph
        else:
            account_pool = 'scanner'
            speed_limit = self.args.kph

        accounts_lock = self.accounts_locks[account_pool]
        active_pool = self.active[account_pool]
        spare_pool = self.accounts[account_pool]

        with accounts_lock:
            now = datetime.utcnow()
            picked_username = None
            last_scan_secs = 0

            # Loop through available spare accounts.
            # Reversed iteration to maximize account re-usage.
            for username in reversed(spare_pool.keys()):
                account = spare_pool[username]

                # Check if this account remains below speed limit.
                if location and speed_limit and account['last_scan']:
                    last_scan_secs = (now -
                                      account['last_scan']).total_seconds()
                    old_location = (account['latitude'], account['longitude'])

                    meters = distance(old_location, location)
                    cooldown_time_secs = meters / speed_limit * 3.6

                    # Not enough time has passed for this one.
                    sleep_time = cooldown_time_secs - last_scan_secs
                    if sleep_time > 10:
                        continue

                # We've found an account ready to work.
                picked_username = username
                break

            if picked_username:
                picked_account = spare_pool.pop(picked_username)

                log.info('Picked %s account %s from spare account pool.',
                         account_pool, picked_username)

                picked_account['account_pool'] = account_pool
                active_pool[picked_username] = picked_account

                return picked_account

        if hlvl and not self.args.hlvl_workers:
            # Check if we're not allocating too many accounts.
            available_count = len(active_pool) + len(spare_pool)
            if available_count >= self.args.hlvl_workers_max:
                log.debug('Reached %s allocation limit of %d accounts.',
                          account_pool, self.args.hlvl_workers_max)
                return None

            # "On-the-fly" high-level account allocation.
            accounts = self._fetch_accounts(1, hlvl=True, spare=False)
            if len(accounts) < 1:
                return None

            picked_username, picked_account = accounts.popitem()
            log.info('Picked %s account %s "on-the-fly" from database.',
                     account_pool, picked_username)

            return picked_account

        return None

    # Move account from active to spare account pool.
    def release_account(self, account):
        username = account['username']
        account_pool = account['account_pool']
        active_pool = self.active[account_pool]

        # Make sure account is active.
        if username not in active_pool:
            log.error('Trying to release a %s account %s that is not active.',
                      account_pool, username)
            return

        accounts_lock = self.accounts_locks[account_pool]
        allocated_pool = self.allocated[account_pool]
        spare_pool = self.accounts[account_pool]

        if account_pool == 'scanner':
            holding_time = self.args.workers_holding_time
        else:
            holding_time = self.args.hlvl_workers_holding_time

        with accounts_lock:
            active_pool.pop(username)

            if holding_time > 0:
                # Keep account allocated to this instance for a while.
                log.info('Moving active %s account %s to spare account pool.',
                         account_pool, username)
                spare_pool[username] = account
            else:
                # Immediately release account from this instance.
                account['allocated'] = False
                allocated_pool.remove(username)
                log.info('Released %s account %s from this instance.',
                         account_pool, username)

        # Update account information in database.
        self.dbq.put((Account, {0: Account.db_format(account)}))

    # Move account from active to failed pool.
    def failed_account(self, account, reason):
        username = account['username']
        account_pool = account['account_pool']
        accounts_lock = self.accounts_locks[account_pool]
        active_pool = self.active[account_pool]

        with accounts_lock:
            # Make sure account is active.
            if username not in active_pool:
                log.warning('Unable to find %s account %s in active pool.',
                            account_pool, username)
            else:
                log.info('Moving active %s account %s to failed pool.',
                         account_pool, username)

                active_pool.pop(username)
                self.accounts['failed'].append((account, reason, False))

        # Update account information in database.
        self.dbq.put((Account, {0: Account.db_format(account)}))

    # Check account status and update the database.
    def check_account(self, account, status):
        username = account['username']
        account_pool = account['account_pool']
        active_pool = self.active[account_pool]

        # Check if account is still active.
        if username not in active_pool:
            status['message'] = (
                'Account {} was removed from active {} account pool. ' +
                'Switching accounts...').format(username, account_pool)
            return False

        # Check if account is shadow banned.
        if (not self.args.shadow_ban_scan and
                account['banned'] == AccountBanned.Shadowban):
            status['message'] = (
                'Account {} is shadow banned: {} scans without ' +
                'rare Pokemon. Switching accounts...').format(
                    account['username'], status['no_rares'])
            log.warning(status['message'])
            self.failed_account(account, 'shadow banned')
            return False

        # Update account information in database.
        self.dbq.put((Account, {0: Account.db_format(account)}))
        return True

    # Check and handle captcha encounters.
    def handle_captcha(self, account, status, api, response):
        username = account['username']

        # Default result: no captcha, no failure.
        result = {'found': False, 'failed': False}

        if not response:
            return result

        if 'CHECK_CHALLENGE' not in response.get('responses', {}):
            return result

        captcha_url = response['responses']['CHECK_CHALLENGE'].challenge_url

        if len(captcha_url) < 2:
            return result

        # Update thread status if it belongs to this account.
        if status['username'] == account['username']:
            status['captcha'] += 1

        # Default result: captcha found, failed to solve it.
        result = {'found': False, 'failed': False}
        account['captcha'] = True

        # Captcha solving is disabled completely.
        if not self.args.captcha_solving:
            status['message'] = (
                'Account {} has encountered a captcha. ' +
                'Putting account away.').format(username)
            log.warning(status['message'])

            # Send webhook message.
            if 'captcha' in self.args.wh_types:
                wh_message = {
                    'status_name': self.args.status_name,
                    'status': 'encounter',
                    'mode': 'disabled',
                    'account': username,
                    'captcha': status['captcha'],
                    'time': 0
                }
                self.whq.put(('captcha', wh_message))

            # Put account out of circulation - handled by check_account().
            self.failed_account(account, 'captcha')

        # Automatic captcha solving only.
        elif self.args.captcha_key and self.args.manual_captcha_timeout == 0:
            if self._automatic_captcha_solve(account, status, api,
                                             captcha_url):
                # Solved the captcha on the spot, no fuzz.
                result['failed'] = False
                account['captcha'] = False
            else:
                status['message'] = (
                    'Account {} has encountered a captcha and failed to ' +
                    'solve it. Putting account away.').format(username)
                log.warning(status['message'])

                # Put account out of circulation - handled by check_account().
                self.failed_account(account, 'captcha failed')

        # Hybrid/Manual captcha solving.
        else:
            timeout = self.args.manual_captcha_timeout
            if self.args.captcha_key:
                solving_mode = 'hybrid'
                status['message'] = (
                    'Account {} has encountered a captcha. Hybrid-mode, ' +
                    'waiting {} secs for a token.').format(username, timeout)
            else:
                solving_mode = 'manual'
                status['message'] = (
                    'Account {} has encountered a captcha. Manual-mode, ' +
                    'waiting for a token.').format(username)

            log.warning(status['message'])

            if 'captcha' in self.args.wh_types:
                wh_message = {
                    'status_name': self.args.status_name,
                    'status': 'encounter',
                    'mode': solving_mode,
                    'account': username,
                    'captcha': status['captcha'],
                    'time': timeout
                }
                self.whq.put(('captcha', wh_message))

            # Put account out of circulation - handled by check_account().
            self._captcha_account(account, status, captcha_url)

        return result

    # Move account from active to captcha account pool.
    def _captcha_account(self, account, status, captcha_url):
        username = account['username']
        account_pool = account['account_pool']
        accounts_lock = self.accounts_locks[account_pool]
        active_pool = self.active[account_pool]

        with accounts_lock:
            # Make sure account is active.
            if username not in active_pool:
                log.error('Unable to find %s account %s in active pool. ',
                          active_pool, username)
            else:
                log.info('Moving active %s account %s to captcha pool.',
                         account_pool, username)

                active_pool.pop(username)
                self.accounts['captcha'].append((account, status, captcha_url))

        # Update account information in database.
        self.dbq.put((Account, {0: Account.db_format(account)}))

    # Returns true if captcha was succesfully solved.
    def _automatic_captcha_solve(self, account, status, api, captcha_url):
        status['message'] = (
            'Account {} is encountering a captcha, starting 2captcha ' +
            'sequence.').format(account['username'])
        log.warning(status['message'])

        if 'captcha' in self.args.wh_types:
            wh_message = {
                'status_name': self.args.status_name,
                'status': 'encounter',
                'mode': '2captcha',
                'account': account['username'],
                'captcha': status['captcha'],
                'time': 0}
            self.whq.put(('captcha', wh_message))

        time_start = time.time()
        captcha_token = token_request(self.args, status, captcha_url)
        time_elapsed = time.time() - time_start

        if 'ERROR' in captcha_token:
            log.warning('Unable to resolve captcha, please check your ' +
                        '2captcha API key and/or wallet balance.')
            if 'captcha' in self.args.wh_types:
                wh_message['status'] = 'error'
                wh_message['time'] = time_elapsed
                self.whq.put(('captcha', wh_message))

            return False
        else:
            status['message'] = (
                'Retrieved captcha token, attempting to verify challenge ' +
                'for {}.').format(account['username'])
            log.info(status['message'])

            req = api.create_request()
            req.verify_challenge(token=captcha_token)
            response = req.call(False)
            time_elapsed = time.time() - time_start
            success = response['responses']['VERIFY_CHALLENGE'].success
            if success:
                status['message'] = (
                    'Account {} got its captcha solved.').format(
                    account['username'])
            else:
                status['message'] = (
                    'Account {} failed to verify challenge, putting it ' +
                    'away for now.').format(account['username'])
            log.info(status['message'])
            if 'captcha' in self.args.wh_types:
                wh_message['status'] = 'success' if success else 'failure'
                wh_message['time'] = time_elapsed
                self.whq.put(('captcha', wh_message))

            return success

    # Keeps track of captcha'd accounts awaiting for manual token inputs.
    def _captcha_manager(self):
        tokens_needed = len(self.accounts['captcha'])
        if tokens_needed > 0:
            tokens = Token.get_valid(tokens_needed)
            tokens_available = len(tokens)
            solvers = min(tokens_needed, tokens_available)
            log.debug('Captcha manager running. Captchas: %d - Tokens: %d',
                      tokens_needed, tokens_available)
            for i in range(0, solvers):
                hash_key = self.key_scheduler.next()

                t = Thread(
                    target=self._captcha_solver,
                    name='captcha-solver-{}'.format(self.thread_id),
                    args=(hash_key, tokens[i]))
                t.daemon = True
                t.start()

                self.thread_id += 1
                if self.thread_id > 999:
                    self.thread_id = 0
                # Wait a bit before launching next thread.
                time.sleep(1)

            # Hybrid mode - after waiting send to automatic captcha solver.
            if self.args.captcha_key and self.args.manual_captcha_timeout > 0:
                tokens_remaining = tokens_needed - tokens_available
                # Safety guard, don't grab too much work.
                tokens_remaining = min(tokens_remaining, 5)
                for i in range(0, tokens_remaining):
                    account = self.accounts['captcha'][0][0]
                    hold_time = (datetime.utcnow() -
                                 account['last_modified']).total_seconds()
                    if hold_time > self.args.manual_captcha_timeout:
                        log.debug('Account %s waited %ds for captcha token ' +
                                  'and reached the %ds timeout.',
                                  account['username'], hold_time,
                                  self.args.manual_captcha_timeout)
                        hash_key = self.key_scheduler.next()

                        t = Thread(
                            target=self._captcha_solver,
                            name='captcha-solver-{}'.format(self.thread_id),
                            args=hash_key)
                        t.daemon = True
                        t.start()

                        self.thread_id += 1
                        if self.thread_id > 999:
                            self.thread_id = 0

                        # Wait a little bit before launching next thread.
                        time.sleep(1)
                    else:
                        break

    # Log-in with account, setup API and attempt to solve captcha with token.
    def _captcha_solver(self, hash_key, token=None):
        account, status, captcha_url = self.accounts['captcha'].popleft()

        username = account['username']
        if username != status['username']:
            # Search worker thread has moved on, don't use its status.
            status = {
                'message': '',
                'captcha': 1,
                'proxy_display': 'No',
                'proxy_url': False
            }

        status['message'] = 'Waking up account {} to solve captcha.'.format(
                            username)
        log.info(status['message'])

        api = setup_api(self.args, status, account)

        if hash_key:
            log.debug('Using hash key %s to solve this captcha.', hash_key)
            api.activate_hash_server(hash_key)

        location = (account['latitude'], account['longitude'])
        altitude = get_altitude(self.args, location)
        location = (location[0], location[1], altitude)

        if self.args.jitter:
            # Jitter location before attempting to verify challenge.
            location = jitter_location(location)

        api.set_position(*location)
        if not check_login(self, status, api, account):
            return

        if not token:
            token = token_request(self.args, status, captcha_url)

        req = api.create_request()
        req.verify_challenge(token=token)
        response = req.call(False)
        success = response['responses']['VERIFY_CHALLENGE'].success

        if success:
            status['message'] = (
                'Account {} successfully solved its captcha, ' +
                'returning to active duty.').format(username)
            log.info(status['message'])

            # Update account information in database.
            account['captcha'] = False
            self.dbq.put((Account, {0: Account.db_format(account)}))

            # Return account to the appropriate account pool.
            account_pool = account['account_pool']
            accounts_lock = self.accounts_locks[account_pool]
            with accounts_lock:
                self.accounts[account_pool][username] = account

        else:
            status['message'] = (
                'Account {} failed to verify challenge, putting it back ' +
                'in captcha account pool.').format(username)
            log.warning(status['message'])
            self.accounts['captcha'].append((status, account, captcha_url))

        if 'captcha' in self.args.wh_types:
            hold_time = (datetime.utcnow() -
                         account['last_modified']).total_seconds()
            wh_message = {
                'status_name': self.args.status_name,
                'mode': 'manual' if token else '2captcha',
                'account': 'scanner',
                'captcha': status['captcha'],
                'time': int(hold_time),
                'status': 'success' if success else 'failure'
            }
            self.whq.put(('captcha', wh_message))

        # Let things settle down a bit.
        time.sleep(1)


def token_request(args, status, url):
    s = Session()
    # Fetch the CAPTCHA_ID from 2captcha.
    try:
        request_url = (
            'http://2captcha.com/in.php?key={}&method=userrecaptcha' +
            '&googlekey={}&pageurl={}').format(args.captcha_key,
                                               args.captcha_dsk, url)
        captcha_id = s.post(request_url, timeout=5).text.split('|')[1]
        captcha_id = str(captcha_id)
    # IndexError implies that the retuned response was a 2captcha error.
    except IndexError:
        return 'ERROR'
    status['message'] = (
        'Retrieved captcha ID: {}; now retrieving token.').format(captcha_id)
    log.info(status['message'])
    # Get the response, retry every 5 seconds if it's not ready.
    recaptcha_response = s.get(
        'http://2captcha.com/res.php?key={}&action=get&id={}'.format(
            args.captcha_key, captcha_id), timeout=5).text
    while 'CAPCHA_NOT_READY' in recaptcha_response:
        log.info('Captcha token is not ready, retrying in 5 seconds...')
        time.sleep(5)
        recaptcha_response = s.get(
            'http://2captcha.com/res.php?key={}&action=get&id={}'.format(
                args.captcha_key, captcha_id), timeout=5).text
    token = str(recaptcha_response.split('|')[1])
    return token
