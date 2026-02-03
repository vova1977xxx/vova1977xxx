STATES = ['scouted','downloaded','probed','analyzed','ranked','published','dropped','quarantine']
ERROR_STATES = ['stuck','retry_exceeded']
TRANSITIONS = {
 'scouted':['downloaded'],
 'downloaded':['probed'],
 'probed':['analyzed'],
 'analyzed':['ranked','quarantine'],
 'ranked':['published','dropped']
}
