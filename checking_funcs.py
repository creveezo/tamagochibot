from helpedit_funcs import get_smth, push_smth

def if_alive(id):
    try:
        get_smth('id', id)
        return 1
    except Exception:
        return 0
    
def if_plot_now(id):
    n = get_smth('action_number', id)
    stage = get_smth('stage', id)
    if stage == 0:
        if n == 12: 
            ans = 0
        else:
            ans = 1
    if stage == 1:
        print('ДОБАВЬТЕ ЧЕ ПРОИСХОДИТЬ В ИФ ПЛОТ НАУ')
    return ans

def push_main_loc(id):
    main_loc = ''
    loc_kind = get_smth('kind_count_loc', id)
    loc_evil = get_smth('evil_count_loc', id)
    loc_cringe = get_smth('cringe_count_loc', id)
    if loc_kind > loc_evil and loc_kind >= loc_cringe:
        main_loc = 'kind'
    elif loc_evil > loc_kind and loc_evil >= loc_cringe:
        main_loc = 'evil'
    elif (loc_kind == loc_evil and loc_kind >= loc_cringe) or (loc_cringe > loc_kind and loc_cringe > loc_evil):
        main_loc = 'cringe'
    push_smth('main_loc', main_loc, id)