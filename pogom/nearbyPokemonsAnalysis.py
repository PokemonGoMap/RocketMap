import time
import logging
from geopy import distance
from base64 import b64decode
from .transform import get_new_coords
log = logging.getLogger(__name__)

def anplog(m,*a):
    if m == 0:
        m = ''
        for n in a:
            log.info( n )
    else:
        log.info(m.format(*a))
    
def get_bitgroup_analysis_constants():
    # these values will probably always be constant, but better to use
    # variables in case Niantic changes the values on us
    pokemon_visible_distance = 70
    pokemon_nearby_distance = 200
    encounter_id_bit_length = 64
    '''
    the encounter id, is 64 bits long
    a bitgroup is a small subset of those 64 bits
    groups are counted sequentially in reverse, so bitgroup 0 is at the end (least significant bits)
    presumably each bitgroup represents something, but so far we only know the meaning first 3 groups
        bitgroup 0 is 4 bits long, bits 0 through 3
        bitgroup 1 is 3 bits long, bits 4 through 6
        bitgroup 2 is 3 bits long, bits 7 through 9
        bitgroup 3 must start at bit # 10
    as we learn more about where to divide up these groups, we can add to that list of starting numbers (see "groups" in the code below)
    this function will return the value of the requested bitgroup, you provide an encounter_id and what group you want
    or instead of a group number, provide a starting bit and length (this will be useful if people want to start exploring patterns in the other bit groups)

    bitgroups can go through a sequence of values and then starts that sequence over
    bitgroups can also cycle through different sequences
    to reiterate: cycles are made up of sequences which are made up of values
    bitpos = bit position = what is the group's starting bit position in the 64-bit ID
    seqlen = sequence length = how many values are in a sequence before it repeats
    seqint = sequence interval = what is the interval (ms) between sequence value incrementations
    cyclen = cycle length = how many sequences are in a cycle before it repeats
    cycint = cycle interval = what is the interval (ms) between cycles ( changing to a different sequence )
    '''

    # define how many bitgroups we know of (currently 3: 0, 1, and 2)
    known_bitgroups = 3

    # create list of bitgroups
    bitgroups = [{} for n in range(known_bitgroups + 1)]

    # DEFINE BITGROUP INFO BELOW

    # bitgroup 0 is the least 4 significant bits and doesn't change through
    # any sequence. it is always value 13 for catchables (credit: /u/Kaetemi)
    bitgroups[0]['bitpos'] = 0
    # no sequence incrementation (so its always in the same one sequence)
    bitgroups[0]['seqlen'] = 1
    # no sequence incrementation (so its always in the same one sequence)
    bitgroups[0]['seqint'] = 1
    # no cycle incrementation (so its always in the same one cycle)
    bitgroups[0]['cyclen'] = 1
    # no cycle incrementation (so its always in the same one cycle)
    bitgroups[0]['cycint'] = 1

    # bitgroup 1 is the next least 3 significant bits and increments through a
    # fixed sequence by either 1, 3, 5, or 7 every hour, repeating after the
    # 8th value. it does not cycle (it is a fixed incrementation) (credit:
    # /u/Kaetemi)
    bitgroups[1]['bitpos'] = 4
    bitgroups[1]['seqlen'] = 8  # sequence repeats after 8 value increments
    # sequence increments to next value every hour
    bitgroups[1]['seqint'] = 1000 * 60 * 60
    # no sequence incrementation (so its always in the same one cycle)
    bitgroups[1]['cyclen'] = 1
    # no sequence incrementation (so its always in the same one cycle)
    bitgroups[1]['cycint'] = 1

    # bitgroup 2 is the next least 3 significant bits and increments through a
    # sequence by either 1, 3, 5, or 7 every day, repeating after the 8th
    # value. it cycles through incrementations hourly (credit: /u/Kaetemi)
    bitgroups[2]['bitpos'] = 7
    bitgroups[2]['seqlen'] = 8  # sequence repeats after 8 value increments
    # sequence increments to next value every 24 hrs
    bitgroups[2]['seqint'] = 1000 * 60 * 60 * 24
    bitgroups[2]['cyclen'] = 24  # cycle repeats after 24 sequence increments
    # cycle increments to next sequence every hour
    bitgroups[2]['cycint'] = 1000 * 60 * 60

    # we need to define the start of the next group even though we don't know
    # anything more about it
    bitgroups[3]['bitpos'] = 10

    # make a list of the starting bits for each group, to be passed to our bit
    # calculator
    startbits = [group['bitpos'] for group in bitgroups]
    startbits.append(encounter_id_bit_length - 1)

    r = {}
    r['min_dist'] = pokemon_visible_distance
    r['max_dist'] = pokemon_nearby_distance
    r['groups'] = bitgroups
    r['startbits'] = startbits

    return r

def do_query(sql):
    from .models import BaseModel
    try:
        return [ row for row in  BaseModel.raw(sql).dicts().execute() ]
    except:
        return []

def convert_time_sql_to_unix():
    # sqlite doesn't have UNIX_TIMESTAMP
    # todo: get db_type here for real
    #if args.db_type == 'sqlite':
    if 0:
        return "round((strftime('%%f',disappear_time) - strftime('%%S',disappear_time)),3) + strftime('%%s',disappear_time)"
    else:
        return "UNIX_TIMESTAMP(disappear_time)"


def get_spawns_in_donut(center, min_dist, max_dist):
    # this sql query is getting a "square donut" where the outer distance is a square AROUND the max_dist radius
    # but the inner "hole" is a square that will fit INSIDE the min_dist radius
    # so we need to shrink the min_dist radius to a square that fits inside it
    # we do this by multiplying by half of the square root of 2
    # we will round down slightly to 0.7071 because its better exclude too
    # little than too much
    min_dist_shrunken = 0.7071 * min_dist
    
    #convert to km
    min_dist_km = min_dist_shrunken / 1000.0
    max_dist_km = max_dist / 1000.0
    
    # find edges for big square
    big_n = get_new_coords(center, max_dist_km, 0)[0]
    big_e = get_new_coords(center, max_dist_km, 90)[1]
    big_s = get_new_coords(center, max_dist_km, 180)[0]
    big_w = get_new_coords(center, max_dist_km, 270)[1]
    
    # find edges for little square (hole)
    small_n = get_new_coords(center, min_dist_km, 0)[0]
    small_e = get_new_coords(center, min_dist_km, 90)[1]
    small_s = get_new_coords(center, min_dist_km, 180)[0]
    small_w = get_new_coords(center, min_dist_km, 270)[1]
    
    # build sql query
    in_big_box = '{} <= latitude AND latitude <= {} AND {} <= longitude AND longitude <= {}'.format(big_s, big_n, big_w, big_e)
    in_small_box = '{} <= latitude AND latitude <= {} AND {} <= longitude AND longitude <= {}'.format(small_s, small_n, small_w, small_e)
    sql = "SELECT spawnpoint_id, latitude, longitude, {} %% 3600 as expiration_ms FROM pokemon WHERE {} AND NOT({}) GROUP BY spawnpoint_id, expiration_ms"
    sql = sql.format(convert_time_sql_to_unix(),in_big_box, in_small_box)
    
    # do sql query and cut it down to return only those which are in range of 200m and outside 70m
    return [sp for sp in do_query( sql ) if min_dist <= distance.distance( (center[0],center[1]), (sp['latitude'], sp['longitude'])).meters <= max_dist]

def calculate_next_disappearance(exp_ms_past_hr):

    # str to int
    exp_ms_past_hr = int(exp_ms_past_hr)

    # we'll do all work in ms, then convert to s at the end when needed
    now_ms = time.time() * 1000
    now_ms_past_hr = now_ms % 3600000

    # to calculate the next disappear time, start with the unix ms of the
    # current hour, then just add the exp_ms_past_hr
    top_of_current_hour = now_ms - now_ms_past_hr
    next_dt_ms = top_of_current_hour + exp_ms_past_hr

    # and if that caluclated timestamp already happend, add another hour to
    # get the next one
    if next_dt_ms < now_ms:
        next_dt_ms += 3600000

    # todo: don't assume spawn length is 15min, actually figure out if this is
    # a 30min, 45min, etc
    spawn_length_ms = 900000  # 15 min

    # return:
    # 1. disappear_time in seconds
    # 2. last_modified_timestamp_ms (work backwards from d_t using spawn_length)
    # 3. time_till_hidden_ms ( work backwards from d_t til now )

    return (next_dt_ms / 1000.0, next_dt_ms -
            spawn_length_ms, next_dt_ms - now_ms)


def get_bitgroup_value(startbits, encounter_id, query='all', length=False, trackit = False):
    try:
        i = int(b64decode(encounter_id))
    except:
        i = int(encounter_id)
    if query == 'all':
        return [get_bitgroup_value(startbits, encounter_id, n) for n in range(len(startbits[:-2]))]
    if not length:
        group = query
        try:
            start = startbits[group]
        except IndexError:
            return None
        length = startbits[group + 1] - start
    else:
        start = query
    return (i >> start) & 2 ** length - 1

def extrapolate_bit_sequence_with_error_checking(s):
    
    pk = inc = first = None
    
    for k, v in enumerate(s):

        if pk != None and v != None:
            # keep in mind: if the previous value was larger, we've crossed the sequence max_value and started over
            # cacluclate the increment and first value
            new_inc = (s[pk] - v) / (len(s) + pk - k) if s[pk] > v else (v - s[pk]) / (k - pk)

            # check for inconsistant calculations
            if inc != None and inc != new_inc:
                #log.info(s)
                #log.info('at step {} and the sequence interval caluclated does not match from one step to another. thought it was {} but now it seems to be {}'.format(k, inc, new_inc))
                return s

            inc = new_inc
            
            max_value = len(s) * inc
            
            if max_value == 0:
                return s
                
            new_first = (v + inc * (len(s) - k)) % max_value

            # check for inconsistant calculations
            if first != None and first != new_first:
                #log.info(s)
                #log.info('at step {} and the first value caluclated does not match from one step to another. thought it was {} but now it seems to be {}'.format(k, first, new_first))
                return s

            first = new_first

        # track how many actual values we've passed so far
        if v != None:
          pk = k

    # we looped the whole thing and got to here, lets quit if we didn't get a
    # first and an inc
    if inc == None or first == None:
        return s

    new_s = []
    for k, v in enumerate(s):
        new_s.append(((k * inc) + first) % max_value)
        if v != None and new_s[k] != v:
            #log.info(s)
            #log.info(new_s)
            #log.info('at step {} and the new value calulated {} does not match the existing value {}'.format(k, new_s[k], v))
            return s

    if len(new_s) != len(s):
        #log.info(s)
        #log.info(new_s)
        #log.info('length of s and new_s do not match')
        return s

    if None in new_s:
        #log.info(s)
        #log.info(new_s)
        #log.info('new_s contains a None')
        return s

    r = map(int, new_s)
    return r


def extrapolate_bit_sequence(s, extra_error_checking=False):

    if extra_error_checking: return extrapolate_bit_sequence_with_error_checking( s )

    # get all bit values which are not None and quit now if we don't have at
    # least 2 to use
    not_none = [k for k, v in enumerate(s) if v != None]
    if len(not_none) < 2: return s

    # gonna use this a few times, lets assign it to a variable
    sequence_length = len(s)

    # in our list of not_none values: get first key, last key, first value, last value
    # and then use those 4 values to figure out the increment between
    # successive keys in this list
    fk, lk = [min(not_none), max(not_none)]
    fv, lv = [s[fk], s[lk]]

    # we need to handle cases where the list restarts at 0 between fk and lk
    # (i.e. fv > lv)
    flip = (sequence_length * (fv > lv))
    increment = (lv - fv) / (lk - fk - flip)

    # determine the value of the first item in the list
    first_value = lv + increment * (sequence_length - lk)

    # restart incrementation at 0 when the largest possible value is reached
    max_value = sequence_length * increment
    
    if max_value == 0:
        return s

    # return the new list

    return [int((k * increment + first_value) % max_value) for k, v in enumerate(s)]


def get_sid_bits(sp, c, use_extra_error_checking=False):
    sp_bitgroups = c['groups'][:-1]
    sp['disappear_time_ms'] = sp['disappear_time'] * 1000
    base_query = "SELECT {} FROM pokemon WHERE {} HAVING {}"
    d_t_sql = "({})".format(convert_time_sql_to_unix())
    select = 'encounter_id, disappear_time, {} as disappear_time_ms_unix'.format(
        d_t_sql)
    where = 'spawnpoint_id = "{}"'.format(sp['spawnpoint_id'])
    having = '1'
    formula = "( (1000 * {}) DIV {} ) %% {}"
    for id, g in enumerate(sp_bitgroups):
        sp_bitgroups[id]['bitvalues'] = [
            [None for s in range(g['seqlen'])] for x in range(g['cyclen'])]
        sp_bitgroups[id]['seqpos']      = int( sp['disappear_time_ms'] / g['seqint']) % g['seqlen']
        sp_bitgroups[id]['cycpos']      = int( sp['disappear_time_ms'] / g['cycint']) % g['cyclen']
        sp_bitgroups[id]['seqsqlname']  = "bg_{}_seq".format(id)
        sp_bitgroups[id]['cycsqlname']  = "bg_{}_cyc".format(id)
        sp_bitgroups[id]['seqsqlmath']  = formula.format(d_t_sql, g['seqint'], g['seqlen'])
        sp_bitgroups[id]['cycsqlmath']  = formula.format(d_t_sql, g['cycint'], g['cyclen'])
        sp_bitgroups[id]['seqsqlsel']   =    ", {} as {}".format(sp_bitgroups[id]['seqsqlmath'], sp_bitgroups[id]['seqsqlname'])
        sp_bitgroups[id]['cycsqlsel']   =    ", {} as {}".format(sp_bitgroups[id]['cycsqlmath'], sp_bitgroups[id]['cycsqlname'])
        sp_bitgroups[id]['seqsqlwhere'] = " AND {} =  {}".format(sp_bitgroups[id]['seqsqlname'], sp_bitgroups[id]['seqpos'])
        sp_bitgroups[id]['cycsqlwhere'] = " AND {} =  {}".format(sp_bitgroups[id]['cycsqlname'], sp_bitgroups[id]['cycpos'])
        select += sp_bitgroups[id]['seqsqlsel']   + sp_bitgroups[id]['cycsqlsel']
        having  += sp_bitgroups[id]['seqsqlwhere'] + sp_bitgroups[id]['cycsqlwhere']

    # first try a direct query for a row with a disappear_time that matches the current sequence and cycle positions,
    # if that is already in the db we can just use the values from that
    # encounter_id since they will match the current/next encounter_id at this spawnpoint
    query = base_query.format(select, where, having)
    results = do_query(query)
    if len(results) > 0:
        return get_bitgroup_value(c['startbits'], results[0]['encounter_id'])
    
    # todo: implement a cache with an expiration that can replace the rest of this function

    # since there wasn't an existing row in the db with a d_t that matched the current seq and cyc positions
    # we will pull all encounter_id and disappear_time for this spawnpoint_id
    # and also have sql calculate the seq and cyc pos for each of those d_t
    query = base_query.format(select, where, '1')
    results = do_query(query)
    if len(results) > 0:
        for n, row in enumerate(results):
            # get all bitgroup values for this encounter_id
            bitvalues = results[n]['bitgroup_values'] = get_bitgroup_value(c['startbits'], row['encounter_id'], 'all', False, True)
            # loop through each bitgroup and store the aquired values
            for id, g in enumerate(sp_bitgroups):
                cycle = row['bg_{}_cyc'.format(id)]
                sequence = row['bg_{}_seq'.format(id)]
                current_value = g['bitvalues'][ cycle ][ sequence ]
                if current_value != None and current_value != bitvalues[id]:
                    pass
                    #log.info('Houston we have a problem. BitValue is thought to be {} but we are now changing it to {}'.format(current_value, bitvalues[id]))
                sp_bitgroups[id]['bitvalues'][row['bg_{}_cyc'.format(id)]][row['bg_{}_seq'.format(id)]] = bitvalues[id]
                try:
                    sp_bitgroups[id]['bitvalues'][row['bg_{}_cyc'.format(id)]] = extrapolate_bit_sequence(sp_bitgroups[id]['bitvalues'][row['bg_{}_cyc'.format(id)]], use_extra_error_checking)
                except:
                    pass
        # we've looped through all previous encounters at this spawnpoint and built a list of bitvalues from that information
        # now just return a list of bitvalues (for every bitgroup) based on the
        # already calculated cycpos and seqpos by pulling them from the list
        result = [g['bitvalues'][g['cycpos']][g['seqpos']] for id, g in enumerate(sp_bitgroups)]
        return result

def analyze_nearby_pokemons(step_loc, nearby_pokemons, use_extra_error_checking = False):
         
    bg_constants=get_bitgroup_analysis_constants()

    nearby_spawnpoints=get_spawns_in_donut( step_loc, bg_constants['min_dist'], bg_constants['max_dist'])
    
    for nearby_sp in nearby_spawnpoints:

        # calculate times for each spawnpoint, they can be used to narrow down
        # potential matches
        nearby_sp['disappear_time'], nearby_sp['last_modified_timestamp_ms'], nearby_sp['time_till_hidden_ms'] = calculate_next_disappearance(nearby_sp['expiration_ms'])
                
        # look up bitvalues for sp
        sid_bits = get_sid_bits(nearby_sp, bg_constants, use_extra_error_checking)
    
    matched_pokes = []
    for nearby_poke in nearby_pokemons:
        eid=nearby_poke['encounter_id']
        potential_spawnpoints=[]
        try:
            eid_bits = get_bitgroup_value(c['startbits'], eid) 
            if eid_bits != None and eid_bits == sid_bits:
                potential_spawnpoints.append(nearby_sp)
        except:
            pass
        if len(potential_spawnpoints) != 1:
            continue

        # shorthand name for the matched potential spawnpoint
        sp = potential_spawnpoints[0]

        # now lets add to nearby_poke the necessary keys so as to make it match the format of the data returned in a real api wild_pokemons list.
        # encounter_id and pokemon_id already exist for nearby_poke

        # move the pokemon_id to 'pokemon_data'
        nearby_poke['pokemon_data'] = {}
        nearby_poke['pokemon_data']['pokemon_id'] = nearby_poke['pokemon_id']

        # copy data from the matched spawnpoint location to nearby_poke
        nearby_poke['spawn_point_id'] = sp['spawnpoint_id']
        nearby_poke['latitude'] = sp['latitude']
        nearby_poke['longitude'] = sp['longitude']
        nearby_poke['disappear_time'] = sp['disappear_time']
        nearby_poke['last_modified_timestamp_ms'] = sp[
            'last_modified_timestamp_ms']
        nearby_poke['time_till_hidden_ms'] = sp['time_till_hidden_ms']
       
        matched_pokes.append( nearby_poke )
        
    return matched_pokes
